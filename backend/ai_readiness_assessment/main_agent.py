"""
Main Orchestrating Agent for AI Readiness Assessment
Coordinates all sub-agents and manages the assessment flow
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
import json
from datetime import datetime

# Import sub-agent tools
from .subagents.assessment_guide import (
    get_question_explanation,
    get_section_guidance,
    get_industry_specific_guidance
)
from .subagents.scoring_agent import (
    calculate_section_score,
    determine_readiness_level,
    validate_section_scores
)
from .subagents.kenya_context import (
    get_kenya_regulations,
    get_kenya_business_context,
    get_kenya_ai_landscape
)
from .subagents.recommendation_agent import (
    generate_personalized_recommendations,
    get_recommendation_templates,
    estimate_implementation_timeline
)
from .subagents.report_generator_agent import (
    generate_comprehensive_report,
    export_report_format,
    create_visual_chart_data
)
from .tools import (
    start_assessment,
    save_assessment_progress,
    load_assessment_progress,
    submit_section_responses,
    calculate_total_score
)


class AssessmentOrchestrator:
    """Main orchestrator for the AI readiness assessment process"""
    
    def __init__(self):
        self.current_assessment = None
        self.assessment_state = {}
        self.error_count = 0
        self.max_errors = 3
    
    def handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle errors with fallback mechanisms"""
        self.error_count += 1
        
        error_response = {
            "success": False,
            "error": str(error),
            "context": context,
            "error_count": self.error_count,
            "fallback_available": self.error_count < self.max_errors
        }
        
        if self.error_count >= self.max_errors:
            error_response["message"] = "Maximum errors reached. Please restart the assessment."
        else:
            error_response["message"] = "An error occurred. Attempting to continue with fallback."
        
        return error_response
    
    def reset_error_count(self):
        """Reset error count on successful operations"""
        self.error_count = 0


@tool
def orchestrate_assessment_flow(action: str, data: str = None, assessment_id: str = None) -> str:
    """
    Main orchestration tool for managing the complete assessment flow.
    """
    try:
        orchestrator = AssessmentOrchestrator()
        
        # Parse input data robustly
        if data is None:
            action_data = {}
        elif isinstance(data, str):
            try:
                action_data = json.loads(data)
            except Exception as e:
                print(f"[DEBUG] Failed to parse data as JSON: {data} ({e})")
                action_data = {}
        elif isinstance(data, dict):
            action_data = data
        else:
            action_data = {}

        # Always extract business_info at the very top
        business_info = action_data.get("business_info", {})
        print(f"[DEBUG] business_info received in orchestrator: {business_info}")
        industry_value = business_info["industry"] if "industry" in business_info and business_info["industry"] else "General"
        print(f"[DEBUG] industry_value to be passed: '{industry_value}'")

        # Start new assessment
        assessment_result = start_assessment.invoke({
            "user_id": "current_user",
            "business_name": business_info.get("name", "Unknown Business"),
            "industry": industry_value
        })

        # Route to appropriate handler
        if action == "start_assessment":
            return _handle_start_assessment(orchestrator, action_data)
        elif action == "get_next_question":
            return _handle_get_next_question(orchestrator, assessment_id)
        elif action == "get_question_help":
            return _handle_question_help(orchestrator, action_data)
        elif action == "submit_responses":
            return _handle_submit_responses(orchestrator, action_data, assessment_id)
        elif action == "get_section_guidance":
            return _handle_section_guidance(orchestrator, action_data)
        elif action == "calculate_scores":
            return _handle_calculate_scores(orchestrator, action_data)
        elif action == "generate_recommendations":
            return _handle_generate_recommendations(orchestrator, action_data)
        elif action == "create_report":
            return _handle_create_report(orchestrator, action_data)
        elif action == "get_assessment_status":
            return _handle_get_status(orchestrator, assessment_id)
        elif action == "complete_assessment":
            return _handle_complete_assessment(orchestrator, action_data, assessment_id)
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": [
                    "start_assessment", "get_question_help", "submit_responses",
                    "get_section_guidance", "calculate_scores", "generate_recommendations",
                    "create_report", "get_assessment_status", "complete_assessment"
                ]
            })
    
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, f"orchestrate_assessment_flow - {action}"))


