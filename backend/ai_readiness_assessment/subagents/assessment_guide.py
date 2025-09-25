"""
Assessment Guide Sub-agent
Provides detailed explanations, clarifications, and Kenya-specific guidance for assessment questions
"""

from typing import Dict, List, Any
from langchain_core.tools import tool
import json

from ..content import AssessmentContent


# Global content instance for sub-agent
_content = AssessmentContent()


@tool
def get_question_explanation(question_id: str, section: str = None, user_context: str = "{}") -> str:
    """
    Get detailed explanation and examples for a specific assessment question using LLM.
    
    Args:
        question_id: The question ID (e.g., "1.1", "2.3", "6.1")
        section: Optional section ID for context
        user_context: Optional JSON string with user context
    
    Returns:
        JSON string with detailed explanation and Kenya-specific examples
    """
    try:
        from ..llm_config import llm_config, get_llm_response, parse_llm_json_response
        
        # Get original question data for context
        question = _content.get_question(question_id)
        if not question:
            return json.dumps({"success": False, "error": f"Question {question_id} not found"})
        
        # Check if LLM is configured
        if not llm_config.is_configured():
            # Fallback to original implementation
            return _get_question_explanation_fallback(question_id, question)
        
        # Prepare context for LLM
        question_context = {
            "question_text": question.question,
            "question_description": question.description,
            "section_name": question.section_name,
            "scoring_rubric": question.scoring_rubric
        }
        
        # Get LLM-powered explanation
        llm_response = get_llm_response(
            "assessment_guide",
            question_id=question_id,
            section=section or question.section_name,
            user_context=user_context,
            question_context=json.dumps(question_context)
        )
        
        # Parse LLM response
        explanation_data = parse_llm_json_response(llm_response)
        
        # If LLM response is valid, enhance it with original data
        if explanation_data.get("success"):
            explanation_data["question"] = {
                "id": question.id,
                "description": question.description,
                "question": question.question,
                "section": question.section_name
            }
            explanation_data["scoring_guidance"] = question.scoring_rubric
            explanation_data["llm_powered"] = True
            
            return json.dumps(explanation_data, indent=2)
        
        # Fallback if LLM response is invalid
        return _get_question_explanation_fallback(question_id, question)
        
    except Exception as e:
        # Fallback on any error
        return _get_question_explanation_fallback(question_id, question)


