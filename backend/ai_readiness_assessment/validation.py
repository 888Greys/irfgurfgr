"""
Validation functions for assessment data
"""

from typing import Dict, Any, List, Tuple
from .models import AssessmentState, SectionScore


def validate_score(score: Any) -> Tuple[bool, str]:
    """
    Validate that a score is within the valid range (1-5)
    
    Args:
        score: The score to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(score, int):
        return False, f"Score must be an integer, got {type(score).__name__}"
    
    if score < 1 or score > 5:
        return False, f"Score must be between 1 and 5, got {score}"
    
    return True, ""


def validate_section_scores(questions: Dict[str, int]) -> Tuple[bool, List[str]]:
    """
    Validate all scores in a section
    
    Args:
        questions: Dictionary of question_id -> score
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not questions:
        errors.append("Section must have at least one question")
        return False, errors
    
    for question_id, score in questions.items():
        is_valid, error_msg = validate_score(score)
        if not is_valid:
            errors.append(f"Question {question_id}: {error_msg}")
    
    return len(errors) == 0, errors


def validate_assessment_data(assessment_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate complete assessment data structure
    
    Args:
        assessment_data: Dictionary containing assessment data
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    required_fields = ["user_id", "business_name", "industry"]
    
    # Check required fields
    for field in required_fields:
        if field not in assessment_data or not assessment_data[field]:
            errors.append(f"Required field '{field}' is missing or empty")
    
    # Validate assessment sections if present
    if "assessment_sections" in assessment_data:
        sections = assessment_data["assessment_sections"]
        if not isinstance(sections, dict):
            errors.append("assessment_sections must be a dictionary")
        else:
            for section_name, section_data in sections.items():
                if isinstance(section_data, dict) and "questions" in section_data:
                    is_valid, section_errors = validate_section_scores(section_data["questions"])
                    if not is_valid:
                        errors.extend([f"Section {section_name}: {error}" for error in section_errors])
    
    return len(errors) == 0, errors


def validate_business_name(business_name: str) -> Tuple[bool, str]:
    """
    Validate business name format
    
    Args:
        business_name: The business name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(business_name, str):
        return False, "Business name must be a string"
    
    if len(business_name.strip()) < 2:
        return False, "Business name must be at least 2 characters long"
    
    if len(business_name) > 100:
        return False, "Business name must be less than 100 characters"
    
    return True, ""


def validate_industry(industry: str) -> Tuple[bool, str]:
    """
    Validate industry format
    
    Args:
        industry: The industry to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    print(f"[DEBUG] validate_industry received: '{industry}' (type: {type(industry)})")
    industry_clean = industry.strip().lower() if isinstance(industry, str) else industry
    print(f"[DEBUG] validate_industry cleaned: '{industry_clean}'")
    valid_industries = [
        "Agriculture", "Manufacturing", "Technology", "Finance", "Healthcare",
        "Education", "Retail", "Transportation", "Construction", "Tourism",
        "Energy", "Telecommunications", "Other"
    ]
    valid_industries_lower = {v.lower(): v for v in valid_industries}

    if not isinstance(industry, str):
        return False, "Industry must be a string"

    industry_clean = industry.strip().lower()
    if industry_clean not in valid_industries_lower:
        return False, f"Industry must be one of: {', '.join(valid_industries)}"

    # Optionally, you could return the canonical industry name here if needed
    return True, ""