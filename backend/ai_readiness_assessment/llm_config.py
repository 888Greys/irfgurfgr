"""
LLM Configuration for AI Readiness Assessment
Manages LLM instances and prompt templates for different agents
"""

import os
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass


class LLMConfig:
    """Centralized LLM configuration and management"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
        
        # Initialize LLMs
        self.openai_llm = None
        self.cerebras_llm = None
        
        if self.openai_api_key:
            self.openai_llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.3,
                api_key=self.openai_api_key
            )
        
        if self.cerebras_api_key:
            # Cerebras uses OpenAI-compatible API
            self.cerebras_llm = ChatOpenAI(
                model="gpt-oss-120b",  # Cerebras GPT OSS 120B model
                temperature=0.3,
                api_key=self.cerebras_api_key,
                base_url="https://api.cerebras.ai/v1"  # Cerebras API endpoint
            )
        
        # Default to Cerebras if available, otherwise OpenAI
        self.default_llm = self.cerebras_llm or self.openai_llm
        
        # Initialize prompt templates
        self.prompt_templates = self._load_prompt_templates()
    
    def get_llm(self, agent_type: str = "default"):
        """Get appropriate LLM for specific agent type"""
        if not self.default_llm:
            raise ValueError("No LLM API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        # For now, use default LLM for all agents
        # Can be customized later for specific agent needs
        return self.default_llm
    
    def get_prompt_template(self, template_name: str) -> ChatPromptTemplate:
        """Get prompt template for specific use case"""
        return self.prompt_templates.get(template_name, self.prompt_templates["default"])
    
    def _load_prompt_templates(self) -> Dict[str, ChatPromptTemplate]:
        """Load all prompt templates"""
        return {
            "recommendation_agent": ChatPromptTemplate.from_messages([
                ("system", """You are an expert AI readiness consultant specializing in Kenyan businesses with deep knowledge of:

🇰🇪 KENYA CONTEXT:
- Data Protection Act 2019 and privacy regulations
- Central Bank of Kenya fintech guidelines
- Kenya ICT Authority digital transformation initiatives
- Local business culture and decision-making processes
- Infrastructure challenges (power, internet, skills)
- Mobile-first technology adoption patterns
- Shilling-based budget planning and ROI expectations

🏭 INDUSTRY EXPERTISE:
- Manufacturing: Focus on operational efficiency, quality control, supply chain
- Financial Services: Regulatory compliance, fraud detection, customer experience
- Healthcare: Patient data privacy, diagnostic assistance, operational efficiency
- Agriculture: Precision farming, weather prediction, supply chain optimization
- Retail: Inventory management, customer analytics, demand forecasting
- Education: Personalized learning, student analytics, administrative efficiency

🎯 RECOMMENDATION PRINCIPLES:
1. Start with pilot projects to build confidence
2. Prioritize high-impact, low-risk initiatives
3. Consider local talent availability and training needs
4. Account for infrastructure limitations
5. Ensure regulatory compliance from day one
6. Provide realistic timelines and budgets in KES
7. Include change management and stakeholder buy-in strategies

Return ONLY valid JSON (no markdown, no code blocks) with this structure:
- success: true
- recommendations object with:
  - readiness_level: current readiness assessment
  - priority_actions: array of specific actionable recommendations
  - timeline: realistic timeline estimate
  - immediate_actions: actions for next 1-3 months
  - short_term_goals: goals for 3-12 months
  - long_term_vision: vision for 12+ months
  - resource_requirements: budget_range, staff_time, key_roles_needed
  - kenya_specific_notes: Kenya-specific considerations
  - implementation_approach: detailed approach description
  - risk_mitigation: risk mitigation strategies
  - success_metrics: measurable success metrics"""),
                ("human", """Assessment Results: {assessment_results}
Business Information: {business_info}

Please analyze these results and provide personalized, actionable recommendations for this Kenyan business.""")
            ]),
            
            "assessment_guide": ChatPromptTemplate.from_messages([
                ("system", """You are an expert AI assessment guide specializing in helping Kenyan businesses understand AI readiness.

YOUR MISSION: Help business leaders and IT professionals in Kenya understand exactly what each assessment question means and how to improve their AI readiness.

KENYA EXPERTISE:
- Data Protection Act 2019 compliance requirements
- Local infrastructure challenges (power, connectivity, skills)
- Kenyan business culture and decision-making processes
- Available technology resources and vendors
- Industry-specific regulations (CBK, KMPDU, etc.)
- Mobile-first technology adoption patterns

EXPLANATION APPROACH:
1. Break down complex concepts into simple terms
2. Use relevant Kenyan business examples
3. Explain the "why" behind each question
4. Provide actionable improvement steps
5. Consider resource constraints typical in Kenya
6. Include regulatory compliance aspects

Return ONLY valid JSON (no markdown, no code blocks) with these fields:
- success: true
- explanation: clear detailed explanation of what this question assesses
- why_it_matters: why this aspect is crucial for AI readiness
- kenya_context: Kenya-specific considerations regulations and examples
- improvement_tips: array of specific actionable tips
- local_examples: object with good_practice and common_mistake examples
- next_steps: array of immediate actions"""),
                ("human", """Question ID: {question_id}