def _handle_start_assessment(orchestrator: AssessmentOrchestrator, data: Dict) -> str:
    """Handle starting a new assessment"""
    try:
        business_info = data.get("business_info", {})
        print(f"[DEBUG] business_info received in orchestrator: {business_info}")
        industry_value = business_info["industry"] if "industry" in business_info and business_info["industry"] else "General"
        print(f"[DEBUG] industry_value to be passed: '{industry_value}'")
        assessment_result = start_assessment.invoke({
            "user_id": "current_user",
            "business_name": business_info.get("name", "Unknown Business"),
            "industry": industry_value
        })
        
        assessment_data = json.loads(assessment_result)
        
        if not assessment_data.get("success"):
            return assessment_result
        
        # Get initial guidance based on industry
        if business_info.get("industry"):
            guidance_result = get_industry_specific_guidance.invoke({
                "industry": business_info["industry"],
                "question_id": "assessment_start"
            })
            
            try:
                guidance_data = json.loads(guidance_result)
                assessment_data["initial_guidance"] = guidance_data
            except:
                # Continue without guidance if it fails
                pass
        
        # Get Kenya-specific context
        try:
            kenya_context = get_kenya_business_context.invoke({
                "industry": industry_value,
                "context_type": "assessment_introduction"
            })
            context_data = json.loads(kenya_context)
            assessment_data["kenya_context"] = context_data
        except:
            # Continue without Kenya context if it fails
            pass
        
        orchestrator.reset_error_count()
        return json.dumps(assessment_data, indent=2)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "start_assessment"))


def _handle_question_help(orchestrator: AssessmentOrchestrator, data: Dict) -> str:
    """Handle requests for question clarification"""
    try:
        question_id = data.get("question_id")
        section = data.get("section")
        user_context = data.get("user_context", {})
        
        if not question_id or not section:
            return json.dumps({
                "success": False,
                "error": "question_id and section are required for help requests"
            })
        
        # Get question clarification
        clarification_result = get_question_explanation.invoke({
            "question_id": question_id
        })
        
        clarification_data = json.loads(clarification_result)
        
        # Enhance with Kenya-specific examples if relevant
        if user_context.get("industry"):
            try:
                examples_result = get_kenya_business_context.invoke({
                    "industry": user_context["industry"],
                    "context_type": "examples"
                })
                
                examples_data = json.loads(examples_result)
                clarification_data["kenya_examples"] = examples_data
            except:
                # Continue without examples if they fail
                pass
        
        orchestrator.reset_error_count()
        return json.dumps(clarification_data, indent=2)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "question_help"))


def _handle_submit_responses(orchestrator: AssessmentOrchestrator, data: Dict, assessment_id: str) -> str:
    """Handle submission of section responses"""
    try:
        section = data.get("section")
        responses = data.get("responses", {})
        
        if not section or not responses:
            return json.dumps({
                "success": False,
                "error": "section and responses are required"
            })
        
        # Validate responses - for single question submission, just validate the score
        from .validation import validate_score
        errors = []
        for question_id, score in responses.items():
            is_valid, error_msg = validate_score(score)
            if not is_valid:
                errors.append(f"Question {question_id}: {error_msg}")
        
        if errors:
            return json.dumps({
                "success": False,
                "error": "Response validation failed",
                "validation_details": {"validation_passed": False, "errors": errors}
            })
        
        # For individual question submission, save to assessment state
        from .persistence import AssessmentPersistence
        from .models import AssessmentState, SectionScore
        
        persistence = AssessmentPersistence()
        path = persistence.get_assessment_path(assessment_id)
        if not path.exists():
            return json.dumps({"success": False, "error": f"Assessment {assessment_id} not found"})
        
        with open(path) as f:
            state_data = json.load(f)
        assessment = AssessmentState(**state_data)
        
        # Update the assessment with the new response
        from .content import AssessmentContent
        content = AssessmentContent()
        section_obj = content.get_section(section)
        if not section_obj:
            return json.dumps({"success": False, "error": f"Section {section} not found"})
            
        if section not in assessment.assessment_sections:
            assessment.assessment_sections[section] = SectionScore(
                section_name=section_obj.name,
                questions={}
            )
        
        assessment.assessment_sections[section].questions.update(responses)
        
        # Save the updated assessment
        persistence.get_assessment_path(assessment_id).write_text(assessment.model_dump_json())
        
        # Return success for individual question submission
        submit_data = {
            "success": True,
            "message": f"Response saved for question {list(responses.keys())[0]}",
            "question_saved": list(responses.keys())[0],
            "score": list(responses.values())[0]
        }
        
        return json.dumps(submit_data)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "submit_responses"))


