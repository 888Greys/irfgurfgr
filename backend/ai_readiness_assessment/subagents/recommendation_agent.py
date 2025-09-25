"""
Recommendation Agent Sub-agent
Generates personalized recommendations based on assessment results
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
import json
from datetime import datetime


@tool
def generate_personalized_recommendations(assessment_results: str, business_info: str = None) -> str:
    """
    Generate personalized AI readiness recommendations based on assessment results using LLM.
    
    Args:
        assessment_results: JSON string with complete assessment results including scores and readiness level
        business_info: Optional JSON string with business information (industry, size, location, etc.)
    
    Returns:
        JSON string with personalized recommendations
    """
    try:
        from ..llm_config import llm_config, get_llm_response, parse_llm_json_response
        
        # Check if LLM is configured
        if not llm_config.is_configured():
            # Fallback to original implementation
            return _generate_recommendations_fallback(assessment_results, business_info)
        
        # Parse assessment results for validation
        try:
            results = json.loads(assessment_results)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for assessment results"})
        
        # Get LLM-powered recommendations
        llm_response = get_llm_response(
            "recommendation_agent",
            assessment_results=assessment_results,
            business_info=business_info or "{}"
        )
        
        # Parse LLM response
        recommendations_data = parse_llm_json_response(llm_response)
        
        # If LLM response is valid, return it
        if recommendations_data.get("success"):
            # Add metadata
            recommendations_data["assessment_summary"] = {
                "total_score": results.get("total_score", 0),
                "readiness_level": results.get("readiness_level", "Unknown"),
                "industry": json.loads(business_info or "{}").get("industry", "General")
            }
            recommendations_data["generated_at"] = datetime.now().isoformat()
            recommendations_data["llm_powered"] = True
            
            return json.dumps(recommendations_data, indent=2)
        
        # Fallback if LLM response is invalid
        return _generate_recommendations_fallback(assessment_results, business_info)
        
    except Exception as e:
        # Fallback on any error
        return _generate_recommendations_fallback(assessment_results, business_info)


def _generate_recommendations_fallback(assessment_results: str, business_info: str = None) -> str:
    """Fallback recommendation generation using original logic"""
    try:
        # Parse assessment results
        try:
            results = json.loads(assessment_results)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": "Invalid JSON format for assessment results"})
        
        # Parse business info if provided
        business_data = {}
        if business_info:
            try:
                business_data = json.loads(business_info)
            except json.JSONDecodeError:
                pass  # Continue without business info
        
        # Extract key information
        total_score = results.get("total_score", 0)
        readiness_level = results.get("readiness_level", "Unknown")
        section_scores = results.get("section_scores", {})
        industry = business_data.get("industry", "General")
        
        # Generate recommendations based on readiness level and scores
        recommendations = _generate_recommendations_by_level(total_score, readiness_level, section_scores, industry)
        
        result = {
            "success": True,
            "assessment_summary": {
                "total_score": total_score,
                "readiness_level": readiness_level,
                "industry": industry
            },
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat(),
            "llm_powered": False
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to generate recommendations: {str(e)}"})


def _generate_recommendations_by_level(total_score: int, readiness_level: str, section_scores: Dict, industry: str) -> Dict[str, Any]:
    """Generate recommendations based on readiness level"""
    
    # Get base recommendations for readiness level
    base_recommendations = _get_base_recommendations_by_level(readiness_level, total_score)
    
    # Analyze section-specific gaps and strengths
    section_analysis = _analyze_section_gaps(section_scores)
    
    # Generate prioritized actions based on gaps
    prioritized_actions = _prioritize_actions_by_gaps(section_analysis, readiness_level)
    
    # Create timeline estimates
    timeline_estimates = _create_timeline_estimates(readiness_level, section_analysis)
    
    # Add industry-specific recommendations
    industry_recommendations = _get_industry_specific_recommendations(industry, readiness_level)
    
    # Add Kenya-specific context
    kenya_context = _get_kenya_specific_recommendations(readiness_level, section_analysis)
    
    return {
        "readiness_level": readiness_level,
        "total_score": total_score,
        "priority_actions": prioritized_actions["high_priority"],
        "timeline": timeline_estimates["overall_timeline"],
        "immediate_actions": timeline_estimates["immediate_actions"],
        "short_term_goals": timeline_estimates["short_term_goals"],
        "long_term_vision": timeline_estimates["long_term_vision"],
        "kenya_specific_notes": kenya_context,
        "industry_recommendations": industry_recommendations,
        "section_analysis": section_analysis,
        "implementation_approach": base_recommendations["approach"],
        "success_metrics": _define_success_metrics(readiness_level),
        "risk_mitigation": _identify_risks_and_mitigation(section_analysis, readiness_level),
        "resource_requirements": _estimate_resource_requirements(readiness_level, section_analysis)
    }


def _get_base_recommendations_by_level(readiness_level: str, total_score: int) -> Dict[str, Any]:
    """Get base recommendations for each readiness level"""
    
    recommendations = {
        "Not Ready": {
            "approach": "Foundation Building",
            "focus": "Establish basic data and technology infrastructure",
            "timeline": "12-18 months",
            "key_areas": ["Data collection", "Basic digitization", "Staff training"]
        },
        "Foundation Building": {
            "approach": "Systematic Preparation",
            "focus": "Build core capabilities and processes",
            "timeline": "9-12 months",
            "key_areas": ["Data quality improvement", "Process documentation", "Technology upgrades"]
        },
        "Ready for Pilots": {
            "approach": "Pilot Implementation",
            "focus": "Start with low-risk AI pilot projects",
            "timeline": "6-9 months",
            "key_areas": ["Pilot project selection", "Team training", "Success measurement"]
        },
        "AI Ready": {
            "approach": "Strategic Implementation",
            "focus": "Scale successful pilots and expand AI use",
            "timeline": "3-6 months",
            "key_areas": ["Scaling pilots", "Advanced training", "ROI optimization"]
        },
        "AI Advanced": {
            "approach": "Innovation Leadership",
            "focus": "Lead AI innovation and share best practices",
            "timeline": "Ongoing",
            "key_areas": ["Innovation projects", "Industry leadership", "Knowledge sharing"]
        }
    }
    
    return recommendations.get(readiness_level, recommendations["Not Ready"])


def _analyze_section_gaps(section_scores: Dict) -> Dict[str, Any]:
    """Analyze gaps and strengths across assessment sections"""
    
    section_names = {
        "data_infrastructure": "Data Infrastructure & Quality",
        "technology_infrastructure": "Technology Infrastructure", 
        "human_resources": "Human Resources & Skills",
        "business_process": "Business Process Maturity",
        "strategic_financial": "Strategic & Financial Readiness",
        "regulatory_compliance": "Regulatory & Compliance Readiness"
    }
    
    analysis = {
        "strengths": [],
        "gaps": [],
        "critical_gaps": [],
        "section_details": {}
    }
    
    for section_key, section_name in section_names.items():
        score = section_scores.get(section_key, {}).get("section_total", 0)
        max_score = section_scores.get(section_key, {}).get("max_possible", 25)
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        analysis["section_details"][section_key] = {
            "name": section_name,
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "status": _get_section_status(percentage)
        }
        
        if percentage >= 80:
            analysis["strengths"].append(section_name)
        elif percentage >= 60:
            analysis["gaps"].append(section_name)
        else:
            analysis["critical_gaps"].append(section_name)
    
    return analysis


def _get_section_status(percentage: float) -> str:
    """Get status label for section score percentage"""
    if percentage >= 80:
        return "Strong"
    elif percentage >= 60:
        return "Adequate"
    elif percentage >= 40:
        return "Needs Improvement"
    else:
        return "Critical Gap"


def _prioritize_actions_by_gaps(section_analysis: Dict, readiness_level: str) -> Dict[str, List[str]]:
    """Prioritize actions based on identified gaps"""
    
    actions = {
        "high_priority": [],
        "medium_priority": [],
        "low_priority": []
    }
    
    # Critical gaps get high priority
    for gap in section_analysis["critical_gaps"]:
        if "Data Infrastructure" in gap:
            actions["high_priority"].extend([
                "Implement data collection and storage systems",
                "Establish data quality standards and processes",
                "Create data governance framework"
            ])
        elif "Technology Infrastructure" in gap:
            actions["high_priority"].extend([
                "Upgrade core technology systems",
                "Implement cloud infrastructure",
                "Establish cybersecurity measures"
            ])
        elif "Human Resources" in gap:
            actions["high_priority"].extend([
                "Hire or train AI-capable staff",
                "Develop AI literacy programs",
                "Create change management processes"
            ])
        elif "Business Process" in gap:
            actions["high_priority"].extend([
                "Document and standardize key processes",
                "Implement process automation where possible",
                "Establish performance measurement systems"
            ])
        elif "Strategic" in gap:
            actions["high_priority"].extend([
                "Develop AI strategy and roadmap",
                "Secure budget and resources for AI initiatives",
                "Establish AI governance structure"
            ])
        elif "Regulatory" in gap:
            actions["high_priority"].extend([
                "Ensure compliance with Kenya's Data Protection Act",
                "Develop AI ethics and governance policies",
                "Implement risk management frameworks"
            ])
    
    # Regular gaps get medium priority
    for gap in section_analysis["gaps"]:
        if "Data Infrastructure" in gap:
            actions["medium_priority"].extend([
                "Improve data analytics capabilities",
                "Enhance data integration processes"
            ])
        elif "Technology Infrastructure" in gap:
            actions["medium_priority"].extend([
                "Optimize existing technology stack",
                "Implement monitoring and maintenance processes"
            ])
        elif "Human Resources" in gap:
            actions["medium_priority"].extend([
                "Expand AI training programs",
                "Build internal AI expertise"
            ])
    
    # Strengths get low priority (optimization)
    for strength in section_analysis["strengths"]:
        actions["low_priority"].append(f"Optimize and leverage existing strength in {strength}")
    
    return actions


def _create_timeline_estimates(readiness_level: str, section_analysis: Dict) -> Dict[str, Any]:
    """Create timeline estimates for implementation approaches"""
    
    base_timelines = {
        "Not Ready": {"immediate": "1-3 months", "short_term": "3-12 months", "long_term": "12-24 months"},
        "Foundation Building": {"immediate": "1-2 months", "short_term": "2-9 months", "long_term": "9-18 months"},
        "Ready for Pilots": {"immediate": "2-4 weeks", "short_term": "1-6 months", "long_term": "6-12 months"},
        "AI Ready": {"immediate": "1-2 weeks", "short_term": "1-3 months", "long_term": "3-9 months"},
        "AI Advanced": {"immediate": "Ongoing", "short_term": "Ongoing", "long_term": "Ongoing"}
    }
    
    timeline = base_timelines.get(readiness_level, base_timelines["Not Ready"])
    
    # Adjust timeline based on critical gaps
    critical_gap_count = len(section_analysis["critical_gaps"])
    if critical_gap_count > 3:
        # Extend timelines for multiple critical gaps
        timeline_multiplier = 1.5
    elif critical_gap_count > 1:
        timeline_multiplier = 1.2
    else:
        timeline_multiplier = 1.0
    
    return {
        "overall_timeline": f"Expected completion in {timeline['long_term']}",
        "immediate_actions": [
            "Conduct detailed assessment of critical gaps",
            "Secure leadership commitment and resources",
            "Form AI implementation team"
        ],
        "short_term_goals": [
            "Address highest priority gaps identified in assessment",
            "Implement foundational systems and processes",
            "Begin staff training and capability building"
        ],
        "long_term_vision": [
            "Achieve target AI readiness level",
            "Successfully implement AI solutions",
            "Realize measurable business value from AI"
        ],
        "timeline_details": {
            "immediate": timeline["immediate"],
            "short_term": timeline["short_term"], 
            "long_term": timeline["long_term"],
            "adjustment_factor": timeline_multiplier
        }
    }


def _get_industry_specific_recommendations(industry: str, readiness_level: str) -> List[str]:
    """Get industry-specific recommendations"""
    
    industry_recommendations = {
        "Agriculture": [
            "Consider precision agriculture and crop monitoring AI solutions",
            "Explore weather prediction and yield optimization tools",
            "Investigate supply chain optimization for agricultural products"
        ],
        "Manufacturing": [
            "Implement predictive maintenance for equipment",
            "Consider quality control automation using computer vision",
            "Explore supply chain optimization and demand forecasting"
        ],
        "Financial Services": [
            "Ensure compliance with Central Bank of Kenya regulations",
            "Consider fraud detection and risk assessment AI tools",
            "Explore customer service automation and personalization"
        ],
        "Healthcare": [
            "Ensure compliance with health data protection regulations",
            "Consider diagnostic assistance and patient management tools",
            "Explore telemedicine and remote monitoring solutions"
        ],
        "Retail": [
            "Implement inventory management and demand forecasting",
            "Consider customer behavior analysis and personalization",
            "Explore automated customer service solutions"
        ],
        "Education": [
            "Consider personalized learning platforms",
            "Explore automated grading and assessment tools",
            "Investigate student performance analytics"
        ]
    }
    
    return industry_recommendations.get(industry, [
        "Focus on core business process automation",
        "Consider customer service and support AI tools",
        "Explore data analytics for business insights"
    ])


def _get_kenya_specific_recommendations(readiness_level: str, section_analysis: Dict) -> List[str]:
    """Get Kenya-specific recommendations and context"""
    
    kenya_recommendations = [
        "Ensure compliance with Kenya's Data Protection Act 2019",
        "Consider local data residency requirements",
        "Leverage Kenya's growing tech ecosystem and partnerships",
        "Explore government AI initiatives and support programs"
    ]
    
    # Add specific recommendations based on gaps
    if "Regulatory" in str(section_analysis["critical_gaps"]):
        kenya_recommendations.extend([
            "Consult with local legal experts on AI compliance",
            "Register with the Data Protection Commissioner if handling personal data",
            "Implement data subject rights and consent management"
        ])
    
    if "Technology Infrastructure" in str(section_analysis["critical_gaps"]):
        kenya_recommendations.extend([
            "Leverage Kenya's fiber optic infrastructure for cloud connectivity",
            "Consider partnerships with local tech companies",
            "Explore government digitization initiatives for support"
        ])
    
    if "Human Resources" in str(section_analysis["critical_gaps"]):
        kenya_recommendations.extend([
            "Partner with Kenyan universities for AI talent",
            "Leverage local training programs and bootcamps",
            "Consider remote work arrangements to access global talent"
        ])
    
    return kenya_recommendations


def _define_success_metrics(readiness_level: str) -> List[str]:
    """Define success metrics for AI implementation"""
    
    base_metrics = [
        "Improvement in assessment scores across all sections",
        "Successful completion of planned AI initiatives",
        "Measurable business value from AI implementations",
        "Staff AI literacy and capability improvements"
    ]
    
    level_specific_metrics = {
        "Not Ready": [
            "Establishment of basic data collection processes",
            "Completion of foundational technology upgrades",
            "Staff training completion rates"
        ],
        "Foundation Building": [
            "Data quality improvement metrics",
            "Process standardization completion",
            "Technology infrastructure reliability"
        ],
        "Ready for Pilots": [
            "Successful pilot project completion",
            "ROI from pilot implementations",
            "User adoption rates for AI tools"
        ],
        "AI Ready": [
            "Scaling of successful pilots",
            "Business process efficiency improvements",
            "Customer satisfaction improvements"
        ],
        "AI Advanced": [
            "Innovation project success rates",
            "Industry recognition and leadership",
            "Knowledge sharing and mentoring activities"
        ]
    }
    
    return base_metrics + level_specific_metrics.get(readiness_level, [])


def _identify_risks_and_mitigation(section_analysis: Dict, readiness_level: str) -> Dict[str, List[str]]:
    """Identify risks and mitigation strategies"""
    
    risks_and_mitigation = {
        "technical_risks": [],
        "business_risks": [],
        "compliance_risks": [],
        "mitigation_strategies": []
    }
    
    # Technical risks based on gaps
    if "Technology Infrastructure" in str(section_analysis["critical_gaps"]):
        risks_and_mitigation["technical_risks"].extend([
            "System integration challenges",
            "Data security vulnerabilities",
            "Technology scalability issues"
        ])
        risks_and_mitigation["mitigation_strategies"].extend([
            "Conduct thorough system architecture review",
            "Implement robust cybersecurity measures",
            "Plan for scalable cloud infrastructure"
        ])
    
    # Business risks
    if "Strategic" in str(section_analysis["critical_gaps"]):
        risks_and_mitigation["business_risks"].extend([
            "Lack of clear AI strategy",
            "Insufficient budget allocation",
            "Resistance to change"
        ])
        risks_and_mitigation["mitigation_strategies"].extend([
            "Develop comprehensive AI strategy with leadership buy-in",
            "Create detailed budget and ROI projections",
            "Implement change management and communication programs"
        ])
    
    # Compliance risks
    if "Regulatory" in str(section_analysis["critical_gaps"]):
        risks_and_mitigation["compliance_risks"].extend([
            "Data protection law violations",
            "AI ethics and bias issues",
            "Regulatory changes and updates"
        ])
        risks_and_mitigation["mitigation_strategies"].extend([
            "Regular compliance audits and legal reviews",
            "Implement AI ethics framework and bias testing",
            "Stay updated on regulatory changes and industry standards"
        ])
    
    return risks_and_mitigation


def _estimate_resource_requirements(readiness_level: str, section_analysis: Dict) -> Dict[str, Any]:
    """Estimate resource requirements for AI implementation"""
    
    base_requirements = {
        "Not Ready": {
            "budget_range": "KES 500K - 2M",
            "staff_time": "2-3 FTE for 12-18 months",
            "external_support": "High - consultants and training providers"
        },
        "Foundation Building": {
            "budget_range": "KES 1M - 5M", 
            "staff_time": "3-5 FTE for 9-12 months",
            "external_support": "Medium - specialized consultants"
        },
        "Ready for Pilots": {
            "budget_range": "KES 2M - 8M",
            "staff_time": "4-6 FTE for 6-9 months", 
            "external_support": "Medium - pilot implementation support"
        },
        "AI Ready": {
            "budget_range": "KES 5M - 15M",
            "staff_time": "5-8 FTE for 3-6 months",
            "external_support": "Low - occasional specialized support"
        },
        "AI Advanced": {
            "budget_range": "KES 10M+",
            "staff_time": "8+ FTE ongoing",
            "external_support": "Low - innovation partnerships"
        }
    }
    
    requirements = base_requirements.get(readiness_level, base_requirements["Not Ready"])
    
    # Adjust based on critical gaps
    critical_gap_count = len(section_analysis["critical_gaps"])
    if critical_gap_count > 3:
        requirements["adjustment_note"] = "Budget and timeline may increase due to multiple critical gaps"
    
    requirements["key_roles_needed"] = [
        "AI Project Manager",
        "Data Analyst/Scientist", 
        "Technical Lead/Developer",
        "Change Management Specialist"
    ]
    
    requirements["training_requirements"] = [
        "Leadership AI awareness training",
        "Technical staff AI/ML training",
        "General staff digital literacy training"
    ]
    
    return requirements


# Additional tool for getting recommendation templates
@tool
def get_recommendation_templates(readiness_level: str) -> str:
    """
    Get recommendation templates for a specific readiness level.
    
    Args:
        readiness_level: The AI readiness level (Not Ready, Foundation Building, etc.)
    
    Returns:
        JSON string with recommendation templates
    """
    try:
        templates = {
            "Not Ready": {
                "priority_focus": "Foundation Building",
                "key_message": "Focus on establishing basic data and technology infrastructure before pursuing AI initiatives.",
                "action_categories": {
                    "immediate": ["Data audit", "Technology assessment", "Leadership alignment"],
                    "short_term": ["Infrastructure upgrades", "Process documentation", "Staff training"],
                    "long_term": ["AI strategy development", "Pilot project planning", "Capability building"]
                }
            },
            "Foundation Building": {
                "priority_focus": "Systematic Preparation", 
                "key_message": "Build core capabilities systematically while preparing for AI pilot projects.",
                "action_categories": {
                    "immediate": ["Gap analysis", "Resource planning", "Team formation"],
                    "short_term": ["Process improvements", "Technology upgrades", "Skills development"],
                    "long_term": ["Pilot preparation", "Advanced training", "Strategy refinement"]
                }
            },
            "Ready for Pilots": {
                "priority_focus": "Pilot Implementation",
                "key_message": "Start with carefully selected, low-risk AI pilot projects to build experience and demonstrate value.",
                "action_categories": {
                    "immediate": ["Pilot selection", "Team preparation", "Success metrics definition"],
                    "short_term": ["Pilot execution", "Performance monitoring", "Learning capture"],
                    "long_term": ["Pilot scaling", "Additional use cases", "Capability expansion"]
                }
            },
            "AI Ready": {
                "priority_focus": "Strategic Implementation",
                "key_message": "Scale successful pilots and expand AI use across the organization strategically.",
                "action_categories": {
                    "immediate": ["Scaling strategy", "Resource allocation", "Performance optimization"],
                    "short_term": ["Implementation expansion", "Advanced training", "ROI optimization"],
                    "long_term": ["Innovation projects", "Industry leadership", "Ecosystem development"]
                }
            },
            "AI Advanced": {
                "priority_focus": "Innovation Leadership",
                "key_message": "Lead AI innovation in your industry and share best practices with the broader ecosystem.",
                "action_categories": {
                    "immediate": ["Innovation planning", "Partnership development", "Knowledge sharing"],
                    "short_term": ["Advanced projects", "Industry collaboration", "Thought leadership"],
                    "long_term": ["Ecosystem leadership", "Innovation mentoring", "Future technology adoption"]
                }
            }
        }
        
        template = templates.get(readiness_level, templates["Not Ready"])
        return json.dumps(template, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get templates: {str(e)}"})


# Tool for timeline estimation
@tool  
def estimate_implementation_timeline(assessment_results: str, priority_actions: str) -> str:
    """
    Estimate implementation timeline based on assessment results and priority actions.
    
    Args:
        assessment_results: JSON string with assessment results
        priority_actions: JSON string with prioritized actions
    
    Returns:
        JSON string with detailed timeline estimates
    """
    try:
        results = json.loads(assessment_results)
        actions = json.loads(priority_actions)
        
        readiness_level = results.get("readiness_level", "Not Ready")
        critical_gaps = len(results.get("section_scores", {}).keys()) - len([s for s in results.get("section_scores", {}).values() if s.get("section_total", 0) > 15])
        
        # Base timeline estimates
        base_timelines = {
            "Not Ready": {"total": "18-24 months", "phases": 4},
            "Foundation Building": {"total": "12-18 months", "phases": 3}, 
            "Ready for Pilots": {"total": "9-12 months", "phases": 3},
            "AI Ready": {"total": "6-9 months", "phases": 2},
            "AI Advanced": {"total": "3-6 months", "phases": 2}
        }
        
        base = base_timelines.get(readiness_level, base_timelines["Not Ready"])
        
        # Adjust for complexity
        complexity_multiplier = 1.0
        if critical_gaps > 4:
            complexity_multiplier = 1.5
        elif critical_gaps > 2:
            complexity_multiplier = 1.2
        
        # Create detailed timeline
        timeline = {
            "overall_estimate": base["total"],
            "complexity_adjustment": complexity_multiplier,
            "phase_breakdown": _create_phase_breakdown(readiness_level, base["phases"]),
            "critical_path_items": actions.get("high_priority", [])[:5],
            "risk_factors": _identify_timeline_risks(critical_gaps, readiness_level),
            "success_factors": _identify_success_factors(readiness_level)
        }
        
        return json.dumps(timeline, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to estimate timeline: {str(e)}"})


def _create_phase_breakdown(readiness_level: str, num_phases: int) -> List[Dict]:
    """Create detailed phase breakdown for implementation"""
    
    phase_templates = {
        "Not Ready": [
            {"phase": 1, "name": "Foundation Assessment", "duration": "2-3 months", "focus": "Data and technology audit"},
            {"phase": 2, "name": "Infrastructure Building", "duration": "6-9 months", "focus": "Core system upgrades"},
            {"phase": 3, "name": "Capability Development", "duration": "6-9 months", "focus": "Skills and process development"},
            {"phase": 4, "name": "AI Readiness Validation", "duration": "3-6 months", "focus": "Pilot preparation"}
        ],
        "Foundation Building": [
            {"phase": 1, "name": "Gap Remediation", "duration": "4-6 months", "focus": "Address critical gaps"},
            {"phase": 2, "name": "Capability Building", "duration": "4-6 months", "focus": "Build AI capabilities"},
            {"phase": 3, "name": "Pilot Preparation", "duration": "4-6 months", "focus": "Prepare for AI pilots"}
        ],
        "Ready for Pilots": [
            {"phase": 1, "name": "Pilot Planning", "duration": "1-2 months", "focus": "Select and plan pilots"},
            {"phase": 2, "name": "Pilot Execution", "duration": "4-6 months", "focus": "Execute pilot projects"},
            {"phase": 3, "name": "Scaling Preparation", "duration": "4-6 months", "focus": "Prepare for scaling"}
        ],
        "AI Ready": [
            {"phase": 1, "name": "Scaling Strategy", "duration": "2-3 months", "focus": "Plan scaling approach"},
            {"phase": 2, "name": "Implementation Scaling", "duration": "4-6 months", "focus": "Scale successful pilots"}
        ],
        "AI Advanced": [
            {"phase": 1, "name": "Innovation Planning", "duration": "1-2 months", "focus": "Plan innovation projects"},
            {"phase": 2, "name": "Innovation Execution", "duration": "2-4 months", "focus": "Execute innovation initiatives"}
        ]
    }
    
    return phase_templates.get(readiness_level, phase_templates["Not Ready"])[:num_phases]


def _identify_timeline_risks(critical_gaps: int, readiness_level: str) -> List[str]:
    """Identify factors that could extend timeline"""
    
    risks = []
    
    if critical_gaps > 4:
        risks.append("Multiple critical gaps may require sequential rather than parallel addressing")
    
    if critical_gaps > 2:
        risks.append("Significant infrastructure upgrades may take longer than estimated")
    
    if readiness_level in ["Not Ready", "Foundation Building"]:
        risks.extend([
            "Change management challenges may slow adoption",
            "Budget constraints may limit parallel initiatives",
            "Skills gaps may require extensive training periods"
        ])
    
    risks.extend([
        "External vendor dependencies could cause delays",
        "Regulatory compliance requirements may add complexity",
        "Integration challenges with existing systems"
    ])
    
    return risks


def _identify_success_factors(readiness_level: str) -> List[str]:
    """Identify factors that could accelerate timeline"""
    
    factors = [
        "Strong leadership commitment and support",
        "Dedicated project team with clear accountability",
        "Adequate budget and resource allocation",
        "Effective change management and communication"
    ]
    
    if readiness_level in ["AI Ready", "AI Advanced"]:
        factors.extend([
            "Existing AI experience and capabilities",
            "Strong technology infrastructure foundation",
            "Data-driven culture and processes"
        ])
    
    return factors