"""
Report Generator Agent Sub-agent
Generates comprehensive assessment reports with visual representations
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
import json
from datetime import datetime


@tool
def generate_comprehensive_report(assessment_results: str, recommendations: str, business_info: str = None) -> str:
    """
    Generate a comprehensive assessment report with all sections.
    
    Args:
        assessment_results: JSON string with complete assessment results
        recommendations: JSON string with personalized recommendations
        business_info: Optional JSON string with business information
    
    Returns:
        JSON string with complete formatted report
    """
    try:
        # Parse input data
        results = json.loads(assessment_results)
        recs = json.loads(recommendations)
        business_data = json.loads(business_info) if business_info else {}
        
        # Generate report sections
        report = {
            "report_metadata": _create_report_metadata(business_data),
            "executive_summary": _create_executive_summary(results, recs),
            "assessment_overview": _create_assessment_overview(results),
            "section_analysis": _create_section_analysis(results),
            "readiness_level_details": _create_readiness_details(results, recs),
            "immediate_actions": _extract_immediate_actions(recs),
            "short_term_goals": _extract_short_term_goals(recs),
            "long_term_vision": _extract_long_term_vision(recs),
            "implementation_roadmap": _create_implementation_roadmap(recs),
            "resource_requirements": _extract_resource_requirements(recs),
            "risk_assessment": _extract_risk_assessment(recs),
            "success_metrics": _extract_success_metrics(recs),
            "kenya_specific_guidance": _extract_kenya_guidance(recs),
            "visual_representations": _create_visual_data(results),
            "appendices": _create_appendices(results, recs)
        }
        
        return json.dumps({
            "success": True,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to generate report: {str(e)}"})


def _create_report_metadata(business_data: Dict) -> Dict[str, Any]:
    """Create report metadata section"""
    return {
        "report_title": "AI Readiness Assessment Report",
        "organization": business_data.get("organization_name", "Organization"),
        "industry": business_data.get("industry", "Not specified"),
        "assessment_date": datetime.now().strftime("%B %d, %Y"),
        "report_version": "1.0",
        "prepared_for": business_data.get("contact_person", "Leadership Team"),
        "location": business_data.get("location", "Kenya")
    }


def _create_executive_summary(results: Dict, recommendations: Dict) -> Dict[str, Any]:
    """Create executive summary section"""
    total_score = results.get("total_score", 0)
    readiness_level = results.get("readiness_level", "Unknown")
    
    # Calculate percentage score
    max_possible = sum(section.get("max_possible", 25) for section in results.get("section_scores", {}).values())
    percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
    
    return {
        "overall_readiness": readiness_level,
        "total_score": f"{total_score}/{max_possible} ({percentage:.1f}%)",
        "key_findings": [
            f"Your organization is currently at the '{readiness_level}' level of AI readiness",
            f"Assessment score of {percentage:.1f}% indicates specific areas for improvement",
            f"Primary focus should be on {recommendations.get('recommendations', {}).get('implementation_approach', 'foundation building')}"
        ],
        "critical_priorities": recommendations.get("recommendations", {}).get("priority_actions", [])[:3],
        "estimated_timeline": recommendations.get("recommendations", {}).get("timeline", "Timeline not available"),
        "investment_level": _determine_investment_level(readiness_level, percentage)
    }


def _determine_investment_level(readiness_level: str, percentage: float) -> str:
    """Determine investment level based on readiness"""
    if readiness_level in ["Not Ready", "Foundation Building"]:
        return "High - Significant infrastructure and capability building required"
    elif readiness_level == "Ready for Pilots":
        return "Medium - Focused investment in pilot projects and training"
    elif readiness_level == "AI Ready":
        return "Medium-Low - Strategic scaling and optimization investment"
    else:
        return "Low - Innovation and leadership investment"


def _create_assessment_overview(results: Dict) -> Dict[str, Any]:
    """Create assessment overview section"""
    section_scores = results.get("section_scores", {})
    
    return {
        "total_questions": sum(len(section.get("responses", {})) for section in section_scores.values()),
        "sections_completed": len(section_scores),
        "overall_score": results.get("total_score", 0),
        "readiness_level": results.get("readiness_level", "Unknown"),
        "assessment_completion": "100%",
        "score_distribution": _calculate_score_distribution(section_scores)
    }


def _calculate_score_distribution(section_scores: Dict) -> Dict[str, int]:
    """Calculate score distribution across sections"""
    distribution = {"Excellent (20-25)": 0, "Good (15-19)": 0, "Fair (10-14)": 0, "Poor (5-9)": 0, "Critical (0-4)": 0}
    
    for section in section_scores.values():
        score = section.get("section_total", 0)
        if score >= 20:
            distribution["Excellent (20-25)"] += 1
        elif score >= 15:
            distribution["Good (15-19)"] += 1
        elif score >= 10:
            distribution["Fair (10-14)"] += 1
        elif score >= 5:
            distribution["Poor (5-9)"] += 1
        else:
            distribution["Critical (0-4)"] += 1
    
    return distribution


def _create_section_analysis(results: Dict) -> List[Dict[str, Any]]:
    """Create detailed section analysis"""
    section_names = {
        "data_infrastructure": "Data Infrastructure & Quality",
        "technology_infrastructure": "Technology Infrastructure",
        "human_resources": "Human Resources & Skills", 
        "business_process": "Business Process Maturity",
        "strategic_financial": "Strategic & Financial Readiness",
        "regulatory_compliance": "Regulatory & Compliance Readiness"
    }
    
    analysis = []
    section_scores = results.get("section_scores", {})
    
    for section_key, section_name in section_names.items():
        if section_key in section_scores:
            section_data = section_scores[section_key]
            score = section_data.get("section_total", 0)
            max_score = section_data.get("max_possible", 25)
            percentage = (score / max_score * 100) if max_score > 0 else 0
            
            analysis.append({
                "section_name": section_name,
                "score": f"{score}/{max_score}",
                "percentage": f"{percentage:.1f}%",
                "status": _get_section_status_label(percentage),
                "key_strengths": _identify_section_strengths(section_data, section_key),
                "improvement_areas": _identify_improvement_areas(section_data, section_key),
                "priority_level": _determine_section_priority(percentage)
            })
    
    return sorted(analysis, key=lambda x: float(x["percentage"].rstrip("%")))


def _get_section_status_label(percentage: float) -> str:
    """Get status label for section percentage"""
    if percentage >= 80:
        return "Excellent"
    elif percentage >= 60:
        return "Good"
    elif percentage >= 40:
        return "Needs Improvement"
    else:
        return "Critical Gap"


def _identify_section_strengths(section_data: Dict, section_key: str) -> List[str]:
    """Identify strengths within a section"""
    strengths_map = {
        "data_infrastructure": [
            "Data collection processes",
            "Data quality standards",
            "Data governance framework"
        ],
        "technology_infrastructure": [
            "Cloud infrastructure",
            "System integration capabilities", 
            "Cybersecurity measures"
        ],
        "human_resources": [
            "Technical expertise",
            "AI literacy levels",
            "Change management readiness"
        ],
        "business_process": [
            "Process documentation",
            "Performance measurement",
            "Automation readiness"
        ],
        "strategic_financial": [
            "AI strategy clarity",
            "Budget allocation",
            "Leadership commitment"
        ],
        "regulatory_compliance": [
            "Data protection compliance",
            "Risk management framework",
            "Ethics and governance"
        ]
    }
    
    # Return generic strengths for the section
    return strengths_map.get(section_key, ["General capabilities in this area"])


def _identify_improvement_areas(section_data: Dict, section_key: str) -> List[str]:
    """Identify improvement areas within a section"""
    improvement_map = {
        "data_infrastructure": [
            "Data integration processes",
            "Analytics capabilities",
            "Data storage optimization"
        ],
        "technology_infrastructure": [
            "System modernization",
            "Scalability planning",
            "Integration architecture"
        ],
        "human_resources": [
            "AI skills development",
            "Training programs",
            "Talent acquisition"
        ],
        "business_process": [
            "Process standardization",
            "Automation implementation",
            "Performance optimization"
        ],
        "strategic_financial": [
            "ROI measurement",
            "Resource planning",
            "Strategic alignment"
        ],
        "regulatory_compliance": [
            "Compliance monitoring",
            "Policy implementation",
            "Risk assessment"
        ]
    }
    
    return improvement_map.get(section_key, ["General improvements needed"])


def _determine_section_priority(percentage: float) -> str:
    """Determine priority level for section"""
    if percentage < 40:
        return "Critical Priority"
    elif percentage < 60:
        return "High Priority"
    elif percentage < 80:
        return "Medium Priority"
    else:
        return "Low Priority"


def _create_readiness_details(results: Dict, recommendations: Dict) -> Dict[str, Any]:
    """Create readiness level details section"""
    readiness_level = results.get("readiness_level", "Unknown")
    
    level_descriptions = {
        "Not Ready": {
            "description": "Your organization needs foundational work before pursuing AI initiatives",
            "characteristics": [
                "Limited data infrastructure",
                "Basic technology capabilities",
                "Minimal AI awareness",
                "Informal processes"
            ],
            "next_level": "Foundation Building"
        },
        "Foundation Building": {
            "description": "Your organization is building the necessary foundations for AI adoption",
            "characteristics": [
                "Developing data capabilities",
                "Improving technology infrastructure",
                "Growing AI awareness",
                "Formalizing processes"
            ],
            "next_level": "Ready for Pilots"
        },
        "Ready for Pilots": {
            "description": "Your organization is ready to begin AI pilot projects",
            "characteristics": [
                "Solid data foundation",
                "Adequate technology infrastructure",
                "Basic AI skills present",
                "Structured processes"
            ],
            "next_level": "AI Ready"
        },
        "AI Ready": {
            "description": "Your organization can successfully implement and scale AI solutions",
            "characteristics": [
                "Strong data capabilities",
                "Modern technology stack",
                "AI-skilled workforce",
                "Optimized processes"
            ],
            "next_level": "AI Advanced"
        },
        "AI Advanced": {
            "description": "Your organization is an AI leader with advanced capabilities",
            "characteristics": [
                "Cutting-edge data infrastructure",
                "Advanced AI technologies",
                "AI expertise throughout organization",
                "AI-driven processes"
            ],
            "next_level": "Continued Innovation"
        }
    }
    
    details = level_descriptions.get(readiness_level, level_descriptions["Not Ready"])
    
    return {
        "current_level": readiness_level,
        "level_description": details["description"],
        "key_characteristics": details["characteristics"],
        "path_to_next_level": details["next_level"],
        "estimated_time_to_next_level": recommendations.get("recommendations", {}).get("timeline", "Not available"),
        "success_indicators": _get_level_success_indicators(readiness_level)
    }


def _get_level_success_indicators(readiness_level: str) -> List[str]:
    """Get success indicators for current readiness level"""
    indicators = {
        "Not Ready": [
            "Completion of data infrastructure assessment",
            "Technology upgrade planning initiated",
            "AI awareness training completed"
        ],
        "Foundation Building": [
            "Data quality standards implemented",
            "Core technology systems upgraded",
            "AI strategy document created"
        ],
        "Ready for Pilots": [
            "First AI pilot project launched",
            "Pilot success metrics defined",
            "AI team established"
        ],
        "AI Ready": [
            "Multiple AI solutions in production",
            "Measurable business value achieved",
            "AI governance framework operational"
        ],
        "AI Advanced": [
            "Industry-leading AI implementations",
            "AI innovation projects active",
            "Knowledge sharing with ecosystem"
        ]
    }
    
    return indicators.get(readiness_level, indicators["Not Ready"])


def _extract_immediate_actions(recommendations: Dict) -> List[Dict[str, Any]]:
    """Extract immediate actions from recommendations"""
    immediate = recommendations.get("recommendations", {}).get("immediate_actions", [])
    
    actions = []
    for i, action in enumerate(immediate[:5], 1):  # Limit to top 5
        actions.append({
            "priority": i,
            "action": action,
            "timeline": "1-4 weeks",
            "owner": "Leadership Team",
            "resources_needed": "Internal resources",
            "success_criteria": f"Completion of {action.lower()}"
        })
    
    return actions


def _extract_short_term_goals(recommendations: Dict) -> List[Dict[str, Any]]:
    """Extract short-term goals from recommendations"""
    short_term = recommendations.get("recommendations", {}).get("short_term_goals", [])
    
    goals = []
    for i, goal in enumerate(short_term[:5], 1):
        goals.append({
            "goal": goal,
            "timeline": "1-6 months",
            "success_metrics": f"Measurable progress in {goal.lower()}",
            "dependencies": "Completion of immediate actions",
            "estimated_effort": "Medium",
            "expected_outcome": f"Improved capability in {goal.lower()}"
        })
    
    return goals


def _extract_long_term_vision(recommendations: Dict) -> List[Dict[str, Any]]:
    """Extract long-term vision from recommendations"""
    long_term = recommendations.get("recommendations", {}).get("long_term_vision", [])
    
    vision = []
    for i, item in enumerate(long_term[:3], 1):
        vision.append({
            "vision_element": item,
            "timeline": "6-24 months",
            "strategic_impact": "High",
            "success_indicators": f"Achievement of {item.lower()}",
            "business_value": "Significant competitive advantage",
            "sustainability": "Long-term organizational capability"
        })
    
    return vision


def _create_implementation_roadmap(recommendations: Dict) -> Dict[str, Any]:
    """Create implementation roadmap"""
    recs = recommendations.get("recommendations", {})
    
    return {
        "overall_timeline": recs.get("timeline", "Not specified"),
        "implementation_approach": recs.get("implementation_approach", "Systematic approach"),
        "phases": [
            {
                "phase": 1,
                "name": "Foundation & Planning",
                "duration": "1-3 months",
                "key_activities": recs.get("immediate_actions", [])[:3],
                "deliverables": ["Assessment completion", "Strategy document", "Team formation"]
            },
            {
                "phase": 2, 
                "name": "Capability Building",
                "duration": "3-9 months",
                "key_activities": recs.get("short_term_goals", [])[:3],
                "deliverables": ["Infrastructure upgrades", "Training completion", "Process improvements"]
            },
            {
                "phase": 3,
                "name": "Implementation & Scaling",
                "duration": "6-18 months", 
                "key_activities": recs.get("long_term_vision", [])[:3],
                "deliverables": ["AI solutions deployed", "Business value realized", "Continuous improvement"]
            }
        ],
        "critical_milestones": [
            "Leadership commitment secured",
            "Core team established",
            "First pilot launched",
            "Measurable ROI achieved"
        ]
    }


def _extract_resource_requirements(recommendations: Dict) -> Dict[str, Any]:
    """Extract resource requirements"""
    resources = recommendations.get("recommendations", {}).get("resource_requirements", {})
    
    return {
        "budget_estimate": resources.get("budget_range", "To be determined"),
        "staffing_needs": resources.get("staff_time", "To be determined"),
        "external_support": resources.get("external_support", "To be determined"),
        "key_roles": resources.get("key_roles_needed", []),
        "training_requirements": resources.get("training_requirements", []),
        "technology_investments": [
            "Cloud infrastructure",
            "Data management systems",
            "AI/ML platforms",
            "Security solutions"
        ],
        "ongoing_costs": "10-20% of initial investment annually"
    }


def _extract_risk_assessment(recommendations: Dict) -> Dict[str, Any]:
    """Extract risk assessment"""
    risks = recommendations.get("recommendations", {}).get("risk_mitigation", {})
    
    return {
        "technical_risks": risks.get("technical_risks", []),
        "business_risks": risks.get("business_risks", []),
        "compliance_risks": risks.get("compliance_risks", []),
        "mitigation_strategies": risks.get("mitigation_strategies", []),
        "risk_monitoring": [
            "Regular progress reviews",
            "Stakeholder feedback sessions",
            "Technical performance monitoring",
            "Compliance audits"
        ]
    }


def _extract_success_metrics(recommendations: Dict) -> List[Dict[str, Any]]:
    """Extract success metrics"""
    metrics = recommendations.get("recommendations", {}).get("success_metrics", [])
    
    formatted_metrics = []
    for metric in metrics[:8]:  # Limit to 8 metrics
        formatted_metrics.append({
            "metric": metric,
            "measurement_method": "Quantitative assessment",
            "target": "Improvement over baseline",
            "frequency": "Monthly review",
            "owner": "Project team"
        })
    
    return formatted_metrics


def _extract_kenya_guidance(recommendations: Dict) -> Dict[str, Any]:
    """Extract Kenya-specific guidance"""
    kenya_notes = recommendations.get("recommendations", {}).get("kenya_specific_notes", [])
    
    return {
        "regulatory_considerations": [
            "Kenya Data Protection Act 2019 compliance",
            "Central Bank of Kenya regulations (if applicable)",
            "Industry-specific regulatory requirements"
        ],
        "local_opportunities": [
            "Government digitization initiatives",
            "Local tech ecosystem partnerships",
            "Regional market expansion potential"
        ],
        "specific_recommendations": kenya_notes,
        "local_resources": [
            "Kenyan universities for talent",
            "Local training providers",
            "Government support programs",
            "Tech hubs and incubators"
        ]
    }


def _create_visual_data(results: Dict) -> Dict[str, Any]:
    """Create data for visual representations"""
    section_scores = results.get("section_scores", {})
    
    # Prepare data for charts and graphs
    visual_data = {
        "readiness_radar_chart": _create_radar_chart_data(section_scores),
        "score_bar_chart": _create_bar_chart_data(section_scores),
        "readiness_gauge": _create_gauge_data(results),
        "progress_timeline": _create_timeline_data(results),
        "comparison_matrix": _create_comparison_data(section_scores)
    }
    
    return visual_data


def _create_radar_chart_data(section_scores: Dict) -> Dict[str, Any]:
    """Create radar chart data for section scores"""
    sections = {
        "data_infrastructure": "Data Infrastructure",
        "technology_infrastructure": "Technology",
        "human_resources": "Human Resources", 
        "business_process": "Business Process",
        "strategic_financial": "Strategy & Finance",
        "regulatory_compliance": "Compliance"
    }
    
    chart_data = {
        "labels": [],
        "scores": [],
        "max_scores": []
    }
    
    for key, label in sections.items():
        if key in section_scores:
            chart_data["labels"].append(label)
            chart_data["scores"].append(section_scores[key].get("section_total", 0))
            chart_data["max_scores"].append(section_scores[key].get("max_possible", 25))
    
    return chart_data


def _create_bar_chart_data(section_scores: Dict) -> Dict[str, Any]:
    """Create bar chart data for section comparison"""
    sections = {
        "data_infrastructure": "Data Infrastructure",
        "technology_infrastructure": "Technology",
        "human_resources": "Human Resources",
        "business_process": "Business Process", 
        "strategic_financial": "Strategy & Finance",
        "regulatory_compliance": "Compliance"
    }
    
    chart_data = {
        "categories": [],
        "current_scores": [],
        "percentages": [],
        "status_colors": []
    }
    
    for key, label in sections.items():
        if key in section_scores:
            score = section_scores[key].get("section_total", 0)
            max_score = section_scores[key].get("max_possible", 25)
            percentage = (score / max_score * 100) if max_score > 0 else 0
            
            chart_data["categories"].append(label)
            chart_data["current_scores"].append(score)
            chart_data["percentages"].append(percentage)
            chart_data["status_colors"].append(_get_status_color(percentage))
    
    return chart_data


def _get_status_color(percentage: float) -> str:
    """Get color code for status visualization"""
    if percentage >= 80:
        return "#22c55e"  # Green
    elif percentage >= 60:
        return "#eab308"  # Yellow
    elif percentage >= 40:
        return "#f97316"  # Orange
    else:
        return "#ef4444"  # Red


def _create_gauge_data(results: Dict) -> Dict[str, Any]:
    """Create gauge chart data for overall readiness"""
    total_score = results.get("total_score", 0)
    max_possible = sum(section.get("max_possible", 25) for section in results.get("section_scores", {}).values())
    percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
    
    return {
        "current_score": total_score,
        "max_score": max_possible,
        "percentage": percentage,
        "readiness_level": results.get("readiness_level", "Unknown"),
        "gauge_color": _get_status_color(percentage),
        "level_thresholds": {
            "Not Ready": 0,
            "Foundation Building": 25,
            "Ready for Pilots": 50,
            "AI Ready": 75,
            "AI Advanced": 90
        }
    }


def _create_timeline_data(results: Dict) -> Dict[str, Any]:
    """Create timeline visualization data"""
    readiness_level = results.get("readiness_level", "Not Ready")
    
    levels = ["Not Ready", "Foundation Building", "Ready for Pilots", "AI Ready", "AI Advanced"]
    current_index = levels.index(readiness_level) if readiness_level in levels else 0
    
    timeline_data = {
        "current_position": current_index,
        "levels": []
    }
    
    for i, level in enumerate(levels):
        timeline_data["levels"].append({
            "name": level,
            "position": i,
            "status": "completed" if i <= current_index else "future",
            "description": f"Level {i+1}: {level}"
        })
    
    return timeline_data


def _create_comparison_data(section_scores: Dict) -> Dict[str, Any]:
    """Create comparison matrix data"""
    sections = list(section_scores.keys())
    
    comparison_data = {
        "sections": sections,
        "scores": [],
        "benchmarks": []
    }
    
    for section in sections:
        score = section_scores[section].get("section_total", 0)
        max_score = section_scores[section].get("max_possible", 25)
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        comparison_data["scores"].append(percentage)
        comparison_data["benchmarks"].append(70)  # Industry benchmark
    
    return comparison_data


def _create_appendices(results: Dict, recommendations: Dict) -> Dict[str, Any]:
    """Create appendices section"""
    return {
        "assessment_methodology": {
            "description": "This assessment uses a comprehensive 6-section framework",
            "scoring_system": "Each question scored 1-5, sections weighted equally",
            "readiness_levels": "Five levels from 'Not Ready' to 'AI Advanced'",
            "validation": "Responses validated for consistency and completeness"
        },
        "detailed_scores": results.get("section_scores", {}),
        "recommendation_details": recommendations.get("recommendations", {}),
        "glossary": _create_glossary(),
        "resources": _create_resource_list(),
        "contact_information": {
            "support_email": "support@aireadiness.ke",
            "website": "www.aireadiness.ke",
            "phone": "+254-XXX-XXXX"
        }
    }


def _create_glossary() -> Dict[str, str]:
    """Create glossary of terms"""
    return {
        "AI Readiness": "An organization's capability to successfully adopt and implement artificial intelligence solutions",
        "Data Infrastructure": "Systems and processes for collecting, storing, and managing organizational data",
        "Machine Learning": "A subset of AI that enables systems to learn and improve from experience",
        "Digital Transformation": "Integration of digital technology into all areas of business operations",
        "Data Governance": "Framework for managing data availability, usability, integrity, and security",
        "Change Management": "Structured approach to transitioning individuals and organizations to new processes"
    }


def _create_resource_list() -> List[Dict[str, str]]:
    """Create list of helpful resources"""
    return [
        {
            "title": "Kenya Data Protection Act 2019",
            "type": "Legal Document",
            "url": "https://www.odpc.go.ke/dpa-2019/",
            "description": "Official data protection legislation"
        },
        {
            "title": "AI for Development in Kenya",
            "type": "Research Report", 
            "url": "https://www.example.com/ai-kenya",
            "description": "Comprehensive study on AI adoption in Kenya"
        },
        {
            "title": "Digital Economy Blueprint",
            "type": "Government Policy",
            "url": "https://www.ict.go.ke/",
            "description": "Kenya's digital transformation strategy"
        }
    ]


@tool
def export_report_format(report_data: str, format_type: str = "json") -> str:
    """
    Export report in different formats.
    
    Args:
        report_data: JSON string with complete report data
        format_type: Export format (json, markdown, html, pdf_data)
    
    Returns:
        Formatted report string or JSON with export data
    """
    try:
        report = json.loads(report_data)
        
        if format_type == "markdown":
            return _export_markdown(report)
        elif format_type == "html":
            return _export_html(report)
        elif format_type == "pdf_data":
            return _export_pdf_data(report)
        else:
            return json.dumps(report, indent=2)
            
    except Exception as e:
        return json.dumps({"success": False, "error": f"Export failed: {str(e)}"})


def _export_markdown(report: Dict) -> str:
    """Export report as Markdown"""
    if not report.get("success"):
        return "# Error\nFailed to generate report"
    
    report_data = report["report"]
    metadata = report_data["report_metadata"]
    summary = report_data["executive_summary"]
    
    markdown = f"""# {metadata["report_title"]}