def _handle_section_guidance(orchestrator: AssessmentOrchestrator, data: Dict) -> str:
    """Handle requests for section-specific guidance"""
    try:
        section = data.get("section")
        user_context = data.get("user_context", {})
        
        if not section:
            return json.dumps({
                "success": False,
                "error": "section is required for guidance requests"
            })
        
        # Get section explanation
        explanation_result = get_section_guidance.invoke({
            "section_id": section
        })
        
        explanation_data = json.loads(explanation_result)
        
        # Add Kenya-specific compliance guidance if relevant
        if section in ["regulatory_compliance", "data_infrastructure"]:
            try:
                compliance_result = get_kenya_regulations.invoke({
                    "regulation_type": "data_protection" if section == "regulatory_compliance" else "general"
                })
                
                compliance_data = json.loads(compliance_result)
                explanation_data["compliance_guidance"] = compliance_data
            except:
                # Continue without compliance guidance if it fails
                pass
        
        orchestrator.reset_error_count()
        return json.dumps(explanation_data, indent=2)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "section_guidance"))


def _handle_calculate_scores(orchestrator: AssessmentOrchestrator, data: Dict) -> str:
    """Handle score calculation for completed assessment"""
    try:
        assessment_data = data.get("assessment_data", {})
        
        if not assessment_data:
            return json.dumps({
                "success": False,
                "error": "assessment_data is required for score calculation"
            })
        
        # Calculate total assessment score
        total_score_result = calculate_total_score.invoke({
            "section_scores": json.dumps(assessment_data.get("sections", {}))
        })
        
        total_score_data = json.loads(total_score_result)
        
        if not total_score_data.get("success"):
            return total_score_result
        
        # Determine readiness level
        readiness_result = determine_readiness_level.invoke({
            "total_score": total_score_data["total_score"],
            "section_scores": json.dumps(total_score_data["section_scores"])
        })
        
        readiness_data = json.loads(readiness_result)
        
        # Combine results
        final_results = {
            "success": True,
            "total_score": total_score_data["total_score"],
            "section_scores": total_score_data["section_scores"],
            "readiness_level": readiness_data.get("readiness_level", "Unknown"),
            "readiness_details": readiness_data,
            "calculated_at": datetime.now().isoformat()
        }
        
        orchestrator.reset_error_count()
        return json.dumps(final_results, indent=2)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "calculate_scores"))


def _handle_generate_recommendations(orchestrator: AssessmentOrchestrator, data: Dict) -> str:
    """Handle generation of personalized recommendations"""
    try:
        assessment_results = data.get("assessment_results", {})
        business_info = data.get("business_info", {})
        
        if not assessment_results:
            return json.dumps({
                "success": False,
                "error": "assessment_results are required for recommendations"
            })
        
        # Generate personalized recommendations
        recommendations_result = generate_personalized_recommendations.invoke({
            "assessment_results": json.dumps(assessment_results),
            "business_info": json.dumps(business_info)
        })
        
        recommendations_data = json.loads(recommendations_result)
        
        if not recommendations_data.get("success"):
            return recommendations_result
        
        # Generate timeline estimates
        try:
            priority_actions = recommendations_data.get("recommendations", {}).get("priority_actions", [])
            
            timeline_result = estimate_implementation_timeline.invoke({
                "assessment_results": json.dumps(assessment_results),
                "priority_actions": json.dumps({"high_priority": priority_actions})
            })
            
            timeline_data = json.loads(timeline_result)
            recommendations_data["timeline_details"] = timeline_data
        except:
            # Continue without detailed timeline if it fails
            pass
        
        orchestrator.reset_error_count()
        return json.dumps(recommendations_data, indent=2)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "generate_recommendations"))


