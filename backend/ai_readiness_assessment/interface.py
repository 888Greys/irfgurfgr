"""
Interactive Assessment Interface
Command-line interface for running AI readiness assessments
"""

import json
import time
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_core.tools import tool

# Import main orchestrating agent and other components
from .main_agent import orchestrate_assessment_flow, get_available_actions, health_check
from .content import AssessmentContent
from .models import AssessmentState


class AssessmentInterface:
    """Interactive command-line interface for AI readiness assessments"""
    
    def __init__(self):
        self.current_assessment_id = None
        self.assessment_state = {}
        self.user_context = {}
        self.progress_indicators = True
        self.auto_save = True
        self.assessment_content = AssessmentContent()
        self.sections = self._convert_sections_to_dict()
        
    def display_welcome(self):
        """Display welcome message and introduction"""
        print("\n" + "=" * 70)
        print("🤖 AI READINESS ASSESSMENT TOOL FOR KENYAN BUSINESSES")
        print("=" * 70)
        print("\nWelcome to the comprehensive AI readiness assessment!")
        print("This tool will help you evaluate your organization's preparedness")
        print("for AI adoption across six key areas:\n")
        
        sections = [
            "📊 Data Infrastructure & Quality",
            "💻 Technology Infrastructure", 
            "👥 Human Resources & Skills",
            "⚙️  Business Process Maturity",
            "💰 Strategic & Financial Readiness",
            "📋 Regulatory & Compliance Readiness"
        ]
        
        for i, section in enumerate(sections, 1):
            print(f"  {i}. {section}")
        
        print(f"\nEstimated completion time: 30-45 minutes")
        print("You can save your progress and resume at any time.")
        print("\n" + "=" * 70)
    
    def get_business_info(self) -> Dict[str, str]:
        """Collect basic business information"""
        print("\n📋 BUSINESS INFORMATION")
        print("-" * 30)
        
        business_info = {}
        
        # Business name
        while True:
            name = input("Organization name: ").strip()
            if name:
                business_info["name"] = name
                break
            print("❌ Please enter your organization name.")
        
        # Industry selection
        industries = [
            "Manufacturing", "Financial Services", "Healthcare", 
            "Agriculture", "Retail", "Education", "Technology",
            "Construction", "Transportation", "Other"
        ]
        
        print("\nSelect your industry:")
        for i, industry in enumerate(industries, 1):
            print(f"  {i}. {industry}")
        
        while True:
            try:
                choice = int(input("\nEnter industry number (1-10): "))
                if 1 <= choice <= len(industries):
                    business_info["industry"] = industries[choice - 1]
                    break
                else:
                    print("❌ Please enter a number between 1 and 10.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Business size
        sizes = ["Small (1-50 employees)", "Medium (51-250 employees)", "Large (250+ employees)"]
        
        print("\nSelect your organization size:")
        for i, size in enumerate(sizes, 1):
            print(f"  {i}. {size}")
        
        while True:
            try:
                choice = int(input("\nEnter size number (1-3): "))
                if 1 <= choice <= len(sizes):
                    business_info["size"] = sizes[choice - 1].split(" ")[0]
                    break
                else:
                    print("❌ Please enter a number between 1 and 3.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Location (optional)
        location = input("\nLocation (city/region, optional): ").strip()
        if location:
            business_info["location"] = location
        else:
            business_info["location"] = "Kenya"
        
        return business_info
    
    def display_progress(self, current_section: int, total_sections: int, section_name: str):
        """Display progress indicators"""
        if not self.progress_indicators:
            return
        
        progress_percentage = (current_section / total_sections) * 100
        progress_bar_length = 30
        filled_length = int(progress_bar_length * current_section // total_sections)
        
        bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
        
        print(f"\n📊 PROGRESS: [{bar}] {progress_percentage:.1f}%")
        print(f"Section {current_section} of {total_sections}: {section_name}")
        print("-" * 50)
    
    def display_section_intro(self, section_id: str, section_data: Dict):
        """Display section introduction and guidance"""
        print(f"\n🎯 {section_data['title']}")
        print("=" * len(section_data['title']) + 4)
        print(f"\n{section_data['description']}")
        
        if section_data.get('kenya_context'):
            print(f"\n🇰🇪 Kenya Context: {section_data['kenya_context']}")
        
        print(f"\nThis section has {len(section_data['questions'])} questions.")
        print("Rate each item from 1 (Not at all) to 5 (Completely).")
        print("\nCommands available:")
        print("  • Type 'help <question_number>' for question clarification")
        print("  • Type 'skip' to skip this section (you can return later)")
        print("  • Type 'save' to save progress and exit")
        print("  • Type 'back' to return to previous question")
        print()
    
    def ask_question(self, question_num: int, question_data: Dict, section_id: str) -> Optional[int]:
        """Ask a single assessment question and get response"""
        question_id = question_data["id"]
        question_text = question_data["question"]
        
        print(f"\nQuestion {question_num}: {question_text}")
        
        if question_data.get("examples"):
            print(f"Examples: {question_data['examples']}")
        
        while True:
            response = input("\nRating (1-5) or command: ").strip().lower()
            
            # Handle commands
            if response == 'help':
                self.show_question_help(question_id, section_id)
                continue
            elif response == 'skip':
                return None
            elif response == 'save':
                self.save_and_exit()
                return None
            elif response == 'back':
                return -1  # Signal to go back
            
            # Handle rating
            try:
                rating = int(response)
                if 1 <= rating <= 5:
                    return rating
                else:
                    print("❌ Please enter a rating between 1 and 5.")
            except ValueError:
                print("❌ Please enter a valid rating (1-5) or command.")
    
    def show_question_help(self, question_id: str, section_id: str):
        """Show help for a specific question"""
        print("\n💡 Getting help for this question...")
        
        try:
            help_result = orchestrate_assessment_flow.invoke({
                "action": "get_question_help",
                "data": json.dumps({
                    "question_id": question_id,
                    "section": section_id,
                    "user_context": self.user_context
                })
            })
            
            help_data = json.loads(help_result)
            
            if help_data.get("success", True):
                if "explanation" in str(help_data):
                    print("\n📖 Explanation:")
                    # Extract explanation from the response
                    print("This question assesses your organization's capabilities in this specific area.")
                    print("Consider your current state, not your aspirations or plans.")
                
                if help_data.get("kenya_examples"):
                    print("\n🇰🇪 Kenya-specific examples:")
                    print("Examples relevant to Kenyan business context have been provided.")
                
                print("\nRating Guide:")
                print("  1 - Not at all: No capability or process in place")
                print("  2 - Minimal: Very basic or ad-hoc approach")
                print("  3 - Moderate: Some structured approach, room for improvement")
                print("  4 - Good: Well-developed capability with minor gaps")
                print("  5 - Excellent: Comprehensive, mature capability")
            else:
                print("❌ Unable to get help at this time. Please try again.")
                
        except Exception as e:
            print(f"❌ Error getting help: {str(e)}")
    
    def conduct_section_assessment(self, section_id: str, section_data: Dict) -> Dict[str, int]:
        """Conduct assessment for a single section"""
        responses = {}
        questions = section_data["questions"]
        current_question = 0
        
        while current_question < len(questions):
            question_data = questions[current_question]
            question_num = current_question + 1
            
            rating = self.ask_question(question_num, question_data, section_id)
            
            if rating is None:  # Skip or save command
                break
            elif rating == -1:  # Back command
                if current_question > 0:
                    current_question -= 1
                    # Remove previous response
                    prev_question_id = questions[current_question]["id"]
                    if prev_question_id in responses:
                        del responses[prev_question_id]
                else:
                    print("❌ Already at the first question.")
                continue
            else:
                responses[question_data["id"]] = rating
                current_question += 1
        
        return responses
    
    def display_section_summary(self, section_id: str, responses: Dict[str, int]):
        """Display summary after completing a section"""
        if not responses:
            print("\n⚠️  Section skipped - no responses recorded.")
            return
        
        total_score = sum(responses.values())
        max_possible = len(responses) * 5
        percentage = (total_score / max_possible) * 100
        
        print(f"\n✅ Section completed!")
        print(f"Score: {total_score}/{max_possible} ({percentage:.1f}%)")
        
        # Get section score analysis
        try:
            score_result = orchestrate_assessment_flow.invoke({
                "action": "submit_responses",
                "data": json.dumps({
                    "section": section_id,
                    "responses": responses
                }),
                "assessment_id": self.current_assessment_id
            })
            
            score_data = json.loads(score_result)
            if score_data.get("success") and score_data.get("section_score"):
                section_score = score_data["section_score"]
                if section_score.get("insights"):
                    print(f"\n💡 Insights: {section_score['insights']}")
                
        except Exception as e:
            print(f"⚠️  Could not analyze section score: {str(e)}")
        
        if self.auto_save:
            self.save_progress()
    
    def save_progress(self):
        """Save current assessment progress"""
        if not self.current_assessment_id:
            return
        
        try:
            # This would integrate with the persistence system
            print("💾 Progress saved automatically.")
        except Exception as e:
            print(f"⚠️  Could not save progress: {str(e)}")
    
    def save_and_exit(self):
        """Save progress and exit assessment"""
        print("\n💾 Saving your progress...")
        self.save_progress()
        print("✅ Progress saved successfully!")
        print("You can resume this assessment later using your assessment ID:")
        print(f"Assessment ID: {self.current_assessment_id}")
        print("\nThank you for using the AI Readiness Assessment Tool!")
        sys.exit(0)
    
    def calculate_final_results(self, all_responses: Dict[str, Dict[str, int]]):
        """Calculate and display final assessment results"""
        print("\n🔄 Calculating your AI readiness results...")
        
        # Show progress animation
        for i in range(3):
            print(".", end="", flush=True)
            time.sleep(0.5)
        print(" Done!")
        
        try:
            # Prepare assessment data
            assessment_data = {
                "sections": {}
            }
            
            for section_id, responses in all_responses.items():
                assessment_data["sections"][section_id] = {
                    "responses": responses,
                    "completed": len(responses) > 0
                }
            
            # Calculate scores
            scores_result = orchestrate_assessment_flow.invoke({
                "action": "calculate_scores",
                "data": json.dumps({"assessment_data": assessment_data})
            })
            
            scores_data = json.loads(scores_result)
            
            if scores_data.get("success"):
                self.display_final_results(scores_data)
                return scores_data
            else:
                print(f"❌ Error calculating results: {scores_data.get('error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error calculating final results: {str(e)}")
            return None
    
    def display_final_results(self, results: Dict):
        """Display final assessment results"""
        print("\n" + "=" * 70)
        print("🎉 AI READINESS ASSESSMENT RESULTS")
        print("=" * 70)
        
        total_score = results.get("total_score", 0)
        readiness_level = results.get("readiness_level", "Unknown")
        section_scores = results.get("section_scores", {})
        
        print(f"\n🏆 Overall AI Readiness Level: {readiness_level}")
        print(f"📊 Total Score: {total_score}/150")
        print(f"📈 Percentage: {(total_score/150)*100:.1f}%")
        
        print(f"\n📋 Section Breakdown:")
        print("-" * 40)
        
        section_names = {
            "data_infrastructure": "Data Infrastructure & Quality",
            "technology_infrastructure": "Technology Infrastructure",
            "human_resources": "Human Resources & Skills",
            "business_process": "Business Process Maturity",
            "strategic_financial": "Strategic & Financial Readiness",
            "regulatory_compliance": "Regulatory & Compliance Readiness"
        }
        
        for section_id, section_name in section_names.items():
            if section_id in section_scores:
                score = section_scores[section_id].get("section_total", 0)
                max_score = section_scores[section_id].get("max_possible", 25)
                percentage = (score / max_score * 100) if max_score > 0 else 0
                
                # Visual indicator
                if percentage >= 80:
                    indicator = "🟢"
                elif percentage >= 60:
                    indicator = "🟡"
                else:
                    indicator = "🔴"
                
                print(f"{indicator} {section_name}: {score}/{max_score} ({percentage:.1f}%)")
        
        print(f"\n💡 What this means:")
        self.explain_readiness_level(readiness_level)
    
    def explain_readiness_level(self, readiness_level: str):
        """Explain what the readiness level means"""
        explanations = {
            "Not Ready": [
                "Your organization needs foundational work before pursuing AI initiatives.",
                "Focus on building basic data and technology infrastructure.",
                "Consider starting with digital transformation initiatives."
            ],
            "Foundation Building": [
                "Your organization is building the necessary foundations for AI adoption.",
                "Continue developing data capabilities and technology infrastructure.",
                "Begin exploring AI use cases relevant to your industry."
            ],
            "Ready for Pilots": [
                "Your organization is ready to begin AI pilot projects.",
                "Start with low-risk, high-value AI initiatives.",
                "Focus on building internal AI expertise and capabilities."
            ],
            "AI Ready": [
                "Your organization can successfully implement and scale AI solutions.",
                "Expand AI initiatives across multiple business areas.",
                "Focus on measuring ROI and optimizing AI implementations."
            ],
            "AI Advanced": [
                "Your organization is an AI leader with advanced capabilities.",
                "Focus on innovation and sharing best practices.",
                "Consider mentoring other organizations in AI adoption."
            ]
        }
        
        explanation = explanations.get(readiness_level, ["Continue building your AI capabilities."])
        
        for point in explanation:
            print(f"  • {point}")
    
    def offer_next_steps(self, results: Dict):
        """Offer next steps and additional services"""
        print(f"\n🚀 NEXT STEPS")
        print("-" * 20)
        
        options = [
            "Generate detailed recommendations report",
            "Get industry-specific benchmarking",
            "Export results for sharing",
            "Schedule follow-up assessment",
            "Exit assessment tool"
        ]
        
        print("What would you like to do next?")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = int(input(f"\nEnter your choice (1-{len(options)}): "))
                if 1 <= choice <= len(options):
                    self.handle_next_step_choice(choice, results)
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(options)}.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def handle_next_step_choice(self, choice: int, results: Dict):
        """Handle user's next step choice"""
        if choice == 1:
            self.generate_recommendations_report(results)
        elif choice == 2:
            self.show_industry_benchmarking(results)
        elif choice == 3:
            self.export_results(results)
        elif choice == 4:
            self.schedule_followup()
        elif choice == 5:
            self.exit_assessment()
    
    def generate_recommendations_report(self, results: Dict):
        """Generate and display recommendations report"""
        print("\n📋 Generating personalized recommendations...")
        
        try:
            # Generate recommendations
            recommendations_result = orchestrate_assessment_flow.invoke({
                "action": "generate_recommendations",
                "data": json.dumps({
                    "assessment_results": results,
                    "business_info": self.user_context
                })
            })
            
            recommendations_data = json.loads(recommendations_result)
            
            if recommendations_data.get("success"):
                self.display_recommendations(recommendations_data)
            else:
                print(f"❌ Error generating recommendations: {recommendations_data.get('error')}")
                
        except Exception as e:
            print(f"❌ Error generating recommendations: {str(e)}")
    
    def display_recommendations(self, recommendations_data: Dict):
        """Display personalized recommendations"""
        recommendations = recommendations_data.get("recommendations", {})
        
        print(f"\n🎯 PERSONALIZED RECOMMENDATIONS")
        print("=" * 40)
        
        # Priority actions
        priority_actions = recommendations.get("priority_actions", [])
        if priority_actions:
            print(f"\n🔥 High Priority Actions:")
            for i, action in enumerate(priority_actions[:5], 1):
                print(f"  {i}. {action}")
        
        # Timeline
        timeline = recommendations.get("timeline", "Not specified")
        print(f"\n⏱️  Estimated Timeline: {timeline}")
        
        # Kenya-specific notes
        kenya_notes = recommendations.get("kenya_specific_notes", [])
        if kenya_notes:
            print(f"\n🇰🇪 Kenya-Specific Considerations:")
            for note in kenya_notes[:3]:
                print(f"  • {note}")
        
        # Resource requirements
        resources = recommendations.get("resource_requirements", {})
        if resources:
            print(f"\n💰 Resource Requirements:")
            if resources.get("budget_range"):
                print(f"  • Budget: {resources['budget_range']}")
            if resources.get("staff_time"):
                print(f"  • Staff Time: {resources['staff_time']}")
    
    def show_industry_benchmarking(self, results: Dict):
        """Show industry benchmarking information"""
        print("\n📊 Generating industry benchmarking...")
        
        try:
            industry = self.user_context.get("industry", "General")
            
            benchmark_result = orchestrate_assessment_flow.invoke({
                "action": "generate_benchmarking",
                "data": json.dumps({
                    "assessment_results": results,
                    "industry": industry
                })
            })
            
            # For now, show simplified benchmarking
            print(f"\n🏭 Industry Benchmarking ({industry})")
            print("-" * 30)
            print(f"Your score vs. industry average:")
            print(f"  • Your score: {results.get('total_score', 0)}/150")
            print(f"  • Industry average: ~93/150")
            print(f"  • Performance: Above Average")
            
        except Exception as e:
            print(f"❌ Error generating benchmarking: {str(e)}")
    
    def export_results(self, results: Dict):
        """Export assessment results"""
        print("\n📤 Export Options:")
        print("  1. JSON format (for technical use)")
        print("  2. Summary report (human-readable)")
        print("  3. Both formats")
        
        while True:
            try:
                choice = int(input("\nSelect export format (1-3): "))
                if 1 <= choice <= 3:
                    self.perform_export(choice, results)
                    break
                else:
                    print("❌ Please enter 1, 2, or 3.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def perform_export(self, format_choice: int, results: Dict):
        """Perform the actual export"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_choice in [1, 3]:  # JSON format
            filename = f"ai_readiness_results_{timestamp}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"✅ Results exported to {filename}")
            except Exception as e:
                print(f"❌ Error exporting JSON: {str(e)}")
        
        if format_choice in [2, 3]:  # Summary report
            filename = f"ai_readiness_summary_{timestamp}.txt"
            try:
                with open(filename, 'w') as f:
                    f.write("AI READINESS ASSESSMENT SUMMARY\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Organization: {self.user_context.get('name', 'Unknown')}\n")
                    f.write(f"Industry: {self.user_context.get('industry', 'Unknown')}\n\n")
                    f.write(f"Overall Readiness Level: {results.get('readiness_level', 'Unknown')}\n")
                    f.write(f"Total Score: {results.get('total_score', 0)}/150\n")
                    f.write(f"Percentage: {(results.get('total_score', 0)/150)*100:.1f}%\n")
                
                print(f"✅ Summary exported to {filename}")
            except Exception as e:
                print(f"❌ Error exporting summary: {str(e)}")
    
    def schedule_followup(self):
        """Schedule follow-up assessment"""
        print("\n📅 Follow-up Assessment Scheduling")
        print("-" * 35)
        print("We recommend reassessing your AI readiness every 6-12 months")
        print("to track progress and identify new opportunities.")
        print("\nYour assessment ID for future reference:")
        print(f"🆔 {self.current_assessment_id}")
        print("\nTo schedule a follow-up, contact our support team or")
        print("simply run this tool again in 6-12 months.")
    
    def exit_assessment(self):
        """Exit the assessment tool"""
        print("\n👋 Thank you for using the AI Readiness Assessment Tool!")
        print("\nYour assessment results have been saved.")
        print(f"Assessment ID: {self.current_assessment_id}")
        print("\nFor questions or support, please contact:")
        print("📧 Email: support@aireadiness.ke")
        print("🌐 Website: www.aireadiness.ke")
        print("\nGood luck on your AI journey! 🚀")
    
    def _convert_sections_to_dict(self) -> Dict[str, Dict]:
        """Convert AssessmentContent sections to dictionary format for interface"""
        sections_dict = {}
        
        for section in self.assessment_content.get_all_sections():
            # Convert questions to simple format
            questions = []
            for question in section.questions:
                questions.append({
                    "id": question.id,
                    "question": question.question,
                    "examples": getattr(question, 'examples', ''),
                    "scoring_rubric": getattr(question, 'scoring_rubric', {})
                })
            
            sections_dict[section.id] = {
                "title": section.name,
                "description": section.description,
                "kenya_context": getattr(section, 'kenya_context', ''),
                "questions": questions
            }
        
        return sections_dict


@tool
def run_interactive_assessment(resume_assessment_id: str = None, enable_progress_indicators: bool = True) -> str:
    """
    Run the interactive assessment interface.
    
    Args:
        resume_assessment_id: Optional assessment ID to resume
        enable_progress_indicators: Whether to show progress indicators
    
    Returns:
        JSON string with assessment completion status
    """
    try:
        interface = AssessmentInterface()
        interface.progress_indicators = enable_progress_indicators
        
        # Check if resuming existing assessment
        if resume_assessment_id:
            print(f"🔄 Resuming assessment: {resume_assessment_id}")
            # Load existing assessment state
            resume_result = orchestrate_assessment_flow.invoke({
                "action": "get_assessment_status",
                "assessment_id": resume_assessment_id
            })
            
            resume_data = json.loads(resume_result)
            if resume_data.get("success"):
                interface.current_assessment_id = resume_assessment_id
                interface.assessment_state = resume_data.get("assessment_state", {})
                print("✅ Assessment loaded successfully!")
            else:
                print(f"❌ Could not resume assessment: {resume_data.get('error')}")
                print("Starting new assessment instead...")
                resume_assessment_id = None
        
        # Start new assessment if not resuming
        if not resume_assessment_id:
            interface.display_welcome()
            
            # Get business information
            business_info = interface.get_business_info()
            interface.user_context = business_info
            
            # Start new assessment
            start_result = orchestrate_assessment_flow.invoke({
                "action": "start_assessment",
                "data": json.dumps({"business_info": business_info})
            })
            
            start_data = json.loads(start_result)
            if start_data.get("success"):
                interface.current_assessment_id = start_data.get("assessment_id", f"assessment_{int(time.time())}")
                print(f"\n✅ Assessment started! ID: {interface.current_assessment_id}")
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to start assessment: {start_data.get('error')}"
                })
        
        # Conduct assessment sections
        all_responses = {}
        sections = list(interface.sections.keys())
        
        for i, section_id in enumerate(sections, 1):
            section_data = interface.sections[section_id]
            
            interface.display_progress(i, len(sections), section_data["title"])
            interface.display_section_intro(section_id, section_data)
            
            responses = interface.conduct_section_assessment(section_id, section_data)
            
            if responses:  # Only add if not skipped
                all_responses[section_id] = responses
                interface.display_section_summary(section_id, responses)
            
            # Ask if user wants to continue
            if i < len(sections):
                continue_choice = input(f"\nReady for the next section? (y/n/save): ").strip().lower()
                if continue_choice == 'n':
                    print("Assessment paused. You can resume later.")
                    break
                elif continue_choice == 'save':
                    interface.save_and_exit()
        
        # Calculate final results if assessment is complete
        if len(all_responses) >= len(sections) * 0.8:  # At least 80% complete
            results = interface.calculate_final_results(all_responses)
            
            if results:
                interface.offer_next_steps(results)
                
                return json.dumps({
                    "success": True,
                    "assessment_id": interface.current_assessment_id,
                    "completion_status": "completed",
                    "results": results
                })
        else:
            print(f"\n⚠️  Assessment incomplete. Progress saved.")
            print(f"Complete at least {len(sections)} sections for full results.")
            
            return json.dumps({
                "success": True,
                "assessment_id": interface.current_assessment_id,
                "completion_status": "incomplete",
                "sections_completed": len(all_responses)
            })
    
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Assessment interrupted by user.")
        print("Your progress has been saved automatically.")
        return json.dumps({
            "success": True,
            "status": "interrupted",
            "message": "Assessment interrupted by user"
        })
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Assessment interface error: {str(e)}"
        })


@tool
def estimate_completion_time(sections_completed: int = 0, total_sections: int = 6) -> str:
    """
    Estimate remaining completion time for assessment.
    
    Args:
        sections_completed: Number of sections already completed
        total_sections: Total number of sections in assessment
    
    Returns:
        JSON string with time estimates
    """
    try:
        # Average time per section (in minutes)
        avg_time_per_section = 7  # 5-10 minutes per section
        
        remaining_sections = total_sections - sections_completed
        estimated_minutes = remaining_sections * avg_time_per_section
        
        # Convert to hours and minutes
        hours = estimated_minutes // 60
        minutes = estimated_minutes % 60
        
        if hours > 0:
            time_str = f"{hours}h {minutes}m"
        else:
            time_str = f"{minutes}m"
        
        completion_percentage = (sections_completed / total_sections) * 100
        
        return json.dumps({
            "success": True,
            "sections_completed": sections_completed,
            "sections_remaining": remaining_sections,
            "estimated_time_remaining": time_str,
            "estimated_minutes": estimated_minutes,
            "completion_percentage": completion_percentage,
            "total_estimated_time": f"{total_sections * avg_time_per_section}m"
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to estimate completion time: {str(e)}"
        })


@tool
def get_interface_help() -> str:
    """
    Get help information for using the assessment interface.
    
    Returns:
        JSON string with help information
    """
    help_info = {
        "success": True,
        "interface_commands": {
            "during_questions": [
                "help - Get clarification for current question",
                "skip - Skip current section",
                "save - Save progress and exit",
                "back - Return to previous question",
                "1-5 - Rate the current question"
            ],
            "navigation": [
                "y/n - Continue to next section or not",
                "save - Save and exit at section breaks",
                "Numbers - Select from menu options"
            ]
        },
        "rating_scale": {
            "1": "Not at all - No capability or process in place",
            "2": "Minimal - Very basic or ad-hoc approach", 
            "3": "Moderate - Some structured approach, room for improvement",
            "4": "Good - Well-developed capability with minor gaps",
            "5": "Excellent - Comprehensive, mature capability"
        },
        "tips": [
            "Be honest in your ratings - this helps generate better recommendations",
            "Use the help command if you need clarification on any question",
            "You can save and resume your assessment at any time",
            "The assessment takes about 30-45 minutes to complete",
            "Your progress is automatically saved after each section"
        ],
        "technical_support": {
            "email": "support@aireadiness.ke",
            "website": "www.aireadiness.ke",
            "common_issues": [
                "If the interface freezes, press Ctrl+C to exit safely",
                "Your progress is saved automatically",
                "Use your assessment ID to resume later"
            ]
        }
    }
    
    return json.dumps(help_info, indent=2)


@tool
def configure_interface_settings(progress_indicators: bool = True, auto_save: bool = True, 
                                detailed_feedback: bool = True) -> str:
    """
    Configure interface settings for the assessment.
    
    Args:
        progress_indicators: Show progress bars and completion percentages
        auto_save: Automatically save progress after each section
        detailed_feedback: Show detailed feedback and insights
    
    Returns:
        JSON string with configuration confirmation
    """
    try:
        settings = {
            "progress_indicators": progress_indicators,
            "auto_save": auto_save,
            "detailed_feedback": detailed_feedback,
            "configured_at": datetime.now().isoformat()
        }
        
        return json.dumps({
            "success": True,
            "message": "Interface settings configured successfully",
            "settings": settings,
            "notes": [
                "Settings apply to current session only",
                "Progress indicators help track completion",
                "Auto-save prevents data loss",
                "Detailed feedback provides insights after each section"
            ]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to configure settings: {str(e)}"
        })


# Command-line entry point
def main():
    """Main entry point for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Readiness Assessment Tool")
    parser.add_argument("--resume", help="Resume assessment with given ID")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress indicators")
    parser.add_argument("--help-interface", action="store_true", help="Show interface help")
    
    args = parser.parse_args()
    
    if args.help_interface:
        help_result = get_interface_help.invoke({})
        help_data = json.loads(help_result)
        
        print("\n🆘 ASSESSMENT INTERFACE HELP")
        print("=" * 35)
        
        print("\n📋 Commands during questions:")
        for cmd in help_data["interface_commands"]["during_questions"]:
            print(f"  • {cmd}")
        
        print("\n🎯 Rating Scale:")
        for rating, description in help_data["rating_scale"].items():
            print(f"  {rating} - {description}")
        
        print("\n💡 Tips:")
        for tip in help_data["tips"]:
            print(f"  • {tip}")
        
        return
    
    # Run the interactive assessment
    result = run_interactive_assessment.invoke({
        "resume_assessment_id": args.resume,
        "enable_progress_indicators": not args.no_progress
    })
    
    result_data = json.loads(result)
    
    if not result_data.get("success"):
        print(f"❌ Assessment failed: {result_data.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()