**Organization:** {metadata["organization"]}  
**Industry:** {metadata["industry"]}  
**Assessment Date:** {metadata["assessment_date"]}  
**Location:** {metadata["location"]}

## Executive Summary

**Overall Readiness Level:** {summary["overall_readiness"]}  
**Total Score:** {summary["total_score"]}  
**Estimated Timeline:** {summary["estimated_timeline"]}

### Key Findings
"""
    
    for finding in summary["key_findings"]:
        markdown += f"- {finding}\n"
    
    markdown += "\n### Critical Priorities\n"
    for i, priority in enumerate(summary["critical_priorities"], 1):
        markdown += f"{i}. {priority}\n"
    
    # Add section analysis
    markdown += "\n## Section Analysis\n"
    for section in report_data["section_analysis"]:
        markdown += f"\n### {section['section_name']}\n"
        markdown += f"**Score:** {section['score']} ({section['percentage']}) - {section['status']}\n"
        markdown += f"**Priority:** {section['priority_level']}\n"
    
    # Add immediate actions
    markdown += "\n## Immediate Actions\n"
    for action in report_data["immediate_actions"]:
        markdown += f"{action['priority']}. {action['action']} (Timeline: {action['timeline']})\n"
    
    return markdown


def _export_html(report: Dict) -> str:
    """Export report as HTML"""
    if not report.get("success"):
        return "<html><body><h1>Error</h1><p>Failed to generate report</p></body></html>"
    
    report_data = report["report"]
    metadata = report_data["report_metadata"]
    summary = report_data["executive_summary"]
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{metadata["report_title"]}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .priority {{ background-color: #fff3cd; padding: 10px; border-radius: 3px; }}
        .score {{ font-weight: bold; color: #007bff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{metadata["report_title"]}</h1>
        <p><strong>Organization:</strong> {metadata["organization"]}</p>
        <p><strong>Industry:</strong> {metadata["industry"]}</p>
        <p><strong>Assessment Date:</strong> {metadata["assessment_date"]}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <p><strong>Overall Readiness Level:</strong> <span class="score">{summary["overall_readiness"]}</span></p>
        <p><strong>Total Score:</strong> {summary["total_score"]}</p>
        <p><strong>Estimated Timeline:</strong> {summary["estimated_timeline"]}</p>
        
        <h3>Key Findings</h3>
        <ul>
"""
    
    for finding in summary["key_findings"]:
        html += f"            <li>{finding}</li>\n"
    
    html += """        </ul>
        
        <h3>Critical Priorities</h3>
        <ol>
"""
    
    for priority in summary["critical_priorities"]:
        html += f'            <li class="priority">{priority}</li>\n'
    
    html += """        </ol>
    </div>
</body>
</html>"""
    
    return html