def _handle_create_report(orchestrator: AssessmentOrchestrator, data: Dict) -> str:
    """Handle comprehensive report generation"""
    try:
        assessment_results = data.get("assessment_results", {})
        recommendations = data.get("recommendations", {})
        business_info = data.get("business_info", {})
        export_format = data.get("export_format", "json")
        
        if not assessment_results or not recommendations:
            return json.dumps({
                "success": False,
                "error": "assessment_results and recommendations are required for report generation"
            })
        
        # Generate comprehensive report
        report_result = generate_comprehensive_report.invoke({
            "assessment_results": json.dumps(assessment_results),
            "recommendations": json.dumps(recommendations),
            "business_info": json.dumps(business_info)
        })
        
        report_data = json.loads(report_result)
        
        if not report_data.get("success"):
            return report_result
        
        # Export in requested format if not JSON
        if export_format != "json":
            try:
                export_result = export_report_format.invoke({
                    "report_data": report_result,
                    "format_type": export_format
                })
                
                if export_format in ["markdown", "html"]:
                    # Return formatted text
                    return json.dumps({
                        "success": True,
                        "format": export_format,
                        "content": export_result
                    })
                else:
                    # Return structured data for PDF
                    return export_result
            except:
                # Fall back to JSON if export fails
                pass
        
        orchestrator.reset_error_count()
        return json.dumps(report_data, indent=2)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "create_report"))


def _handle_get_status(orchestrator: AssessmentOrchestrator, assessment_id: str) -> str:
    """Handle assessment status requests"""
    try:
        if not assessment_id:
            return json.dumps({
                "success": False,
                "error": "assessment_id is required for status requests"
            })
        
        # Load assessment state
        state_result = load_assessment_progress.invoke({
            "user_id": assessment_id
        })
        
        state_data = json.loads(state_result)
        
        if not state_data.get("success"):
            return state_result
        
        # Calculate completion percentage
        assessment_state = state_data.get("assessment_state", {})
        completed_sections = len([s for s in assessment_state.get("sections", {}).values() if s.get("completed")])
        total_sections = 6  # We have 6 assessment sections
        completion_percentage = (completed_sections / total_sections) * 100
        
        status_response = {
            "success": True,
            "assessment_id": assessment_id,
            "completion_percentage": completion_percentage,
            "completed_sections": completed_sections,
            "total_sections": total_sections,
            "current_section": assessment_state.get("current_section"),
            "assessment_state": assessment_state,
            "last_updated": assessment_state.get("last_updated")
        }
        
        orchestrator.reset_error_count()
        return json.dumps(status_response, indent=2)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "get_status"))


def _handle_complete_assessment(orchestrator: AssessmentOrchestrator, data: Dict, assessment_id: str) -> str:
    """Handle complete assessment workflow"""
    try:
        assessment_data = data.get("assessment_data", {})
        business_info = data.get("business_info", {})
        
        if not assessment_data:
            return json.dumps({
                "success": False,
                "error": "assessment_data is required for completion"
            })
        
        # Step 1: Calculate final scores
        scores_result = _handle_calculate_scores(orchestrator, {"assessment_data": assessment_data})
        scores_data = json.loads(scores_result)
        
        if not scores_data.get("success"):
            return scores_result
        
        # Step 2: Generate recommendations
        recommendations_result = _handle_generate_recommendations(orchestrator, {
            "assessment_results": scores_data,
            "business_info": business_info
        })
        
        recommendations_data = json.loads(recommendations_result)
        
        if not recommendations_data.get("success"):
            return recommendations_result
        
        # Step 3: Generate comprehensive report
        report_result = _handle_create_report(orchestrator, {
            "assessment_results": scores_data,
            "recommendations": recommendations_data,
            "business_info": business_info,
            "export_format": data.get("export_format", "json")
        })
        
        report_data = json.loads(report_result)
        
        if not report_data.get("success"):
            return report_result
        
        # Step 4: Save final results
        try:
            final_results = {
                "assessment_results": scores_data,
                "recommendations": recommendations_data,
                "report": report_data,
                "completed_at": datetime.now().isoformat()
            }
            
            save_result = save_assessment_progress.invoke({
                "user_id": assessment_id or "current_user",
                "assessment_data": json.dumps(final_results)
            })
        except:
            # Continue even if save fails
            pass
        
        # Return complete results
        completion_response = {
            "success": True,
            "assessment_id": assessment_id,
            "completion_status": "completed",
            "final_results": {
                "scores": scores_data,
                "recommendations": recommendations_data,
                "report": report_data
            },
            "completed_at": datetime.now().isoformat()
        }
        
        orchestrator.reset_error_count()
        return json.dumps(completion_response, indent=2)
        
    except Exception as e:
        return json.dumps(orchestrator.handle_error(e, "complete_assessment"))


