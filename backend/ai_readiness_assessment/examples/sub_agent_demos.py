#!/usr/bin/env python3
"""
Sub-Agent Demonstrations
Shows individual sub-agent capabilities and usage examples
"""

import json
from datetime import datetime
from ai_readiness_assessment.examples.sample_data import get_sample_business, get_sample_assessment_result
from ai_readiness_assessment.subagents.scoring_agent import calculate_section_score, determine_readiness_level
from ai_readiness_assessment.subagents.recommendation_agent import generate_personalized_recommendations, get_recommendation_templates
from ai_readiness_assessment.subagents.report_generator_agent import generate_comprehensive_report, create_visual_chart_data
from ai_readiness_assessment.subagents.kenya_context import get_kenya_regulations, get_kenya_business_context
from ai_readiness_assessment.subagents.assessment_guide import get_question_explanation, get_section_guidance


def demonstrate_scoring_agent():
    """Demonstrate the Scoring Agent capabilities"""
    print("🧮 SCORING AGENT DEMONSTRATION")
    print("=" * 50)
    print()
    
    # Get sample data
    sample_business = get_sample_business("manufacturing_medium")
    sample_responses = sample_business["responses"]["data_infrastructure"]
    
    print("📊 Sample Section Responses:")
    print(f"   Section: Data Infrastructure & Quality")
    for question_id, score in sample_responses.items():
        print(f"   {question_id}: {score}/5")
    print()
    
    # Demonstrate section score calculation
    print("🔢 Calculating Section Score...")
    
    try:
        score_result = calculate_section_score.invoke({
            "section_id": "data_infrastructure",
            "responses": json.dumps(sample_responses)
        })
        
        score_data = json.loads(score_result)
        
        if score_data.get("success", True):
            print("✅ Section score calculated successfully!")
            section_total = sum(sample_responses.values())
            max_possible = len(sample_responses) * 5
            percentage = (section_total / max_possible) * 100
            
            print(f"   📈 Section Total: {section_total}/{max_possible}")
            print(f"   📊 Percentage: {percentage:.1f}%")
            print(f"   🎯 Performance Level: {'Strong' if percentage >= 80 else 'Good' if percentage >= 60 else 'Needs Improvement'}")
        else:
            print(f"❌ Score calculation failed: {score_data.get('error')}")
    except Exception as e:
        print(f"❌ Error in score calculation: {str(e)}")
    
    print()
    
    # Demonstrate readiness level determination
    print("🎯 Determining Overall Readiness Level...")
    
    total_score = sample_business["total_score"]
    section_scores = {}
    
    for section_id, responses in sample_business["responses"].items():
        section_total = sum(responses.values())
        section_scores[section_id] = {
            "section_total": section_total,
            "max_possible": len(responses) * 5
        }
    
    try:
        readiness_result = determine_readiness_level.invoke({
            "total_score": total_score,
            "section_scores": json.dumps(section_scores)
        })
        
        readiness_data = json.loads(readiness_result)
        
        if readiness_data.get("readiness_level"):
            readiness_level = readiness_data["readiness_level"]
            print("✅ Readiness level determined successfully!")
            print(f"   🏆 Total Score: {total_score}/150")
            print(f"   📈 Overall Percentage: {(total_score/150)*100:.1f}%")
            print(f"   🎯 Readiness Level: {readiness_level}")
            
            # Show readiness level explanation
            level_descriptions = {
                "Not Ready": "Needs foundational work before AI initiatives",
                "Foundation Building": "Building necessary foundations for AI adoption",
                "Ready for Pilots": "Ready to begin AI pilot projects",
                "AI Ready": "Can successfully implement and scale AI solutions",
                "AI Advanced": "AI leader with advanced capabilities"
            }
            
            description = level_descriptions.get(readiness_level, "Unknown level")
            print(f"   💡 Meaning: {description}")
        else:
            print(f"❌ Readiness determination failed: {readiness_data.get('error')}")
    except Exception as e:
        print(f"❌ Error in readiness determination: {str(e)}")
    
    print("\n" + "=" * 50 + "\n")