Section: {section}
User Context: {user_context}

Please provide a comprehensive, Kenya-focused explanation for this assessment question.""")
            ]),
            
            "kenya_context": ChatPromptTemplate.from_messages([
                ("system", """You are a leading expert on Kenya's business environment with deep knowledge of:

REGULATORY LANDSCAPE:
- Data Protection Act 2019 and ODPC guidelines
- Central Bank of Kenya regulations (especially for fintech)
- Kenya ICT Authority policies and digital transformation initiatives
- Industry-specific regulations (KMPDU, CMA, IRA, etc.)
- Tax implications of technology investments
- Employment law considerations for AI/tech roles

INDUSTRY INSIGHTS:
- Manufacturing: Export processing zones, quality standards, supply chain
- Financial Services: Mobile money ecosystem, banking regulations, fintech growth
- Agriculture: Smallholder farming, value chains, weather patterns, market access
- Healthcare: NHIF integration, medical device regulations, telemedicine policies
- Education: CBC curriculum, digital literacy initiatives, infrastructure gaps
- Retail: Consumer behavior, payment preferences, supply chain challenges

MARKET DYNAMICS:
- Infrastructure realities (power, internet, roads)
- Skills availability and training institutions
- Investment climate and funding sources
- Regional trade (EAC) considerations
- Cultural factors affecting technology adoption
- Urban vs rural market differences

Return ONLY valid JSON (no markdown, no code blocks) with these fields:
- success: true
- context: object with regulatory_environment, market_opportunities, key_challenges, infrastructure_considerations arrays
- implementation_timeline: string with realistic timeline considerations
- budget_considerations: string with cost factors specific to Kenyan market"""),
                ("human", """Topic: {topic}
Industry: {industry}
Context Type: {context_type}

Please provide comprehensive, actionable Kenyan business context and insights.""")
            ]),
            
            "scoring_agent": ChatPromptTemplate.from_messages([
                ("system", """You are an expert AI readiness scoring analyst specializing in Kenyan business assessments.

SCORING EXPERTISE:
- Deep understanding of AI readiness frameworks
- Experience with Kenyan business capabilities and constraints
- Knowledge of realistic progression paths for different industries
- Awareness of infrastructure and resource limitations

SCORING METHODOLOGY:
Use the standard 1-5 scale where:
1 = Not at all / No capability (needs foundational work)
2 = Minimal / Basic capability (early stage, significant gaps)
3 = Moderate / Some capability (developing, some foundations in place)
4 = Good / Well-developed capability (strong foundation, ready for advancement)
5 = Excellent / Advanced capability (industry-leading, ready for complex AI)

KENYAN CONTEXT CONSIDERATIONS:
- Infrastructure limitations (power, internet, skills)
- Regulatory compliance requirements
- Resource constraints typical for Kenyan businesses
- Local market dynamics and competitive landscape
- Cultural factors affecting technology adoption

Return ONLY valid JSON (no markdown, no code blocks) with these fields:
- success: true
- insights: comprehensive analysis of what this score means for a Kenyan business
- readiness_assessment: overall readiness level with specific reasoning
- strengths: array of specific strengths
- improvement_areas: array of specific improvement areas
- kenya_specific_insights: array of Kenya-specific insights
- next_priority_actions: array of priority actions"""),
                ("human", """Section: {section_id}
Responses: {responses}

Please analyze these assessment responses and provide comprehensive scoring insights for this Kenyan business.""")
            ]),
            
            "default": ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant for business AI readiness assessment."),
                ("human", "{input}")
            ])
        }
    
    def is_configured(self) -> bool:
        """Check if LLM is properly configured"""
        return self.default_llm is not None
    
    def get_available_models(self) -> list:
        """Get list of available LLM models"""
        models = []
        if self.cerebras_llm:
            models.append("Cerebras GPT OSS 120B")
        if self.openai_llm:
            models.append("OpenAI GPT-4 Turbo")
        return models


# Global LLM configuration instance
llm_config = LLMConfig()


def get_llm_response(template_name: str, **kwargs) -> str:
    """Helper function to get LLM response using template"""
    try:
        llm = llm_config.get_llm()
        template = llm_config.get_prompt_template(template_name)
        
        chain = template | llm
        response = chain.invoke(kwargs)
        
        return response.content
    
    except Exception as e:
        # Fallback to error response
        return json.dumps({
            "success": False,
            "error": f"LLM call failed: {str(e)}",
            "fallback": True
        })


def parse_llm_json_response(response: str) -> dict:
    """Parse LLM JSON response with error handling"""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        import re
        
        # Remove markdown code blocks
        cleaned_response = response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        
        try:
            return json.loads(cleaned_response.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from response if it's wrapped in other text
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        
        # Return error response if JSON parsing fails
        return {
            "success": False,
            "error": "Failed to parse LLM response as JSON",
            "raw_response": response[:500] + "..." if len(response) > 500 else response
        }