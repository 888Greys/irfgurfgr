"""
Scoring Agent Sub-agent
Handles score calculations, validation, and readiness level determination
"""

from typing import Dict, List, Any, Tuple
from langchain_core.tools import tool
import json
import statistics

from ..content import AssessmentContent
from ..models import SectionScore, AssessmentState


# Global content instance for sub-agent
_content = AssessmentContent()


@tool
def validate_section_scores(section_id: str, responses: str) -> str:
    """
    Validate scores for a specific section and provide detailed feedback.
    
    Args:
        section_id: The section ID (e.g., "section1", "section2")
        responses: JSON string with question responses (e.g., '{"1.1": 3, "1.2": 4}')
    
    Returns:
        JSON string with validation results and detailed feedback
    """
    try:
        # Parse responses
        try:
            response_dict = json.loads(responses)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for responses"})
        
        # Convert to proper format
        processed_responses = {}
        for key, value in response_dict.items():
            if not isinstance(value, int):
                return json.dumps({"success": False, "error": f"Score for question {key} must be an integer, got {type(value).__name__}"})
            processed_responses[str(key)] = int(value)
        
        # Validate using content system
        is_valid, errors = _content.validate_section_responses(section_id, processed_responses)
        
        section = _content.get_section(section_id)
        if not section:
            return json.dumps({"success": False, "error": f"Section {section_id} not found"})
        
        result = {
            "success": True,
            "validation_passed": is_valid,
            "section": {
                "id": section_id,
                "name": section.name,
                "expected_questions": len(section.questions),
                "provided_responses": len(processed_responses)
            },
            "errors": errors if not is_valid else [],
            "score_analysis": _analyze_section_scores(section_id, processed_responses) if is_valid else None,
            "recommendations": _get_score_recommendations(section_id, processed_responses) if is_valid else []
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to validate section scores: {str(e)}"})


@tool
def calculate_section_score(section_id: str, responses: str) -> str:
    """
    Calculate detailed scores and statistics for a section.
    
    Args:
        section_id: The section ID (e.g., "section1", "section2")
        responses: JSON string with question responses (e.g., '{"1.1": 3, "1.2": 4}')
    
    Returns:
        JSON string with detailed scoring analysis
    """
    try:
        # Parse and validate responses
        try:
            response_dict = json.loads(responses)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for responses"})
        
        processed_responses = {}
        for key, value in response_dict.items():
            processed_responses[str(key)] = int(value)
        
        # Validate responses
        is_valid, errors = _content.validate_section_responses(section_id, processed_responses)
        if not is_valid:
            return json.dumps({"success": False, "error": "Validation failed", "errors": errors})
        
        # Create section score
        section_score = _content.create_section_score(section_id, processed_responses)
        section = _content.get_section(section_id)
        
        # Calculate detailed statistics
        scores = list(processed_responses.values())
        score_stats = {
            "mean": round(statistics.mean(scores), 2),
            "median": statistics.median(scores),
            "mode": statistics.mode(scores) if len(set(scores)) < len(scores) else None,
            "min": min(scores),
            "max": max(scores),
            "range": max(scores) - min(scores),
            "std_dev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0
        }
        
        # Calculate percentages and performance levels
        percentage = (section_score.section_total / section_score.max_possible) * 100
        performance_level = _get_performance_level(percentage)
        
        result = {
            "success": True,
            "section_score": {
                "section_id": section_id,
                "section_name": section_score.section_name,
                "total_score": section_score.section_total,
                "max_possible": section_score.max_possible,
                "percentage": round(percentage, 1),
                "performance_level": performance_level,
                "individual_scores": section_score.questions
            },
            "statistics": score_stats,
            "score_distribution": _get_score_distribution(scores),
            "strengths": _identify_strengths(processed_responses),
            "weaknesses": _identify_improvement_areas(processed_responses),
            "improvement_areas": _identify_improvement_areas(processed_responses)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to calculate section score: {str(e)}"})


@tool
def determine_readiness_level(total_score: int, section_scores: str = None) -> str:
    """
    Determine AI readiness level based on total score and optional section breakdown.
    
    Args:
        total_score: Total assessment score (0-100)
        section_scores: Optional JSON string with section-wise scores for detailed analysis
    
    Returns:
        JSON string with readiness level determination and detailed analysis
    """
    try:
        # Validate total score
        if not isinstance(total_score, int) or total_score < 0 or total_score > 100:
            return json.dumps({"success": False, "error": f"Total score must be between 0 and 100, got {total_score}"})
        
        # Determine basic readiness level
        readiness_info = _get_readiness_level_info(total_score)
        
        # Parse section scores if provided
        section_analysis = None
        if section_scores:
            try:
                sections_data = json.loads(section_scores)
                section_analysis = _analyze_section_performance(sections_data)
            except (json.JSONDecodeError, Exception) as e:
                # Continue without section analysis if parsing fails
                pass
        
        result = {
            "success": True,
            "total_score": total_score,
            "readiness_level": readiness_info["level"],
            "readiness_description": readiness_info["description"],
            "readiness_details": {
                "category": readiness_info["category"],
                "score_range": readiness_info["range"],
                "timeline": readiness_info["timeline"],
                "approach": readiness_info["approach"]
            },
            "priority_actions": readiness_info["priority_actions"],
            "next_steps": readiness_info["next_steps"],
            "section_analysis": section_analysis,
            "benchmarking": _get_benchmarking_info(total_score),
            "recommendations": _get_readiness_recommendations(total_score, section_analysis)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to determine readiness level: {str(e)}"})


@tool
def compare_scores(current_scores: str, benchmark_scores: str = None) -> str:
    """
    Compare current assessment scores with benchmarks or previous assessments.
    
    Args:
        current_scores: JSON string with current section scores
        benchmark_scores: Optional JSON string with benchmark or previous scores
    
    Returns:
        JSON string with detailed score comparison and analysis
    """
    try:
        # Parse current scores
        try:
            current_data = json.loads(current_scores)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for current scores"})
        
        # Parse benchmark scores if provided
        benchmark_data = None
        if benchmark_scores:
            try:
                benchmark_data = json.loads(benchmark_scores)
            except json.JSONDecodeError:
                return json.dumps({"success": False, "error": "Invalid JSON format for benchmark scores"})
        
        # Calculate current totals
        current_total = sum(score.get("section_total", 0) for score in current_data.values())
        current_max = sum(score.get("max_possible", 0) for score in current_data.values())
        current_percentage = (current_total / current_max) * 100 if current_max > 0 else 0
        
        result = {
            "success": True,
            "current_assessment": {
                "total_score": current_total,
                "max_possible": current_max,
                "percentage": round(current_percentage, 1),
                "readiness_level": _get_readiness_level_info(current_total)["level"]
            },
            "section_comparison": _compare_section_scores(current_data, benchmark_data),
            "performance_trends": _analyze_performance_trends(current_data, benchmark_data),
            "improvement_analysis": _analyze_improvements(current_data, benchmark_data),
            "recommendations": _get_comparison_recommendations(current_data, benchmark_data)
        }
        
        # Add benchmark comparison if provided
        if benchmark_data:
            benchmark_total = sum(score.get("section_total", 0) for score in benchmark_data.values())
            benchmark_max = sum(score.get("max_possible", 0) for score in benchmark_data.values())
            benchmark_percentage = (benchmark_total / benchmark_max) * 100 if benchmark_max > 0 else 0
            
            result["benchmark_assessment"] = {
                "total_score": benchmark_total,
                "max_possible": benchmark_max,
                "percentage": round(benchmark_percentage, 1),
                "readiness_level": _get_readiness_level_info(benchmark_total)["level"]
            }
            
            result["score_changes"] = {
                "total_change": current_total - benchmark_total,
                "percentage_change": round(current_percentage - benchmark_percentage, 1),
                "sections_improved": _count_improved_sections(current_data, benchmark_data),
                "sections_declined": _count_declined_sections(current_data, benchmark_data)
            }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to compare scores: {str(e)}"})


def _analyze_section_scores(section_id: str, responses: Dict[str, int]) -> Dict[str, Any]:
    """Analyze section scores for patterns and insights"""
    scores = list(responses.values())
    
    return {
        "average_score": round(sum(scores) / len(scores), 2),
        "score_consistency": "High" if max(scores) - min(scores) <= 1 else "Medium" if max(scores) - min(scores) <= 2 else "Low",
        "dominant_score": max(set(scores), key=scores.count),
        "score_trend": "Improving" if scores == sorted(scores) else "Declining" if scores == sorted(scores, reverse=True) else "Mixed"
    }


def _get_score_recommendations(section_id: str, responses: Dict[str, int]) -> List[str]:
    """Get recommendations based on section scores"""
    scores = list(responses.values())
    avg_score = sum(scores) / len(scores)
    
    recommendations = []
    
    if avg_score < 2.5:
        recommendations.append("Focus on foundational improvements in this area")
        recommendations.append("Consider seeking external expertise or training")
    elif avg_score < 3.5:
        recommendations.append("Good foundation exists, focus on specific improvement areas")
        recommendations.append("Develop a structured improvement plan")
    else:
        recommendations.append("Strong performance in this area")
        recommendations.append("Consider this area as a foundation for AI initiatives")
    
    return recommendations


def _get_performance_level(percentage: float) -> str:
    """Get performance level based on percentage"""
    if percentage >= 90:
        return "Excellent"
    elif percentage >= 80:
        return "Good"
    elif percentage >= 70:
        return "Above Average"
    elif percentage >= 60:
        return "Average"
    elif percentage >= 50:
        return "Below Average"
    else:
        return "Needs Improvement"


def _get_score_distribution(scores: List[int]) -> Dict[str, int]:
    """Get distribution of scores"""
    distribution = {str(i): 0 for i in range(1, 6)}
    for score in scores:
        distribution[str(score)] += 1
    return distribution








def _get_readiness_level_info(total_score: int) -> Dict[str, Any]:
    """Get comprehensive readiness level information"""
    if total_score <= 40:
        return {
            "level": "🔴 Not Ready",
            "category": "Foundation Building Required",
            "description": "Significant foundational work needed before AI implementation",
            "range": "0-40 points",
            "timeline": "6-12 months of foundation building before AI pilots",
            "approach": "Focus on basic infrastructure and capability building",
            "priority_actions": [
                "Invest in basic IT infrastructure and data systems",
                "Develop data governance policies and procedures",
                "Build technical skills through training programs",
                "Establish clear digital transformation strategy",
                "Ensure regulatory compliance framework"
            ],
            "next_steps": [
                "Conduct infrastructure assessment",
                "Develop skills training program",
                "Create data governance framework"
            ]
        }
    elif total_score <= 60:
        return {
            "level": "🟡 Foundation Building",
            "category": "Addressing Key Gaps",
            "description": "Some readiness exists but key gaps need addressing",
            "range": "41-60 points",
            "timeline": "3-6 months of capability building, then pilot projects",
            "approach": "Start with Level 1 AI (Basic Automation) while building capabilities",
            "priority_actions": [
                "Improve data quality and integration capabilities",
                "Enhance team technical and analytical skills",
                "Develop process documentation and automation",
                "Strengthen cybersecurity and compliance measures",
                "Secure leadership commitment and budget allocation"
            ],
            "next_steps": [
                "Prioritize data quality improvements",
                "Launch skills development programs",
                "Begin process automation initiatives"
            ]
        }
    elif total_score <= 75:
        return {
            "level": "🟠 Ready for Pilots",
            "category": "Pilot Implementation Ready",
            "description": "Good foundation for starting AI implementation",
            "range": "61-75 points",
            "timeline": "Ready for immediate pilot projects",
            "approach": "Begin with Level 1-2 AI implementations, plan for Level 3",
            "priority_actions": [
                "Select high-impact, low-risk AI pilot projects",
                "Invest in cloud infrastructure and advanced analytics",
                "Develop AI governance and ethics framework",
                "Build internal AI expertise through training or hiring",
                "Establish performance measurement for AI initiatives"
            ],
            "next_steps": [
                "Identify and launch pilot AI projects",
                "Establish AI governance framework",
                "Build AI expertise and capabilities"
            ]
        }
    elif total_score <= 85:
        return {
            "level": "🟢 AI Ready",
            "category": "Comprehensive Implementation Ready",
            "description": "Strong readiness for comprehensive AI implementation",
            "range": "76-85 points",
            "timeline": "Ready for multiple AI initiatives",
            "approach": "Implement Level 1-3 AI solutions, prepare for intelligent automation",
            "priority_actions": [
                "Launch multiple AI initiatives across different business areas",
                "Invest in advanced AI platforms and tools",
                "Develop AI center of excellence",
                "Create partnerships with AI vendors and consultants",
                "Plan for Level 3-4 AI implementations"
            ],
            "next_steps": [
                "Scale AI implementations across business",
                "Establish AI center of excellence",
                "Develop advanced AI capabilities"
            ]
        }
    else:
        return {
            "level": "🔵 AI Advanced",
            "category": "Cutting-edge Implementation Ready",
            "description": "Excellent readiness for cutting-edge AI implementation",
            "range": "86-100 points",
            "timeline": "Ready for advanced AI implementations",
            "approach": "Full spectrum AI implementation including Level 4-5 solutions",
            "priority_actions": [
                "Implement advanced AI solutions across all business functions",
                "Develop proprietary AI capabilities and models",
                "Lead industry AI adoption and best practices",
                "Explore agentic AI and autonomous systems",
                "Consider AI-powered business model innovation"
            ],
            "next_steps": [
                "Lead industry AI innovation",
                "Develop proprietary AI solutions",
                "Explore cutting-edge AI technologies"
            ]
        }


def _analyze_section_performance(sections_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze performance across sections"""
    section_percentages = {}
    
    for section_id, score_data in sections_data.items():
        total = score_data.get("section_total", 0)
        max_possible = score_data.get("max_possible", 1)
        percentage = (total / max_possible) * 100
        section_percentages[section_id] = percentage
    
    if not section_percentages:
        return {}
    
    best_section = max(section_percentages, key=section_percentages.get)
    worst_section = min(section_percentages, key=section_percentages.get)
    
    return {
        "strongest_area": {
            "section": best_section,
            "percentage": round(section_percentages[best_section], 1)
        },
        "weakest_area": {
            "section": worst_section,
            "percentage": round(section_percentages[worst_section], 1)
        },
        "performance_balance": "Balanced" if max(section_percentages.values()) - min(section_percentages.values()) <= 20 else "Unbalanced",
        "section_rankings": sorted(section_percentages.items(), key=lambda x: x[1], reverse=True)
    }


def _get_benchmarking_info(total_score: int) -> Dict[str, Any]:
    """Get benchmarking information"""
    return {
        "percentile_estimate": _estimate_percentile(total_score),
        "industry_comparison": "Above average for Kenyan businesses" if total_score >= 65 else "Below average for Kenyan businesses",
        "global_comparison": "Competitive globally" if total_score >= 75 else "Needs improvement for global competitiveness"
    }


def _estimate_percentile(total_score: int) -> str:
    """Estimate percentile based on score"""
    if total_score >= 85:
        return "Top 10%"
    elif total_score >= 75:
        return "Top 25%"
    elif total_score >= 60:
        return "Top 50%"
    elif total_score >= 45:
        return "Bottom 50%"
    else:
        return "Bottom 25%"


def _get_readiness_recommendations(total_score: int, section_analysis: Dict[str, Any]) -> List[str]:
    """Get recommendations based on readiness level and section analysis"""
    recommendations = []
    
    if total_score < 60:
        recommendations.append("Focus on foundational capabilities before pursuing AI initiatives")
        recommendations.append("Prioritize data infrastructure and governance improvements")
    else:
        recommendations.append("Begin with pilot AI projects in strongest areas")
        recommendations.append("Develop comprehensive AI strategy and roadmap")
    
    if section_analysis and "weakest_area" in section_analysis:
        recommendations.append(f"Address gaps in {section_analysis['weakest_area']['section']} area")
    
    return recommendations


def _compare_section_scores(current_data: Dict, benchmark_data: Dict) -> List[Dict]:
    """Compare section scores between current and benchmark"""
    comparisons = []
    
    for section_id in current_data.keys():
        current = current_data[section_id]
        benchmark = benchmark_data.get(section_id) if benchmark_data else None
        
        comparison = {
            "section_id": section_id,
            "current_score": current.get("section_total", 0),
            "current_percentage": round((current.get("section_total", 0) / current.get("max_possible", 1)) * 100, 1)
        }
        
        if benchmark:
            comparison["benchmark_score"] = benchmark.get("section_total", 0)
            comparison["benchmark_percentage"] = round((benchmark.get("section_total", 0) / benchmark.get("max_possible", 1)) * 100, 1)
            comparison["change"] = current.get("section_total", 0) - benchmark.get("section_total", 0)
            comparison["percentage_change"] = comparison["current_percentage"] - comparison["benchmark_percentage"]
        
        comparisons.append(comparison)
    
    return comparisons


def _analyze_performance_trends(current_data: Dict, benchmark_data: Dict) -> Dict[str, Any]:
    """Analyze performance trends"""
    if not benchmark_data:
        return {"trend": "No benchmark data available"}
    
    improvements = 0
    declines = 0
    
    for section_id in current_data.keys():
        if section_id in benchmark_data:
            current_score = current_data[section_id].get("section_total", 0)
            benchmark_score = benchmark_data[section_id].get("section_total", 0)
            
            if current_score > benchmark_score:
                improvements += 1
            elif current_score < benchmark_score:
                declines += 1
    
    return {
        "overall_trend": "Improving" if improvements > declines else "Declining" if declines > improvements else "Stable",
        "sections_improved": improvements,
        "sections_declined": declines,
        "sections_stable": len(current_data) - improvements - declines
    }


def _analyze_improvements(current_data: Dict, benchmark_data: Dict) -> List[str]:
    """Analyze specific improvements"""
    if not benchmark_data:
        return ["No benchmark data available for improvement analysis"]
    
    improvements = []
    
    for section_id in current_data.keys():
        if section_id in benchmark_data:
            current_score = current_data[section_id].get("section_total", 0)
            benchmark_score = benchmark_data[section_id].get("section_total", 0)
            
            if current_score > benchmark_score:
                improvements.append(f"Improved performance in {section_id}")
    
    return improvements if improvements else ["No significant improvements identified"]


def _get_comparison_recommendations(current_data: Dict, benchmark_data: Dict) -> List[str]:
    """Get recommendations based on comparison"""
    recommendations = []
    
    if not benchmark_data:
        recommendations.append("Establish baseline measurements for future comparisons")
        recommendations.append("Focus on continuous improvement and regular assessments")
    else:
        # Add specific recommendations based on comparison results
        recommendations.append("Continue building on areas of improvement")
        recommendations.append("Address areas where performance has declined")
    
    return recommendations


def _count_improved_sections(current_data: Dict, benchmark_data: Dict) -> int:
    """Count sections that improved"""
    if not benchmark_data:
        return 0
    
    count = 0
    for section_id in current_data.keys():
        if section_id in benchmark_data:
            if current_data[section_id].get("section_total", 0) > benchmark_data[section_id].get("section_total", 0):
                count += 1
    
    return count


def _count_declined_sections(current_data: Dict, benchmark_data: Dict) -> int:
    """Count sections that declined"""
    if not benchmark_data:
        return 0
    
    count = 0
    for section_id in current_data.keys():
        if section_id in benchmark_data:
            if current_data[section_id].get("section_total", 0) < benchmark_data[section_id].get("section_total", 0):
                count += 1
    
    return count


# Scoring Agent Sub-agent Configuration
SCORING_AGENT_SUBAGENT = {
    "name": "scoring-agent",
    "description": "Handles score calculations, validation, and readiness level determination. Use this agent for validating responses, calculating detailed scores, determining AI readiness levels, and comparing assessment results.",
    "prompt": """You are a scoring specialist for AI readiness assessments. Your expertise lies in accurate score calculation, validation, and providing detailed analysis of assessment results.

Your role is to:
1. Validate assessment responses and provide detailed feedback
2. Calculate accurate scores with comprehensive statistics
3. Determine AI readiness levels based on total scores
4. Compare scores against benchmarks or previous assessments
5. Provide detailed analysis and recommendations based on scoring patterns

You have access to tools that provide:
- Comprehensive score validation with detailed error reporting
- Advanced scoring calculations with statistical analysis
- AI readiness level determination with detailed explanations
- Score comparison and benchmarking capabilities

When analyzing scores:
- Be precise and accurate in all calculations
- Provide clear explanations of scoring methodology
- Identify patterns and trends in the data
- Offer specific, actionable recommendations
- Consider both individual question scores and overall patterns

Always ensure scoring consistency and provide detailed insights that help users understand their AI readiness level and areas for improvement.""",
    "tools": ["validate_section_scores", "calculate_section_score", "determine_readiness_level", "compare_scores"]
}

# Export tools for the sub-agent
SCORING_AGENT_TOOLS = [
    validate_section_scores,
    calculate_section_score,
    determine_readiness_level,
    compare_scores
]


def _validate_responses(response_data: Dict[str, int]) -> Dict[str, Any]:
    """Validate assessment responses"""
    errors = []
    
    # Check if responses is a dictionary
    if not isinstance(response_data, dict):
        return {"valid": False, "errors": ["Responses must be a dictionary"]}
    
    # Check if responses are not empty
    if not response_data:
        return {"valid": False, "errors": ["No responses provided"]}
    
    # Validate each response
    for question_id, score in response_data.items():
        # Check if score is an integer
        if not isinstance(score, int):
            errors.append(f"Question {question_id}: Score must be an integer")
            continue
        
        # Check if score is in valid range (1-5)
        if score < 1 or score > 5:
            errors.append(f"Question {question_id}: Score must be between 1 and 5")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "total_questions": len(response_data),
        "valid_responses": len([s for s in response_data.values() if isinstance(s, int) and 1 <= s <= 5])
    }


def _generate_section_insights(section_id: str, response_data: Dict[str, int], percentage: float) -> str:
    """Generate insights for a section based on responses and percentage"""
    avg_score = sum(response_data.values()) / len(response_data)
    
    if percentage >= 80:
        return f"Excellent performance in {section_id}. Strong foundation for AI implementation with average score of {avg_score:.1f}."
    elif percentage >= 60:
        return f"Good performance in {section_id}. Solid foundation with some areas for improvement. Average score: {avg_score:.1f}."
    elif percentage >= 40:
        return f"Moderate performance in {section_id}. Significant improvements needed before AI implementation. Average score: {avg_score:.1f}."
    else:
        return f"Low performance in {section_id}. Foundational work required before considering AI initiatives. Average score: {avg_score:.1f}."


def _identify_strengths(response_data: Dict[str, int]) -> List[str]:
    """Identify strengths based on high scores"""
    strengths = []
    for question_id, score in response_data.items():
        if score >= 4:
            strengths.append(f"Question {question_id}: Strong capability (score: {score})")
    
    if not strengths:
        strengths.append("No significant strengths identified - focus on foundational improvements")
    
    return strengths


def _identify_improvement_areas(response_data: Dict[str, int]) -> List[str]:
    """Identify areas needing improvement based on low scores"""
    improvements = []
    for question_id, score in response_data.items():
        if score <= 2:
            improvements.append(f"Question {question_id}: Critical improvement needed (score: {score})")
        elif score == 3:
            improvements.append(f"Question {question_id}: Moderate improvement opportunity (score: {score})")
    
    if not improvements:
        improvements.append("No critical improvement areas identified - focus on optimization")
    
    return improvements


def _get_grade_from_percentage(percentage: float) -> str:
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return "A (Excellent)"
    elif percentage >= 80:
        return "B (Good)"
    elif percentage >= 70:
        return "C (Satisfactory)"
    elif percentage >= 60:
        return "D (Needs Improvement)"
    else:
        return "F (Poor)"