def demonstrate_recommendation_agent():
    """Demonstrate the Recommendation Agent capabilities"""
    print("💡 RECOMMENDATION AGENT DEMONSTRATION")
    print("=" * 50)
    print()
    
    # Get sample assessment result
    sample_result = get_sample_assessment_result("Ready for Pilots")
    sample_business = get_sample_business("manufacturing_medium")
    
    print("📋 Sample Assessment Summary:")
    print(f"   Business: {sample_result['business_name']}")
    print(f"   Industry: {sample_result['industry']}")
    print(f"   Total Score: {sample_result['total_score']}/150")
    print(f"   Readiness Level: {sample_result['readiness_level']}")
    print()
    
    # Demonstrate personalized recommendations
    print("🎯 Generating Personalized Recommendations...")
    
    try:
        recommendations_result = generate_personalized_recommendations.invoke({
            "assessment_results": json.dumps(sample_result),
            "business_info": json.dumps(sample_business["business_info"])
        })
        
        recommendations_data = json.loads(recommendations_result)
        
        if recommendations_data.get("success", True):
            recommendations = recommendations_data.get("recommendations", {})
            
            print("✅ Personalized recommendations generated!")
            
            # Priority actions
            priority_actions = recommendations.get("priority_actions", [])
            if priority_actions:
                print("   🔥 Priority Actions:")
                for i, action in enumerate(priority_actions[:5], 1):
                    print(f"      {i}. {action}")
            
            # Timeline
            timeline = recommendations.get("timeline", "Not specified")
            print(f"   ⏱️  Implementation Timeline: {timeline}")
            
            # Resource requirements
            resources = recommendations.get("resource_requirements", {})
            if resources:
                print("   💰 Resource Requirements:")
                if resources.get("budget_range"):
                    print(f"      • Budget: {resources['budget_range']}")
                if resources.get("staff_time"):
                    print(f"      • Staff Time: {resources['staff_time']}")
            
            # Kenya-specific notes
            kenya_notes = recommendations.get("kenya_specific_notes", [])
            if kenya_notes:
                print("   🇰🇪 Kenya-Specific Considerations:")
                for note in kenya_notes[:3]:
                    print(f"      • {note}")
        else:
            print(f"❌ Recommendations generation failed: {recommendations_data.get('error')}")
    except Exception as e:
        print(f"❌ Error in recommendations generation: {str(e)}")
    
    print()
    
    # Demonstrate recommendation templates
    print("📋 Getting Recommendation Templates...")
    
    try:
        template_result = get_recommendation_templates.invoke({
            "readiness_level": sample_result["readiness_level"]
        })
        
        template_data = json.loads(template_result)
        
        if "priority_focus" in template_data:
            print("✅ Recommendation template retrieved!")
            print(f"   🎯 Priority Focus: {template_data['priority_focus']}")
            print(f"   💬 Key Message: {template_data['key_message']}")
            
            action_categories = template_data.get("action_categories", {})
            if action_categories:
                print("   📅 Action Categories:")
                for category, actions in action_categories.items():
                    print(f"      • {category.title()}: {len(actions)} actions")
        else:
            print(f"❌ Template retrieval failed")
    except Exception as e:
        print(f"❌ Error in template retrieval: {str(e)}")
    
    print("\n" + "=" * 50 + "\n")