def _export_pdf_data(report: Dict) -> str:
    """Export report data formatted for PDF generation"""
    if not report.get("success"):
        return json.dumps({"error": "Failed to generate report"})
    
    # Return structured data that can be used by PDF generation libraries
    pdf_data = {
        "title": report["report"]["report_metadata"]["report_title"],
        "metadata": report["report"]["report_metadata"],
        "sections": [
            {
                "title": "Executive Summary",
                "content": report["report"]["executive_summary"]
            },
            {
                "title": "Assessment Overview", 
                "content": report["report"]["assessment_overview"]
            },
            {
                "title": "Section Analysis",
                "content": report["report"]["section_analysis"]
            },
            {
                "title": "Immediate Actions",
                "content": report["report"]["immediate_actions"]
            },
            {
                "title": "Implementation Roadmap",
                "content": report["report"]["implementation_roadmap"]
            }
        ],
        "charts": report["report"]["visual_representations"]
    }
    
    return json.dumps(pdf_data, indent=2)


@tool
def create_visual_chart_data(assessment_results: str, chart_type: str) -> str:
    """
    Create specific chart data for visual representations.
    
    Args:
        assessment_results: JSON string with assessment results
        chart_type: Type of chart (radar, bar, gauge, timeline, comparison)
    
    Returns:
        JSON string with chart-specific data
    """
    try:
        results = json.loads(assessment_results)
        
        if chart_type == "radar":
            chart_data = _create_radar_chart_data(results.get("section_scores", {}))
        elif chart_type == "bar":
            chart_data = _create_bar_chart_data(results.get("section_scores", {}))
        elif chart_type == "gauge":
            chart_data = _create_gauge_data(results)
        elif chart_type == "timeline":
            chart_data = _create_timeline_data(results)
        elif chart_type == "comparison":
            chart_data = _create_comparison_data(results.get("section_scores", {}))
        else:
            return json.dumps({"success": False, "error": f"Unknown chart type: {chart_type}"})
        
        return json.dumps({
            "success": True,
            "chart_type": chart_type,
            "data": chart_data
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to create chart data: {str(e)}"})