def _handle_get_next_question(orchestrator: AssessmentOrchestrator, assessment_id: str) -> str:
    """Return the next unanswered question for the current section, or advance section, or finish."""
    from .persistence import AssessmentPersistence
    from .content import AssessmentContent
    from .models import AssessmentState
    import os
    try:
        persistence = AssessmentPersistence()
        path = persistence.get_assessment_path(assessment_id)
        if not path.exists():
            return json.dumps({"success": False, "error": f"Assessment {assessment_id} not found"})
        with open(path) as f:
            state_data = json.load(f)
        # Reconstruct AssessmentState
        assessment = AssessmentState(**state_data)
        content = AssessmentContent()
        sections = content.sections
        # Find current section
        current_section_idx = assessment.current_section
        if current_section_idx >= len(sections):
            return json.dumps({"success": True, "completed": True, "message": "Assessment complete", "results": state_data})
        section = sections[current_section_idx]
        # Get answered questions for this section
        section_scores = assessment.assessment_sections.get(section.id)
        answered = set(section_scores.questions.keys()) if section_scores else set()
        # Find next unanswered question
        for q in section.questions:
            if q.id not in answered:
                return json.dumps({
                    "success": True,
                    "question": q.question,
                    "question_id": q.id,
                    "section_id": section.id,
                    "section_name": section.name,
                    "description": q.description,
                    "scoring_rubric": q.scoring_rubric,
                    "current_section": current_section_idx,
                    "answered": list(answered)
                })
        # If all questions answered, advance section
        if current_section_idx + 1 < len(sections):
            assessment.current_section += 1
            # Save state
            persistence.get_assessment_path(assessment_id).write_text(assessment.model_dump_json())
            # Recursively get next question in new section
            return _handle_get_next_question(orchestrator, assessment_id)
        # If all sections complete
        assessment.progress = 1.0
        persistence.get_assessment_path(assessment_id).write_text(assessment.model_dump_json())
        return json.dumps({"success": True, "completed": True, "message": "Assessment complete", "results": state_data})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get next question: {str(e)}"})