def _get_question_explanation_fallback(question_id: str, question) -> str:
    """Fallback question explanation using original logic"""
    try:
        # Get Kenya-specific examples based on question type
        kenya_examples = _get_kenya_examples(question_id, question.description)
        
        result = {
            "success": True,
            "question": {
                "id": question.id,
                "description": question.description,
                "question": question.question,
                "section": question.section_name
            },
            "detailed_explanation": _get_detailed_explanation(question_id, question.description),
            "scoring_guidance": question.scoring_rubric,
            "kenya_examples": kenya_examples,
            "tips": _get_assessment_tips(question_id),
            "llm_powered": False
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get question explanation: {str(e)}"})


@tool
def get_section_guidance(section_id: str) -> str:
    """
    Get comprehensive guidance for completing an entire assessment section.
    
    Args:
        section_id: The section ID (e.g., "section1", "section2")
    
    Returns:
        JSON string with section overview and completion guidance
    """
    try:
        section = _content.get_section(section_id)
        if not section:
            return json.dumps({"success": False, "error": f"Section {section_id} not found"})
        
        result = {
            "success": True,
            "section": {
                "id": section.id,
                "name": section.name,
                "description": section.description,
                "max_points": section.max_points,
                "question_count": len(section.questions)
            },
            "completion_guidance": _get_section_completion_guidance(section_id),
            "common_challenges": _get_common_challenges(section_id),
            "kenya_context": _get_kenya_section_context(section_id),
            "preparation_tips": _get_preparation_tips(section_id)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get section guidance: {str(e)}"})


@tool
def get_industry_specific_guidance(industry: str, question_id: str = None) -> str:
    """
    Get industry-specific guidance for assessment questions.
    
    Args:
        industry: The business industry
        question_id: Optional specific question ID for targeted guidance
    
    Returns:
        JSON string with industry-specific assessment guidance
    """
    try:
        if question_id:
            question = _content.get_question(question_id)
            if not question:
                return json.dumps({"success": False, "error": f"Question {question_id} not found"})
        
        result = {
            "success": True,
            "industry": industry,
            "guidance": _get_industry_guidance(industry, question_id),
            "common_scenarios": _get_industry_scenarios(industry, question_id),
            "benchmarks": _get_industry_benchmarks(industry),
            "recommendations": _get_industry_recommendations(industry)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get industry guidance: {str(e)}"})


def _get_detailed_explanation(question_id: str, description: str) -> str:
    """Get detailed explanation for a question"""
    explanations = {
        "data_collection_processes": "Data Collection Processes evaluates how systematically your organization gathers, stores, and manages data from various business operations. This includes the methods, tools, and procedures used to collect data, ensuring data quality, consistency, and accessibility for AI applications.",
        "1.1": "Data Availability measures how much of your business operations generate and store digital data. This includes customer records, transaction data, operational metrics, inventory systems, and employee information. Higher digitization enables better AI implementation.",
        
        "1.2": "Data Quality refers to the accuracy, completeness, consistency, and reliability of your business data. Poor data quality can significantly impact AI model performance and decision-making accuracy.",
        
        "1.3": "Data Integration assesses how well your different business systems can share and exchange data. Integrated systems enable comprehensive data analysis and more effective AI implementations.",
        
        "1.4": "Data Governance involves having formal policies, procedures, and controls for managing data access, quality, security, and compliance. Strong governance is essential for responsible AI deployment.",
        
        "1.5": "Data Storage & Processing Capacity evaluates your infrastructure's ability to handle large volumes of data required for AI applications. This includes both storage capacity and computational power.",
        
        "2.1": "IT Systems Maturity measures how modern, capable, and well-integrated your current technology infrastructure is. Modern systems are more compatible with AI tools and platforms.",
        
        "2.2": "Cloud Readiness assesses your organization's adoption and comfort with cloud computing services, which are often essential for scalable AI implementations.",
        
        "2.3": "Internet & Connectivity evaluates the reliability and speed of your internet connection, which is crucial for cloud-based AI services and real-time data processing.",
        
        "2.4": "Security Infrastructure measures your cybersecurity capabilities, which become even more critical when implementing AI systems that process sensitive business data.",
        
        "3.1": "Technical Skills assesses the technical expertise available in your organization, including IT skills, data analysis capabilities, and any existing AI/ML knowledge.",
        
        "3.2": "Data Literacy measures how comfortable your team is with using data for decision-making, which is fundamental for successful AI adoption.",
        
        "3.3": "Change Management Capability evaluates how well your organization adapts to new technologies and processes, which is crucial for successful AI transformation.",
        
        "3.4": "Leadership Support measures the commitment of senior management to digital transformation and AI adoption, including resource allocation and strategic priority.",
        
        "4.1": "Process Documentation assesses how well your business processes are documented and standardized, which is important for identifying AI automation opportunities.",
        
        "4.2": "Process Automation Level measures the current level of automation in your business processes, indicating readiness for more advanced AI-driven automation.",
        
        "4.3": "Performance Measurement evaluates how well you track and measure business process performance, which is essential for measuring AI impact and ROI.",
        
        "5.1": "Strategic Vision assesses whether your organization has a clear digital transformation strategy that includes AI adoption plans and objectives.",
        
        "5.2": "Budget Allocation measures the financial commitment to technology and innovation, indicating the resources available for AI initiatives.",
        
        "6.1": "Data Protection Compliance specifically addresses compliance with Kenya's Data Protection Act 2019, which is crucial for responsible AI deployment in Kenya.",
        
        "6.2": "Risk Management Framework evaluates your organization's approach to managing technology and data risks, which becomes more complex with AI implementation."
    }
    
    return explanations.get(question_id, f"This question assesses {description.lower()} in the context of AI readiness.")


def _get_kenya_examples(question_id: str, description: str) -> List[str]:
    """Get Kenya-specific examples for questions"""
    examples = {
        "data_collection_processes": [
            "M-Pesa transaction records and mobile money data collection",
            "Customer registration data from telecommunications providers",
            "Agricultural production data from farming cooperatives",
            "Retail point-of-sale systems in Nairobi shopping centers",
            "Digital forms for customer onboarding in Kenyan banks"
        ],
        "1.1": [
            "M-Pesa transaction records and mobile money data",
            "Customer registration data from telecommunications providers",
            "Agricultural production data from farming cooperatives",
            "Retail point-of-sale systems in Nairobi shopping centers"
        ],
        "1.2": [
            "Ensuring customer phone numbers are properly formatted (+254 format)",
            "Validating business registration numbers with the Registrar of Companies",
            "Cross-checking agricultural data with Kenya Bureau of Statistics",
            "Maintaining accurate inventory data for import/export documentation"
        ],
        "1.3": [
            "Integrating M-Pesa payment data with inventory management systems",
            "Connecting customer service systems with billing platforms",
            "Linking agricultural data collection with supply chain management",
            "Integrating HR systems with payroll and tax reporting systems"
        ],
        "1.4": [
            "Implementing data governance policies compliant with Kenya's Data Protection Act 2019",
            "Establishing data access controls for sensitive customer information",
            "Creating data retention policies for financial transaction records",
            "Implementing data classification for personal vs. business data"
        ],
        "1.5": [
            "Using cloud services from providers with data centers in Kenya or Africa",
            "Implementing scalable storage for growing mobile transaction volumes",
            "Processing large datasets for agricultural yield predictions",
            "Managing high-volume customer data for telecommunications providers"
        ],
        "6.1": [
            "Compliance with Kenya's Data Protection Act 2019 requirements",
            "Implementation of data subject rights and consent mechanisms",
            "Data protection impact assessments for new systems",
            "Registration with the Office of the Data Protection Commissioner"
        ],
        "6.2": [
            "Risk assessment frameworks for technology implementations",
            "Business continuity plans for digital system failures",
            "Cybersecurity risk management procedures",
            "Compliance risk management for regulatory requirements"
        ]
    }
    
    return examples.get(question_id, [f"Consider how {description.lower()} applies to your specific industry context in Kenya"])


def _get_assessment_tips(question_id: str) -> List[str]:
    """Get assessment tips for questions"""
    tips = {
        "1.1": [
            "Consider all business processes, not just customer-facing ones",
            "Include data from mobile applications and digital platforms",
            "Think about both structured data (databases) and unstructured data (documents, emails)",
            "Consider data generated by IoT devices or sensors if applicable"
        ],
        "1.2": [
            "Assess data accuracy by checking for duplicates and inconsistencies",
            "Consider how often data needs to be cleaned or corrected",
            "Evaluate data completeness - are there missing fields or records?",
            "Think about data validation processes and quality controls"
        ]
    }
    
    return tips.get(question_id, ["Consider your current capabilities and future needs", "Think about both technical and organizational aspects"])


def _get_section_completion_guidance(section_id: str) -> str:
    """Get guidance for completing a section"""
    guidance = {
        "section1": "Focus on your current data capabilities and infrastructure. Be honest about data quality issues and integration challenges. Consider both the quantity and quality of data your organization collects and manages.",
        
        "section2": "Evaluate your technology infrastructure objectively. Consider not just what you have, but how well it works and how ready it is for future AI implementations. Think about reliability, scalability, and security.",
        
        "section3": "Assess your human resources honestly. Consider both current skills and the organization's ability to learn and adapt. Leadership support is crucial for successful AI adoption.",
        
        "section4": "Think about how well your business processes are documented and measured. Consider automation opportunities and how well you track performance metrics.",
        
        "section5": "Be realistic about your strategic vision and financial commitment. Consider both current budget allocation and future investment plans for technology.",
        
        "section6": "Focus on compliance and risk management frameworks. Consider both current compliance status and your organization's approach to managing technology risks."
    }
    
    return guidance.get(section_id, "Complete this section by honestly assessing your current capabilities and readiness.")


def _get_common_challenges(section_id: str) -> List[str]:
    """Get common challenges for each section"""
    challenges = {
        "section1": [
            "Data scattered across multiple systems with no integration",
            "Poor data quality requiring significant manual cleaning",
            "Lack of formal data governance policies",
            "Limited data storage and processing capacity"
        ],
        "section2": [
            "Legacy systems that are difficult to integrate",
            "Limited cloud adoption and experience",
            "Unreliable internet connectivity",
            "Inadequate cybersecurity measures"
        ]
    }
    
    return challenges.get(section_id, ["Consider the specific challenges relevant to this assessment area"])


def _get_kenya_section_context(section_id: str) -> str:
    """Get Kenya-specific context for sections"""
    context = {
        "section1": "Kenya's digital economy is rapidly growing, with mobile money systems like M-Pesa generating vast amounts of transaction data. Consider how your organization can leverage Kenya's digital infrastructure and data ecosystem.",
        
        "section6": "Kenya's Data Protection Act 2019 requires specific compliance measures for data processing. Consider registration requirements with the Office of the Data Protection Commissioner and implementation of data subject rights."
    }
    
    return context.get(section_id, "Consider the specific Kenyan business and regulatory context for this assessment area.")


def _get_preparation_tips(section_id: str) -> List[str]:
    """Get preparation tips for sections"""
    tips = {
        "section1": [
            "Inventory all your data sources and systems",
            "Assess data quality by sampling key datasets",
            "Document current data integration points",
            "Review existing data governance policies"
        ]
    }
    
    return tips.get(section_id, ["Prepare by gathering relevant information about your current capabilities"])


def _get_industry_guidance(industry: str, question_id: str = None) -> str:
    """Get industry-specific guidance"""
    industry_guidance = {
        "Agriculture": "Focus on data from farming operations, supply chain management, and market access. Consider mobile-based data collection and weather/climate data integration.",
        "Telecommunications": "Leverage your digital infrastructure and customer data. Focus on network analytics, customer behavior analysis, and service optimization.",
        "Finance": "Prioritize data security, regulatory compliance, and customer data management. Consider transaction data analysis and risk management systems."
    }
    
    return industry_guidance.get(industry, "Consider how AI readiness applies to your specific industry context and requirements.")


def _get_industry_scenarios(industry: str, question_id: str = None) -> List[str]:
    """Get industry-specific scenarios"""
    scenarios = {
        "Agriculture": [
            "Using weather data and soil sensors for crop yield prediction",
            "Implementing supply chain tracking from farm to market",
            "Analyzing market prices for optimal selling decisions"
        ]
    }
    
    return scenarios.get(industry, ["Consider scenarios specific to your industry and business model"])


def _get_industry_benchmarks(industry: str) -> Dict[str, str]:
    """Get industry benchmarks"""
    return {
        "data_digitization": "Most leading organizations in your industry have 70-80% of processes digitized",
        "cloud_adoption": "Industry leaders typically have 60-70% of systems in the cloud",
        "automation_level": "Top performers usually have 40-60% of routine processes automated",
        "ai_readiness": "Industry pioneers are typically in the 'AI Ready' or 'AI Advanced' categories"
    }


def _get_industry_recommendations(industry: str) -> List[str]:
    """Get industry-specific recommendations"""
    recommendations = {
        "Agriculture": [
            "Start with mobile data collection for farm operations",
            "Integrate weather and market data for decision-making",
            "Consider partnerships with agtech companies"
        ]
    }
    
    return recommendations.get(industry, ["Focus on areas most relevant to your industry and business model"])


# Assessment Guide Sub-agent Configuration
ASSESSMENT_GUIDE_SUBAGENT = {
    "name": "assessment-guide",
    "description": "Provides detailed explanations, clarifications, and Kenya-specific guidance for assessment questions. Use this agent when users need help understanding questions, want examples, or need context-specific guidance for their industry or situation.",
    "prompt": """You are an AI readiness assessment guide specializing in helping Kenyan businesses understand assessment questions and complete their evaluations effectively.

Your role is to:
1. Provide clear, detailed explanations of assessment questions
2. Offer Kenya-specific examples and context
3. Give industry-specific guidance when relevant
4. Help users understand scoring criteria
5. Provide practical tips for assessment completion

You have access to tools that provide:
- Detailed question explanations with Kenya-specific examples
- Section-level guidance and completion tips
- Industry-specific recommendations and scenarios
- Common challenges and how to address them

When helping users:
- Be encouraging and supportive
- Provide concrete, actionable examples
- Reference Kenyan business context and regulations when relevant
- Help users understand what each score level means in practice
- Suggest preparation steps for better assessment accuracy

Always aim to help users complete their assessment honestly and accurately, while providing the context they need to understand what each question is really asking about their AI readiness.""",
    "tools": ["get_question_explanation", "get_section_guidance", "get_industry_specific_guidance"]
}

# Export tools for the sub-agent
ASSESSMENT_GUIDE_TOOLS = [
    get_question_explanation,
    get_section_guidance,
    get_industry_specific_guidance
]