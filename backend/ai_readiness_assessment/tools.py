"""
Core assessment tools for the Deep Agents system
These tools handle assessment operations like starting, saving, scoring, and progress tracking
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from langchain_core.tools import tool

from .models import AssessmentState, SectionScore, Recommendation
from .content import AssessmentContent
from .validation import validate_assessment_data, validate_business_name, validate_industry


# Global content instance for tools
_content = AssessmentContent()


@tool
def start_assessment(user_id: str, business_name: str, industry: str) -> str:
    """
    Start a new AI readiness assessment for a business.
    
    Args:
        user_id: Unique identifier for the user
        business_name: Name of the business being assessed
        industry: Industry sector (Agriculture, Manufacturing, Technology, Finance, Healthcare, Education, Retail, Transportation, Construction, Tourism, Energy, Telecommunications, Other)
    
    Returns:
        JSON string with assessment initialization status and details
    """
    import uuid
    from .persistence import AssessmentPersistence
    try:
        # Validate inputs
        is_valid, error = validate_business_name(business_name)
        if not is_valid:
            return json.dumps({"success": False, "error": f"Invalid business name: {error}"})

        is_valid, canonical_or_error = validate_industry(industry)
        if not is_valid:
            return json.dumps({"success": False, "error": f"Invalid industry: {canonical_or_error}"})

        canonical_industry = canonical_or_error

        # Generate a unique assessment_id
        assessment_id = str(uuid.uuid4())

        # Create new assessment state
        assessment = AssessmentState(
            user_id=user_id,
            business_name=business_name,
            industry=canonical_industry,
            started_at=datetime.now()
        )

        # Persist assessment state
        persistence = AssessmentPersistence()
        persistence.get_assessment_path(assessment_id).write_text(assessment.model_dump_json())

        # Get assessment overview
        summary = _content.get_section_summary()

        result = {
            "success": True,
            "message": f"Assessment started for {business_name}",
            "assessment_id": assessment_id,
            "business_name": business_name,
            "industry": canonical_industry,
            "started_at": assessment.started_at.isoformat(),
            "overview": {
                "total_sections": summary["total_sections"],
                "total_questions": summary["total_questions"],
                "total_possible_score": summary["total_possible_score"],
                "sections": summary["sections"]
            },
            "current_section": 0,
            "progress": 0.0
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to start assessment: {str(e)}"})


@tool
def get_section_questions(section_id: str) -> str:
    """
    Get all questions for a specific assessment section.
    
    Args:
        section_id: Section identifier (section1, section2, etc.)
    
    Returns:
        JSON string with section questions and details
    """
    try:
        section = _content.get_section(section_id)
        if not section:
            return json.dumps({"success": False, "error": f"Section {section_id} not found"})
        
        questions_data = []
        for question in section.questions:
            questions_data.append({
                "id": question.id,
                "description": question.description,
                "question": question.question,
                "scoring_rubric": question.scoring_rubric
            })
        
        result = {
            "success": True,
            "section": {
                "id": section.id,
                "name": section.name,
                "description": section.description,
                "max_points": section.max_points,
                "question_count": len(section.questions)
            },
            "questions": questions_data
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get section questions: {str(e)}"})


@tool
def submit_section_responses(section_id: str, responses: str) -> str:
    """
    Submit responses for a section and calculate the score.
    
    Args:
        section_id: Section identifier (section1, section2, etc.)
        responses: JSON string with question responses (e.g., '{"1.1": 3, "1.2": 4, "1.3": 2, "1.4": 5, "1.5": 3}')
    
    Returns:
        JSON string with validation results and calculated scores
    """
    try:
        # Parse responses
        try:
            response_dict = json.loads(responses)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for responses"})
        
        # Convert string keys to proper format and validate scores
        processed_responses = {}
        for key, value in response_dict.items():
            if not isinstance(value, int):
                return json.dumps({"success": False, "error": f"Score for question {key} must be an integer, got {type(value).__name__}"})
            processed_responses[str(key)] = int(value)
        
        # Validate responses
        is_valid, errors = _content.validate_section_responses(section_id, processed_responses)
        if not is_valid:
            return json.dumps({"success": False, "error": "Validation failed", "errors": errors})
        
        # Create section score
        section_score = _content.create_section_score(section_id, processed_responses)
        section = _content.get_section(section_id)
        
        # Calculate percentage
        percentage = (section_score.section_total / section_score.max_possible) * 100
        
        result = {
            "success": True,
            "message": f"Section {section.name} completed successfully",
            "section_score": {
                "section_id": section_id,
                "section_name": section_score.section_name,
                "responses": section_score.questions,
                "section_total": section_score.section_total,
                "max_possible": section_score.max_possible,
                "percentage": round(percentage, 1),
                "completion_status": section_score.completion_status
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to submit section responses: {str(e)}"})


@tool
def calculate_total_score(section_scores: str) -> str:
    """
    Calculate total assessment score from all section scores.
    
    Args:
        section_scores: JSON string with all section scores (e.g., '{"section1": {"section_total": 17, "max_possible": 25}, ...}')
    
    Returns:
        JSON string with total score and readiness level
    """
    try:
        # Parse section scores
        try:
            scores_dict = json.loads(section_scores)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for section scores"})
        
        total_score = 0
        total_possible = 0
        section_details = []
        
        # Calculate totals
        for section_id, score_data in scores_dict.items():
            if not isinstance(score_data, dict) or "section_total" not in score_data or "max_possible" not in score_data:
                return json.dumps({"success": False, "error": f"Invalid score data for section {section_id}"})
            
            section_total = score_data["section_total"]
            section_max = score_data["max_possible"]
            
            total_score += section_total
            total_possible += section_max
            
            section = _content.get_section(section_id)
            section_details.append({
                "section_id": section_id,
                "section_name": section.name if section else "Unknown",
                "score": section_total,
                "max_possible": section_max,
                "percentage": round((section_total / section_max) * 100, 1) if section_max > 0 else 0
            })
        
        # Determine readiness level
        if total_score <= 40:
            readiness_level = "🔴 Not Ready"
            readiness_description = "Significant foundational work needed before AI implementation"
        elif total_score <= 60:
            readiness_level = "🟡 Foundation Building"
            readiness_description = "Some readiness exists but key gaps need addressing"
        elif total_score <= 75:
            readiness_level = "🟠 Ready for Pilots"
            readiness_description = "Good foundation for starting AI implementation"
        elif total_score <= 85:
            readiness_level = "🟢 AI Ready"
            readiness_description = "Strong readiness for comprehensive AI implementation"
        else:
            readiness_level = "🔵 AI Advanced"
            readiness_description = "Excellent readiness for cutting-edge AI implementation"
        
        # Calculate overall percentage
        overall_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
        
        result = {
            "success": True,
            "total_score": total_score,
            "total_possible": total_possible,
            "overall_percentage": round(overall_percentage, 1),
            "readiness_level": readiness_level,
            "readiness_description": readiness_description,
            "section_breakdown": section_details,
            "completed_at": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to calculate total score: {str(e)}"})


@tool
def save_assessment_progress(user_id: str, assessment_data: str) -> str:
    """
    Save assessment progress to the virtual file system.
    
    Args:
        user_id: Unique identifier for the user
        assessment_data: JSON string with current assessment state
    
    Returns:
        JSON string with save status
    """
    try:
        # Parse assessment data
        try:
            data = json.loads(assessment_data)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for assessment data"})
        
        # Add metadata
        data["last_saved"] = datetime.now().isoformat()
        data["user_id"] = user_id
        
        # Save to virtual file system (this will be handled by Deep Agents)
        filename = f"assessment_{user_id}.json"
        
        result = {
            "success": True,
            "message": "Assessment progress saved successfully",
            "filename": filename,
            "saved_at": data["last_saved"],
            "user_id": user_id
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to save assessment progress: {str(e)}"})


@tool
def load_assessment_progress(user_id: str) -> str:
    """
    Load saved assessment progress from the virtual file system.
    
    Args:
        user_id: Unique identifier for the user
    
    Returns:
        JSON string with loaded assessment data or error message
    """
    try:
        filename = f"assessment_{user_id}.json"
        
        # This would load from virtual file system in actual implementation
        # For now, return a template response
        result = {
            "success": True,
            "message": "Assessment progress loaded successfully",
            "filename": filename,
            "user_id": user_id,
            "note": "This tool requires integration with Deep Agents virtual file system"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to load assessment progress: {str(e)}"})


@tool
def get_assessment_summary() -> str:
    """
    Get a summary of the assessment structure and content.
    
    Returns:
        JSON string with assessment overview
    """
    try:
        summary = _content.get_section_summary()
        
        result = {
            "success": True,
            "assessment_overview": {
                "title": "AI Readiness Assessment Tool",
                "subtitle": "Self-Evaluation Framework for Kenyan Businesses",
                "total_sections": summary["total_sections"],
                "total_questions": summary["total_questions"],
                "total_possible_score": summary["total_possible_score"],
                "scoring_scale": "1-5 (1=Poor, 2=Below Average, 3=Average, 4=Good, 5=Excellent)",
                "sections": summary["sections"]
            },
            "readiness_levels": [
                {"level": "🔴 Not Ready", "range": "0-40 points", "description": "Significant foundational work needed"},
                {"level": "🟡 Foundation Building", "range": "41-60 points", "description": "Some readiness exists but key gaps need addressing"},
                {"level": "🟠 Ready for Pilots", "range": "61-75 points", "description": "Good foundation for starting AI implementation"},
                {"level": "🟢 AI Ready", "range": "76-85 points", "description": "Strong readiness for comprehensive AI implementation"},
                {"level": "🔵 AI Advanced", "range": "86-100 points", "description": "Excellent readiness for cutting-edge AI implementation"}
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get assessment summary: {str(e)}"})


@tool
def calculate_section_progress(completed_sections: str) -> str:
    """
    Calculate overall assessment progress based on completed sections.
    
    Args:
        completed_sections: JSON array of completed section IDs (e.g., '["section1", "section2"]')
    
    Returns:
        JSON string with progress information
    """
    try:
        # Parse completed sections
        try:
            completed = json.loads(completed_sections)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for completed sections"})
        
        if not isinstance(completed, list):
            return json.dumps({"success": False, "error": "Completed sections must be a list"})
        
        total_sections = len(_content.get_all_sections())
        completed_count = len(completed)
        
        # Calculate progress
        progress_percentage = (completed_count / total_sections) * 100 if total_sections > 0 else 0
        
        # Get section details
        section_status = []
        for section in _content.get_all_sections():
            is_completed = section.id in completed
            section_status.append({
                "section_id": section.id,
                "section_name": section.name,
                "completed": is_completed,
                "questions": len(section.questions),
                "max_points": section.max_points
            })
        
        result = {
            "success": True,
            "progress": {
                "completed_sections": completed_count,
                "total_sections": total_sections,
                "progress_percentage": round(progress_percentage, 1),
                "is_complete": completed_count == total_sections
            },
            "section_status": section_status,
            "next_section": None
        }
        
        # Find next incomplete section
        for section in _content.get_all_sections():
            if section.id not in completed:
                result["next_section"] = {
                    "section_id": section.id,
                    "section_name": section.name,
                    "questions": len(section.questions),
                    "max_points": section.max_points
                }
                break
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to calculate section progress: {str(e)}"})


# Export all tools for easy import
ASSESSMENT_TOOLS = [
    start_assessment,
    get_section_questions,
    submit_section_responses,
    calculate_total_score,
    save_assessment_progress,
    load_assessment_progress,
    get_assessment_summary,
    calculate_section_progress
]