def demonstrate_report_generator():
    """Demonstrate the Report Generator capabilities"""
    print("📋 REPORT GENERATOR DEMONSTRATION")
    print("=" * 50)
    print()
    
    # Get sample data
    sample_result = get_sample_assessment_result("Ready for Pilots")
    sample_business = get_sample_business("manufacturing_medium")
    
    # Create sample recommendations
    sample_recommendations = {
        "success": True,
        "recommendations": {
            "readiness_level": sample_result["readiness_level"],
            "priority_actions": [
                "Launch AI pilot projects in quality control",
                "Develop AI governance framework",
                "Expand technical team capabilities"
            ],
            "timeline": "6-9 months",
            "resource_requirements": {
                "budget_range": "KES 2M - 8M",
                "staff_time": "4-6 FTE for 6-9 months"
            },
            "kenya_specific_notes": [
                "Ensure compliance with Kenya's Data Protection Act",
                "Leverage local manufacturing expertise",
                "Consider regional market opportunities"
            ]
        }
    }
    
    print("📊 Sample Data for Report:")
    print(f"   Business: {sample_result['business_name']}")
    print(f"   Readiness Level: {sample_result['readiness_level']}")
    print(f"   Total Score: {sample_result['total_score']}/150")
    print()
    
    # Demonstrate comprehensive report generation
    print("📄 Generating Comprehensive Report...")
    
    try:
        report_result = generate_comprehensive_report.invoke({
            "assessment_results": json.dumps(sample_result),
            "recommendations": json.dumps(sample_recommendations),
            "business_info": json.dumps(sample_business["business_info"])
        })
        
        report_data = json.loads(report_result)
        
        if report_data.get("success", True):
            report = report_data.get("report", {})
            
            print("✅ Comprehensive report generated!")
            print("   📋 Report Sections:")
            
            section_count = 0
            if "report_metadata" in report:
                print("      • Report Metadata")
                section_count += 1
            if "executive_summary" in report:
                print("      • Executive Summary")
                section_count += 1
            if "section_analysis" in report:
                print("      • Section Analysis")
                section_count += 1
            if "implementation_roadmap" in report:
                print("      • Implementation Roadmap")
                section_count += 1
            if "resource_requirements" in report:
                print("      • Resource Requirements")
                section_count += 1
            if "kenya_specific_guidance" in report:
                print("      • Kenya-Specific Guidance")
                section_count += 1
            if "visual_representations" in report:
                print("      • Visual Representations")
                section_count += 1
            
            print(f"   📊 Total Sections: {section_count}")
            
            # Show executive summary details
            if "executive_summary" in report:
                summary = report["executive_summary"]
                print("   🎯 Executive Summary Highlights:")
                print(f"      • Overall Readiness: {summary.get('overall_readiness', 'N/A')}")
                print(f"      • Total Score: {summary.get('total_score', 'N/A')}")
                print(f"      • Investment Level: {summary.get('investment_level', 'N/A')}")
        else:
            print(f"❌ Report generation failed: {report_data.get('error')}")
    except Exception as e:
        print(f"❌ Error in report generation: {str(e)}")
    
    print()
    
    # Demonstrate visual chart data creation
    print("📊 Creating Visual Chart Data...")
    
    chart_types = ["radar", "bar", "gauge"]
    
    for chart_type in chart_types:
        try:
            chart_result = create_visual_chart_data.invoke({
                "assessment_results": json.dumps(sample_result),
                "chart_type": chart_type
            })
            
            chart_data = json.loads(chart_result)
            
            if chart_data.get("success", True):
                print(f"   ✅ {chart_type.capitalize()} chart data created")
                data = chart_data.get("data", {})
                if chart_type == "radar" and "labels" in data:
                    print(f"      • Data points: {len(data['labels'])}")
                elif chart_type == "bar" and "categories" in data:
                    print(f"      • Categories: {len(data['categories'])}")
                elif chart_type == "gauge" and "percentage" in data:
                    print(f"      • Gauge value: {data['percentage']:.1f}%")
            else:
                print(f"   ❌ {chart_type.capitalize()} chart creation failed")
        except Exception as e:
            print(f"   ❌ Error creating {chart_type} chart: {str(e)}")
    
    print("\n" + "=" * 50 + "\n")


def demonstrate_kenya_context_agent():
    """Demonstrate the Kenya Context Agent capabilities"""
    print("🇰🇪 KENYA CONTEXT AGENT DEMONSTRATION")
    print("=" * 50)
    print()
    
    # Demonstrate Kenya regulations
    print("📜 Getting Kenya Regulations Information...")
    
    try:
        regulations_result = get_kenya_regulations.invoke({
            "regulation_type": "data_protection"
        })
        
        regulations_data = json.loads(regulations_result)
        
        if regulations_data.get("success", True):
            print("✅ Kenya regulations information retrieved!")
            
            if "regulations" in regulations_data:
                regulations = regulations_data["regulations"]
                print("   📋 Key Regulations:")
                for reg in regulations.get("key_acts", [])[:3]:
                    print(f"      • {reg}")
                
                if "compliance_requirements" in regulations:
                    print("   ✅ Compliance Requirements:")
                    for req in regulations["compliance_requirements"][:3]:
                        print(f"      • {req}")
        else:
            print(f"❌ Regulations retrieval failed: {regulations_data.get('error')}")
    except Exception as e:
        print(f"❌ Error retrieving regulations: {str(e)}")
    
    print()
    
    # Demonstrate Kenya business context
    print("🏢 Getting Kenya Business Context...")
    
    try:
        context_result = get_kenya_business_context.invoke({
            "industry": "Manufacturing",
            "context_type": "overview"
        })
        
        context_data = json.loads(context_result)
        
        if context_data.get("success", True):
            print("✅ Kenya business context retrieved!")
            
            if "context" in context_data:
                context = context_data["context"]
                print("   🏭 Industry Context:")
                
                if "market_overview" in context:
                    print(f"      • Market Overview: Available")
                if "key_challenges" in context:
                    challenges = context["key_challenges"]
                    print(f"      • Key Challenges: {len(challenges)} identified")
                if "opportunities" in context:
                    opportunities = context["opportunities"]
                    print(f"      • Opportunities: {len(opportunities)} identified")
                if "local_examples" in context:
                    examples = context["local_examples"]
                    print(f"      • Local Examples: {len(examples)} provided")
        else:
            print(f"❌ Business context retrieval failed: {context_data.get('error')}")
    except Exception as e:
        print(f"❌ Error retrieving business context: {str(e)}")
    
    print("\n" + "=" * 50 + "\n")