@tool
def get_available_actions() -> str:
    """
    Get list of available actions and their descriptions.
    
    Returns:
        JSON string with available actions and usage information
    """
    actions = {
        "start_assessment": {
            "description": "Start a new AI readiness assessment",
            "required_data": ["business_info"],
            "optional_data": ["assessment_preferences"],
            "example": {
                "action": "start_assessment",
                "data": {
                    "business_info": {
                        "name": "TechCorp Kenya",
                        "industry": "Financial Services",
                        "size": "Medium"
                    }
                }
            }
        },
        "get_question_help": {
            "description": "Get clarification and examples for assessment questions",
            "required_data": ["question_id", "section"],
            "optional_data": ["user_context"],
            "example": {
                "action": "get_question_help",
                "data": {
                    "question_id": "data_collection_processes",
                    "section": "data_infrastructure",
                    "user_context": {"industry": "Manufacturing"}
                }
            }
        },
        "submit_responses": {
            "description": "Submit responses for a completed assessment section",
            "required_data": ["section", "responses"],
            "optional_data": [],
            "example": {
                "action": "submit_responses",
                "data": {
                    "section": "data_infrastructure",
                    "responses": {"q1": 4, "q2": 3, "q3": 5}
                },
                "assessment_id": "assessment_123"
            }
        },
        "get_section_guidance": {
            "description": "Get detailed guidance for an assessment section",
            "required_data": ["section"],
            "optional_data": ["user_context"],
            "example": {
                "action": "get_section_guidance",
                "data": {
                    "section": "regulatory_compliance",
                    "user_context": {"industry": "Healthcare"}
                }
            }
        },
        "calculate_scores": {
            "description": "Calculate scores for completed assessment",
            "required_data": ["assessment_data"],
            "optional_data": [],
            "example": {
                "action": "calculate_scores",
                "data": {
                    "assessment_data": {"sections": {"data_infrastructure": {"responses": {"q1": 4}}}}
                }
            }
        },
        "generate_recommendations": {
            "description": "Generate personalized recommendations based on assessment results",
            "required_data": ["assessment_results"],
            "optional_data": ["business_info"],
            "example": {
                "action": "generate_recommendations",
                "data": {
                    "assessment_results": {"total_score": 75, "readiness_level": "AI Ready"},
                    "business_info": {"industry": "Manufacturing"}
                }
            }
        },
        "create_report": {
            "description": "Generate comprehensive assessment report",
            "required_data": ["assessment_results", "recommendations"],
            "optional_data": ["business_info", "export_format"],
            "example": {
                "action": "create_report",
                "data": {
                    "assessment_results": {"total_score": 75},
                    "recommendations": {"priority_actions": []},
                    "export_format": "markdown"
                }
            }
        },
        "get_assessment_status": {
            "description": "Get current status of an ongoing assessment",
            "required_data": [],
            "optional_data": [],
            "example": {
                "action": "get_assessment_status",
                "assessment_id": "assessment_123"
            }
        },
        "complete_assessment": {
            "description": "Complete the entire assessment workflow (scores, recommendations, report)",
            "required_data": ["assessment_data"],
            "optional_data": ["business_info", "export_format"],
            "example": {
                "action": "complete_assessment",
                "data": {
                    "assessment_data": {"sections": {}},
                    "business_info": {"name": "Company"}
                },
                "assessment_id": "assessment_123"
            }
        }
    }
    
    return json.dumps({
        "success": True,
        "available_actions": actions,
        "usage_notes": [
            "All data parameters should be provided as JSON strings",
            "assessment_id is optional for most actions but recommended for tracking",
            "Error handling includes automatic fallback mechanisms",
            "Actions can be chained together for complete workflows"
        ]
    }, indent=2)


@tool
def health_check() -> str:
    """
    Perform health check on all sub-agents and core systems.
    
    Returns:
        JSON string with health status of all components
    """
    health_status = {
        "overall_status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Test each sub-agent
    components_to_test = [
        ("assessment_guide", get_question_explanation),
        ("scoring_agent", calculate_section_score),
        ("kenya_context", get_kenya_regulations),
        ("recommendation_agent", generate_personalized_recommendations),
        ("report_generator", generate_comprehensive_report),
        ("core_tools", start_assessment)
    ]
    
    for component_name, test_tool in components_to_test:
        try:
            # Perform a minimal test call
            if component_name == "assessment_guide":
                result = test_tool.invoke({
                    "question_id": "test_question"
                })
            elif component_name == "scoring_agent":
                result = test_tool.invoke({
                    "section_id": "data_infrastructure",
                    "responses": '{"q1": 3}'
                })
            elif component_name == "kenya_context":
                result = test_tool.invoke({
                    "regulation_type": "data_protection"
                })
            elif component_name == "recommendation_agent":
                result = test_tool.invoke({
                    "assessment_results": '{"total_score": 50, "readiness_level": "Foundation Building"}',
                    "business_info": "{}"
                })
            elif component_name == "report_generator":
                result = test_tool.invoke({
                    "assessment_results": '{"total_score": 50}',
                    "recommendations": '{"recommendations": {}}',
                    "business_info": "{}"
                })
            elif component_name == "core_tools":
                result = test_tool.invoke({
                    "user_id": "test_user",
                    "business_name": "Test Business",
                    "industry": "General"
                })
            
            # Check if result indicates success
            try:
                result_data = json.loads(result)
                if result_data.get("success", True):  # Default to True if no success field
                    health_status["components"][component_name] = "healthy"
                else:
                    health_status["components"][component_name] = "degraded"
                    health_status["overall_status"] = "degraded"
            except:
                # If we can't parse JSON, assume it's working if no exception was thrown
                health_status["components"][component_name] = "healthy"
                
        except Exception as e:
            health_status["components"][component_name] = f"unhealthy: {str(e)}"
            health_status["overall_status"] = "unhealthy"
    
    return json.dumps(health_status, indent=2)
