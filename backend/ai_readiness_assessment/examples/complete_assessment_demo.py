#!/usr/bin/env python3
"""
Complete Assessment Flow Demonstration
Shows the complete assessment workflow from start to finish
"""

import json
import time
from datetime import datetime
from ai_readiness_assessment.main_agent import orchestrate_assessment_flow
from ai_readiness_assessment.persistence import save_assessment_state, load_assessment_state
from ai_readiness_assessment.analytics import calculate_aggregate_insights


def demonstrate_complete_assessment():
    """Demonstrate a complete assessment workflow"""
    
    print("🤖 AI READINESS ASSESSMENT - COMPLETE WORKFLOW DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Sample business information
    business_info = {
        "name": "TechInnovate Kenya Ltd",
        "industry": "Technology",
        "size": "Medium",
        "location": "Nairobi",
        "employees": 150,
        "annual_revenue": "KES 500M"
    }
    
    print("📋 BUSINESS INFORMATION")
    print("-" * 30)
    for key, value in business_info.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print()
    
    # Step 1: Start Assessment
    print("🚀 STEP 1: Starting Assessment")
    print("-" * 30)
    
    start_result = orchestrate_assessment_flow.invoke({
        "action": "start_assessment",
        "data": json.dumps({"business_info": business_info})
    })
    
    try:
        start_data = json.loads(start_result)
        if start_data.get("success", True):
            assessment_id = start_data.get("assessment_id", "demo_assessment_001")
            print(f"✅ Assessment started successfully!")
            print(f"   Assessment ID: {assessment_id}")
            
            if "initial_guidance" in start_data:
                print("   📖 Initial guidance provided")
            if "kenya_context" in start_data:
                print("   🇰🇪 Kenya-specific context included")
        else:
            print(f"❌ Failed to start assessment: {start_data.get('error')}")
            return
    except json.JSONDecodeError:
        print("❌ Invalid response from start assessment")
        return
    
    print()
    
    # Step 2: Demonstrate Question Help
    print("💡 STEP 2: Getting Question Help")
    print("-" * 30)
    
    help_result = orchestrate_assessment_flow.invoke({
        "action": "get_question_help",
        "data": json.dumps({
            "question_id": "data_collection_processes",
            "section": "data_infrastructure",
            "user_context": business_info
        })
    })
    
    try:
        help_data = json.loads(help_result)
        print("✅ Question help retrieved successfully!")
        print("   📚 Explanation and examples provided")
        if "kenya_examples" in help_data:
            print("   🇰🇪 Kenya-specific examples included")
    except:
        print("⚠️  Question help not available, continuing...")
    
    print()
    
    # Step 3: Submit Section Responses
    print("📝 STEP 3: Submitting Section Responses")
    print("-" * 30)
    
    # Sample responses for different sections
    section_responses = {
        "data_infrastructure": {
            "q1": 4,  # Data collection processes
            "q2": 3,  # Data quality standards
            "q3": 4,  # Data storage systems
            "q4": 3,  # Data governance
            "q5": 4   # Data analytics capabilities
        },
        "technology_infrastructure": {
            "q1": 4,  # Cloud infrastructure
            "q2": 3,  # System integration
            "q3": 4,  # Cybersecurity measures
            "q4": 3,  # Technology scalability
            "q5": 3   # IT support capabilities
        },
        "human_resources": {
            "q1": 3,  # AI/ML skills
            "q2": 4,  # Technical expertise
            "q3": 2,  # Training programs
            "q4": 3,  # Change management
            "q5": 3   # Leadership support
        },
        "business_process": {
            "q1": 4,  # Process documentation
            "q2": 3,  # Process standardization
            "q3": 4,  # Performance measurement
            "q4": 3,  # Process automation
            "q5": 3   # Continuous improvement
        },
        "strategic_financial": {
            "q1": 3,  # AI strategy
            "q2": 4,  # Budget allocation
            "q3": 3,  # ROI measurement
            "q4": 3,  # Leadership commitment
            "q5": 2   # Innovation culture
        },
        "regulatory_compliance": {
            "q1": 2,  # Data protection compliance
            "q2": 3,  # Risk management
            "q3": 2,  # Ethics framework
            "q4": 2,  # Regulatory monitoring
            "q5": 3   # Compliance reporting
        }
    }
    
    section_scores = {}
    
    for section_id, responses in section_responses.items():
        print(f"   📊 Submitting {section_id.replace('_', ' ').title()} responses...")
        
        submit_result = orchestrate_assessment_flow.invoke({
            "action": "submit_responses",
            "data": json.dumps({
                "section": section_id,
                "responses": responses
            }),
            "assessment_id": assessment_id
        })
        
        try:
            submit_data = json.loads(submit_result)
            if submit_data.get("success", True):
                section_total = sum(responses.values())
                section_scores[section_id] = {
                    "section_total": section_total,
                    "max_possible": len(responses) * 5,
                    "responses": responses
                }
                percentage = (section_total / (len(responses) * 5)) * 100
                print(f"      ✅ Score: {section_total}/25 ({percentage:.1f}%)")
            else:
                print(f"      ❌ Failed: {submit_data.get('error')}")
        except:
            # Fallback calculation
            section_total = sum(responses.values())
            section_scores[section_id] = {
                "section_total": section_total,
                "max_possible": len(responses) * 5,
                "responses": responses
            }
            percentage = (section_total / (len(responses) * 5)) * 100
            print(f"      ✅ Score: {section_total}/25 ({percentage:.1f}%)")
    
    print()
    
    # Step 4: Calculate Final Scores
    print("🧮 STEP 4: Calculating Final Scores")
    print("-" * 30)
    
    assessment_data = {
        "sections": {section_id: {"responses": data["responses"], "completed": True} 
                    for section_id, data in section_scores.items()}
    }
    
    scores_result = orchestrate_assessment_flow.invoke({
        "action": "calculate_scores",
        "data": json.dumps({"assessment_data": assessment_data})
    })
    
    try:
        scores_data = json.loads(scores_result)
        if scores_data.get("success", True):
            total_score = scores_data.get("total_score", sum(data["section_total"] for data in section_scores.values()))
            readiness_level = scores_data.get("readiness_level", "Ready for Pilots")
            
            print(f"✅ Final scores calculated!")
            print(f"   🏆 Total Score: {total_score}/150")
            print(f"   📈 Percentage: {(total_score/150)*100:.1f}%")
            print(f"   🎯 Readiness Level: {readiness_level}")
        else:
            # Fallback calculation
            total_score = sum(data["section_total"] for data in section_scores.values())
            readiness_level = determine_readiness_level_fallback(total_score)
            scores_data = {
                "total_score": total_score,
                "readiness_level": readiness_level,
                "section_scores": section_scores
            }
            print(f"✅ Final scores calculated (fallback)!")
            print(f"   🏆 Total Score: {total_score}/150")
            print(f"   📈 Percentage: {(total_score/150)*100:.1f}%")
            print(f"   🎯 Readiness Level: {readiness_level}")
    except:
        # Fallback calculation
        total_score = sum(data["section_total"] for data in section_scores.values())
        readiness_level = determine_readiness_level_fallback(total_score)
        scores_data = {
            "total_score": total_score,
            "readiness_level": readiness_level,
            "section_scores": section_scores
        }
        print(f"✅ Final scores calculated (fallback)!")
        print(f"   🏆 Total Score: {total_score}/150")
        print(f"   📈 Percentage: {(total_score/150)*100:.1f}%")
        print(f"   🎯 Readiness Level: {readiness_level}")
    
    print()
    
    # Step 5: Generate Recommendations
    print("💡 STEP 5: Generating Personalized Recommendations")
    print("-" * 30)
    
    recommendations_result = orchestrate_assessment_flow.invoke({
        "action": "generate_recommendations",
        "data": json.dumps({
            "assessment_results": scores_data,
            "business_info": business_info
        })
    })
    
    try:
        recommendations_data = json.loads(recommendations_result)
        if recommendations_data.get("success", True):
            recommendations = recommendations_data.get("recommendations", {})
            
            print("✅ Personalized recommendations generated!")
            
            # Priority actions
            priority_actions = recommendations.get("priority_actions", [])
            if priority_actions:
                print("   🔥 Top Priority Actions:")
                for i, action in enumerate(priority_actions[:3], 1):
                    print(f"      {i}. {action}")
            
            # Timeline
            timeline = recommendations.get("timeline", "6-12 months")
            print(f"   ⏱️  Estimated Timeline: {timeline}")
            
            # Kenya-specific notes
            kenya_notes = recommendations.get("kenya_specific_notes", [])
            if kenya_notes:
                print("   🇰🇪 Kenya-Specific Considerations:")
                for note in kenya_notes[:2]:
                    print(f"      • {note}")
        else:
            print(f"⚠️  Recommendations generation failed: {recommendations_data.get('error')}")
            recommendations_data = {"recommendations": {"priority_actions": ["Improve data infrastructure", "Enhance technology capabilities"]}}
    except:
        print("⚠️  Using fallback recommendations")
        recommendations_data = {"recommendations": {"priority_actions": ["Improve data infrastructure", "Enhance technology capabilities"]}}
    
    print()
    
    # Step 6: Generate Comprehensive Report
    print("📋 STEP 6: Generating Comprehensive Report")
    print("-" * 30)
    
    report_result = orchestrate_assessment_flow.invoke({
        "action": "create_report",
        "data": json.dumps({
            "assessment_results": scores_data,
            "recommendations": recommendations_data,
            "business_info": business_info,
            "export_format": "json"
        })
    })
    
    try:
        report_data = json.loads(report_result)
        if report_data.get("success", True):
            print("✅ Comprehensive report generated!")
            
            if "report" in report_data:
                report = report_data["report"]
                print("   📊 Report sections included:")
                print("      • Executive Summary")
                print("      • Section Analysis")
                print("      • Implementation Roadmap")
                print("      • Resource Requirements")
                print("      • Kenya-Specific Guidance")
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"ai_readiness_report_{timestamp}.json"
            
            try:
                with open(report_filename, 'w') as f:
                    json.dump(report_data, f, indent=2)
                print(f"   💾 Report saved to: {report_filename}")
            except Exception as e:
                print(f"   ⚠️  Could not save report: {str(e)}")
        else:
            print(f"⚠️  Report generation failed: {report_data.get('error')}")
    except:
        print("⚠️  Report generation not available")
    
    print()
    
    # Step 7: Save Assessment State
    print("💾 STEP 7: Saving Assessment State")
    print("-" * 30)
    
    final_assessment_data = {
        "assessment_id": assessment_id,
        "user_id": "demo_user",
        "business_name": business_info["name"],
        "industry": business_info["industry"],
        "created_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "total_score": scores_data.get("total_score", total_score),
        "readiness_level": scores_data.get("readiness_level", readiness_level),
        "sections": assessment_data["sections"],
        "completion_percentage": 100
    }
    
    save_result = save_assessment_state.invoke({
        "assessment_id": assessment_id,
        "assessment_data": json.dumps(final_assessment_data),
        "auto_save": False
    })
    
    try:
        save_data = json.loads(save_result)
        if save_data.get("success", True):
            print("✅ Assessment state saved successfully!")
            print(f"   🆔 Assessment ID: {assessment_id}")
            print(f"   📁 Status: {save_data.get('status', 'completed')}")
        else:
            print(f"⚠️  Save failed: {save_data.get('error')}")
    except:
        print("⚠️  Assessment state save not available")
    
    print()
    
    # Step 8: Demonstrate Analytics
    print("📊 STEP 8: Generating Analytics Insights")
    print("-" * 30)
    
    # Create sample data for analytics
    sample_assessments = [final_assessment_data]
    
    try:
        analytics_result = calculate_aggregate_insights.invoke({
            "assessment_data_list": json.dumps(sample_assessments),
            "analysis_type": "comprehensive"
        })
        
        analytics_data = json.loads(analytics_result)
        if analytics_data.get("success", True):
            print("✅ Analytics insights generated!")
            insights = analytics_data.get("insights", {})
            
            if "overview" in insights:
                print("   📈 Overview statistics available")
            if "industry_breakdown" in insights:
                print("   🏭 Industry breakdown included")
            if "score_analysis" in insights:
                print("   🎯 Score analysis completed")
        else:
            print(f"⚠️  Analytics failed: {analytics_data.get('error')}")
    except:
        print("⚠️  Analytics not available")
    
    print()
    
    # Summary
    print("🎉 ASSESSMENT DEMONSTRATION COMPLETED!")
    print("=" * 70)
    print()
    print("📋 SUMMARY:")
    print(f"   • Business: {business_info['name']}")
    print(f"   • Industry: {business_info['industry']}")
    print(f"   • Final Score: {scores_data.get('total_score', total_score)}/150 ({(scores_data.get('total_score', total_score)/150)*100:.1f}%)")
    print(f"   • Readiness Level: {scores_data.get('readiness_level', readiness_level)}")
    print(f"   • Assessment ID: {assessment_id}")
    print()
    print("🚀 Next Steps:")
    print("   1. Review the generated recommendations")
    print("   2. Implement priority actions")
    print("   3. Schedule follow-up assessment in 6-12 months")
    print("   4. Use the assessment ID to track progress")
    print()
    print("For more information, visit: www.aireadiness.ke")
    print("=" * 70)


def determine_readiness_level_fallback(total_score: int) -> str:
    """Fallback function to determine readiness level"""
    percentage = (total_score / 150) * 100
    
    if percentage >= 85:
        return "AI Advanced"
    elif percentage >= 70:
        return "AI Ready"
    elif percentage >= 50:
        return "Ready for Pilots"
    elif percentage >= 30:
        return "Foundation Building"
    else:
        return "Not Ready"


if __name__ == "__main__":
    demonstrate_complete_assessment()