def demonstrate_assessment_guide():
    """Demonstrate the Assessment Guide capabilities"""
    print("📚 ASSESSMENT GUIDE DEMONSTRATION")
    print("=" * 50)
    print()
    
    # Demonstrate question explanation
    print("❓ Getting Question Explanation...")
    
    try:
        explanation_result = get_question_explanation.invoke({
            "question_id": "data_collection_processes"
        })
        
        explanation_data = json.loads(explanation_result)
        
        if explanation_data.get("success", True):
            print("✅ Question explanation retrieved!")
            
            if "explanation" in explanation_data:
                print("   📖 Explanation provided")
            if "examples" in explanation_data:
                print("   💡 Examples included")
            if "scoring_guidance" in explanation_data:
                print("   🎯 Scoring guidance available")
        else:
            print(f"❌ Question explanation failed: {explanation_data.get('error')}")
    except Exception as e:
        print(f"❌ Error getting question explanation: {str(e)}")
    
    print()
    
    # Demonstrate section guidance
    print("📋 Getting Section Guidance...")
    
    try:
        guidance_result = get_section_guidance.invoke({
            "section_id": "data_infrastructure"
        })
        
        guidance_data = json.loads(guidance_result)
        
        if guidance_data.get("success", True):
            print("✅ Section guidance retrieved!")
            
            if "section_overview" in guidance_data:
                print("   📊 Section overview provided")
            if "key_concepts" in guidance_data:
                print("   🔑 Key concepts explained")
            if "assessment_tips" in guidance_data:
                print("   💡 Assessment tips included")
        else:
            print(f"❌ Section guidance failed: {guidance_data.get('error')}")
    except Exception as e:
        print(f"❌ Error getting section guidance: {str(e)}")
    
    print("\n" + "=" * 50 + "\n")


def run_all_sub_agent_demos():
    """Run all sub-agent demonstrations"""
    print("🤖 AI READINESS ASSESSMENT - SUB-AGENT DEMONSTRATIONS")
    print("=" * 70)
    print()
    print("This demonstration shows the capabilities of each sub-agent")
    print("in the AI Readiness Assessment system.")
    print()
    
    # Run all demonstrations
    demonstrate_scoring_agent()
    demonstrate_recommendation_agent()
    demonstrate_report_generator()
    demonstrate_kenya_context_agent()
    demonstrate_assessment_guide()
    
    print("🎉 ALL SUB-AGENT DEMONSTRATIONS COMPLETED!")
    print("=" * 70)
    print()
    print("📋 SUMMARY OF SUB-AGENTS:")
    print("   🧮 Scoring Agent: Calculates scores and determines readiness levels")
    print("   💡 Recommendation Agent: Generates personalized recommendations")
    print("   📋 Report Generator: Creates comprehensive assessment reports")
    print("   🇰🇪 Kenya Context Agent: Provides local business context and regulations")
    print("   📚 Assessment Guide: Offers question explanations and guidance")
    print()
    print("Each sub-agent can be used independently or as part of the")
    print("complete assessment workflow orchestrated by the main agent.")
    print()
    print("For more information, visit: www.aireadiness.ke")
    print("=" * 70)


if __name__ == "__main__":
    run_all_sub_agent_demos()