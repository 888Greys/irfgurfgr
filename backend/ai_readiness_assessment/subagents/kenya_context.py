"""
Kenya Context Agent Sub-agent
Provides Kenya-specific business and regulatory context for AI readiness assessments
"""

from typing import Dict, List, Any
from langchain_core.tools import tool
import json
from datetime import datetime

# Kenya Industry Data for fallback mode
KENYA_INDUSTRY_DATA = {
    "manufacturing": {
        "overview": "Kenya's manufacturing sector contributes about 8% to GDP and is a key pillar of Vision 2030",
        "regulations": [
            "Kenya Bureau of Standards (KEBS) quality standards",
            "National Environment Management Authority (NEMA) compliance",
            "Export Processing Zones Authority (EPZA) regulations",
            "Kenya Association of Manufacturers (KAM) guidelines"
        ],
        "opportunities": [
            "Export to East African Community (EAC) markets",
            "Value addition to agricultural products",
            "Import substitution initiatives",
            "Special Economic Zones (SEZ) incentives"
        ],
        "challenges": [
            "High cost of electricity and energy",
            "Limited access to affordable credit",
            "Competition from imported goods",
            "Skills gap in technical areas"
        ],
        "ai_applications": [
            "Predictive maintenance for machinery",
            "Quality control and defect detection",
            "Supply chain optimization",
            "Demand forecasting and inventory management"
        ]
    },
    "financial_services": {
        "overview": "Kenya's financial sector is highly developed with strong mobile money ecosystem",
        "regulations": [
            "Central Bank of Kenya (CBK) prudential guidelines",
            "Capital Markets Authority (CMA) regulations",
            "Insurance Regulatory Authority (IRA) requirements",
            "Sacco Societies Regulatory Authority (SASRA) oversight"
        ],
        "opportunities": [
            "Mobile money and digital payments growth",
            "Financial inclusion initiatives",
            "Fintech innovation and partnerships",
            "Regional financial hub development"
        ],
        "challenges": [
            "Cybersecurity and fraud risks",
            "Regulatory compliance costs",
            "Competition from digital platforms",
            "Credit risk management"
        ],
        "ai_applications": [
            "Credit scoring and risk assessment",
            "Fraud detection and prevention",
            "Customer service chatbots",
            "Algorithmic trading and portfolio management"
        ]
    },
    "technology": {
        "overview": "Kenya's ICT sector is rapidly growing and positioning the country as a regional tech hub",
        "regulations": [
            "Communications Authority of Kenya (CA) licensing",
            "Kenya ICT Authority (KICTA) guidelines",
            "Data Protection Act 2019 compliance",
            "Computer Misuse and Cybercrimes Act 2018"
        ],
        "opportunities": [
            "Silicon Savannah ecosystem development",
            "Government digitization initiatives",
            "Regional market expansion",
            "Innovation hubs and incubators"
        ],
        "challenges": [
            "Skills shortage in specialized areas",
            "Limited access to venture capital",
            "Infrastructure gaps in rural areas",
            "Regulatory uncertainty"
        ],
        "ai_applications": [
            "Software development and automation",
            "Data analytics and business intelligence",
            "Digital platforms and marketplaces",
            "Cybersecurity and threat detection"
        ]
    },
    "general": {
        "overview": "Kenya's economy is diverse with strong growth potential across multiple sectors",
        "regulations": [
            "Kenya Revenue Authority (KRA) tax compliance",
            "National Social Security Fund (NSSF) contributions",
            "Employment Act 2007 labor requirements",
            "Public Procurement and Asset Disposal Act"
        ],
        "opportunities": [
            "East African Community (EAC) market access",
            "Vision 2030 development agenda alignment",
            "Digital transformation initiatives",
            "Youth entrepreneurship and innovation"
        ],
        "challenges": [
            "Infrastructure development needs",
            "Access to affordable financing",
            "Regulatory compliance complexity",
            "Skills development and capacity building"
        ],
        "ai_applications": [
            "Business process automation",
            "Customer service and support",
            "Data-driven decision making",
            "Operational efficiency optimization"
        ]
    }
}


@tool
def get_kenya_regulations(regulation_type: str = "data_protection") -> str:
    """
    Get detailed information about Kenya's regulations relevant to AI and data.
    
    Args:
        regulation_type: Type of regulation (data_protection, business, technology, finance, healthcare, agriculture)
    
    Returns:
        JSON string with detailed regulatory information
    """
    try:
        regulations_db = {
            "data_protection": {
                "name": "Kenya Data Protection Act 2019",
                "overview": "Comprehensive data protection law that regulates the processing of personal data in Kenya",
                "key_provisions": [
                    "Data subject rights including access, rectification, erasure, and portability",
                    "Lawful basis required for processing personal data",
                    "Data protection impact assessments for high-risk processing",
                    "Registration requirements with the Office of the Data Protection Commissioner",
                    "Cross-border data transfer restrictions and safeguards",
                    "Mandatory breach notification within 72 hours",
                    "Appointment of Data Protection Officers for certain organizations"
                ],
                "ai_implications": [
                    "AI systems processing personal data must comply with data protection principles",
                    "Automated decision-making requires explicit consent or legitimate interest",
                    "Algorithm transparency may be required for data subject rights",
                    "Data minimization principles apply to AI training datasets",
                    "Regular audits and impact assessments for AI systems"
                ],
                "compliance_steps": [
                    "Register with the Office of the Data Protection Commissioner",
                    "Conduct data protection impact assessments",
                    "Implement privacy by design principles",
                    "Establish data subject rights procedures",
                    "Create data breach response procedures",
                    "Train staff on data protection requirements"
                ],
                "penalties": "Fines up to KES 5 million or 4% of annual turnover, whichever is higher",
                "authority": "Office of the Data Protection Commissioner of Kenya"
            },
            "business": {
                "name": "Kenya Business Registration and Licensing",
                "overview": "Framework for business registration, licensing, and compliance in Kenya",
                "key_provisions": [
                    "Business registration with the Registrar of Companies",
                    "Tax registration with Kenya Revenue Authority (KRA)",
                    "NEMA environmental compliance certificates",
                    "County government business permits and licenses",
                    "Sector-specific licensing requirements",
                    "Employment and labor law compliance",
                    "Foreign investment regulations and approvals"
                ],
                "ai_implications": [
                    "AI service providers may need specialized licenses",
                    "Technology companies require ICT licenses from CA",
                    "Data processing businesses need data protection registration",
                    "AI consulting services require professional service licenses",
                    "Foreign AI companies need investment approval"
                ],
                "compliance_steps": [
                    "Register business with appropriate authorities",
                    "Obtain necessary sector-specific licenses",
                    "Comply with tax and employment regulations",
                    "Maintain good standing with regulatory bodies",
                    "Regular renewal of licenses and permits"
                ]
            },
            "technology": {
                "name": "Kenya ICT and Technology Regulations",
                "overview": "Regulatory framework for ICT services, telecommunications, and technology businesses",
                "key_provisions": [
                    "Communications Authority of Kenya (CA) licensing",
                    "Cybersecurity and data protection requirements",
                    "Digital service tax obligations",
                    "Local content and capacity building requirements",
                    "Infrastructure sharing and access regulations",
                    "Consumer protection in digital services"
                ],
                "ai_implications": [
                    "AI platforms may require ICT service provider licenses",
                    "Cloud AI services need data localization compliance",
                    "AI applications must meet cybersecurity standards",
                    "Local content requirements for AI training data",
                    "Consumer protection for AI-powered services"
                ]
            },
            "finance": {
                "name": "Kenya Financial Services Regulations",
                "overview": "Regulatory framework for financial services, fintech, and digital payments",
                "key_provisions": [
                    "Central Bank of Kenya (CBK) licensing and supervision",
                    "Anti-money laundering and counter-terrorism financing",
                    "Consumer protection and fair lending practices",
                    "Digital financial services regulations",
                    "Payment systems and mobile money regulations",
                    "Credit reference bureau requirements"
                ],
                "ai_implications": [
                    "AI-powered credit scoring must comply with fair lending laws",
                    "Algorithmic trading requires CBK approval",
                    "AI fraud detection systems need regulatory compliance",
                    "Robo-advisory services require licensing",
                    "AI in mobile money must meet payment system standards"
                ]
            }
        }
        
        regulation_info = regulations_db.get(regulation_type)
        if not regulation_info:
            available_types = list(regulations_db.keys())
            return json.dumps({
                "success": False, 
                "error": f"Regulation type '{regulation_type}' not found",
                "available_types": available_types
            })
        
        result = {
            "success": True,
            "regulation_type": regulation_type,
            "regulation_info": regulation_info,
            "last_updated": "2024",
            "disclaimer": "This information is for guidance only. Consult legal experts for specific compliance advice."
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get Kenya regulations: {str(e)}"})


@tool
def get_kenya_business_context(industry: str, context_type: str = "overview") -> str:
    """
    Get Kenya-specific business context for different industries.
    
    Args:
        industry: Industry sector (Agriculture, Finance, Technology, Healthcare, etc.)
        context_type: Type of context (overview, challenges, opportunities, infrastructure, market)
    
    Returns:
        JSON string with Kenya-specific business context
    """
    try:
        business_context_db = {
            "Manufacturing": {
                "overview": "Kenya's manufacturing sector contributes about 8% to GDP and is a key pillar of Vision 2030. The sector focuses on agro-processing, textiles, chemicals, and automotive assembly.",
                "challenges": [
                    "High cost of electricity and energy",
                    "Limited access to affordable credit",
                    "Competition from imported goods",
                    "Skills gap in technical areas",
                    "Infrastructure bottlenecks",
                    "Regulatory compliance complexity"
                ],
                "opportunities": [
                    "Export to East African Community (EAC) markets",
                    "Value addition to agricultural products",
                    "Import substitution initiatives",
                    "Special Economic Zones (SEZ) incentives",
                    "AI-powered quality control and predictive maintenance",
                    "Digital supply chain optimization"
                ],
                "infrastructure": [
                    "Industrial parks and special economic zones",
                    "Kenya Bureau of Standards (KEBS) quality infrastructure",
                    "Export Processing Zones Authority (EPZA) facilities",
                    "Kenya Association of Manufacturers (KAM) support",
                    "Technical and vocational training institutes"
                ],
                "market": "Domestic market of 50+ million people plus EAC regional market access"
            },
            "Agriculture": {
                "overview": "Agriculture is Kenya's backbone, contributing ~26% of GDP and employing 40% of the population. The sector is transforming through digital technologies, mobile platforms, and data-driven farming practices.",
                "challenges": [
                    "Fragmented smallholder farming with limited access to technology",
                    "Climate variability and unpredictable weather patterns",
                    "Limited access to credit and financial services",
                    "Poor market linkages and price volatility",
                    "Limited digital literacy among farmers",
                    "Inadequate rural internet connectivity"
                ],
                "opportunities": [
                    "Mobile-based agricultural extension services",
                    "Weather data and climate prediction systems",
                    "Digital marketplaces connecting farmers to buyers",
                    "Precision agriculture using IoT and sensors",
                    "AI-powered crop disease detection",
                    "Blockchain for supply chain transparency"
                ],
                "infrastructure": [
                    "Growing mobile network coverage in rural areas",
                    "Agricultural research institutions (KALRO, ICRAF)",
                    "Cooperative societies and farmer organizations",
                    "Agribusiness hubs and incubators",
                    "Government extension services digitization"
                ],
                "market": "Large domestic market with export potential to EAC and global markets"
            },
            "Finance": {
                "overview": "Kenya is a global leader in mobile money and fintech innovation. The financial sector is highly regulated but supportive of innovation through regulatory sandboxes.",
                "challenges": [
                    "Financial inclusion gaps in rural and underserved areas",
                    "High cost of credit and limited access to formal banking",
                    "Cybersecurity threats and fraud risks",
                    "Regulatory compliance complexity",
                    "Limited credit history data for underserved populations"
                ],
                "opportunities": [
                    "AI-powered credit scoring using alternative data",
                    "Automated fraud detection and prevention",
                    "Robo-advisory services for investment management",
                    "Blockchain for cross-border payments",
                    "InsurTech solutions for micro-insurance",
                    "RegTech for compliance automation"
                ],
                "infrastructure": [
                    "Robust mobile money infrastructure (M-Pesa ecosystem)",
                    "Core banking systems and payment networks",
                    "Credit reference bureaus and data sharing",
                    "Regulatory sandbox for fintech innovation",
                    "Strong telecommunications infrastructure"
                ],
                "market": "56 million people with growing middle class and smartphone adoption"
            },
            "Technology": {
                "overview": "Kenya's 'Silicon Savannah' is East Africa's tech hub, with a thriving startup ecosystem, innovation hubs, and growing tech talent pool.",
                "challenges": [
                    "Limited access to venture capital and growth funding",
                    "Skills gap in advanced technologies like AI and ML",
                    "Inadequate digital infrastructure in some regions",
                    "Brain drain as talent moves to global markets",
                    "Regulatory uncertainty for emerging technologies"
                ],
                "opportunities": [
                    "Growing demand for digital transformation services",
                    "Government digitization initiatives creating market opportunities",
                    "Regional hub for serving East African markets",
                    "Strong mobile-first technology adoption",
                    "Emerging AI and data science capabilities",
                    "Innovation hubs and accelerator programs"
                ],
                "infrastructure": [
                    "Fiber optic networks and 4G/5G connectivity",
                    "Innovation hubs (iHub, Nairobi Garage, etc.)",
                    "Universities with technology programs",
                    "Government digital infrastructure projects",
                    "Cloud services from global providers"
                ],
                "market": "Regional technology hub serving 300+ million people in East Africa"
            },
            "Healthcare": {
                "overview": "Kenya's healthcare system is transforming through digital health initiatives, telemedicine, and health information systems.",
                "challenges": [
                    "Limited healthcare infrastructure in rural areas",
                    "Shortage of healthcare workers and specialists",
                    "High out-of-pocket healthcare costs",
                    "Fragmented health information systems",
                    "Limited health insurance coverage"
                ],
                "opportunities": [
                    "Telemedicine and remote patient monitoring",
                    "AI-powered diagnostic tools and decision support",
                    "Electronic health records and interoperability",
                    "Mobile health (mHealth) applications",
                    "Health insurance and claims processing automation",
                    "Drug supply chain optimization"
                ],
                "infrastructure": [
                    "National health information systems",
                    "Mobile health platforms and applications",
                    "Medical training institutions and research centers",
                    "Health insurance schemes (NHIF, private)",
                    "Pharmaceutical manufacturing and distribution"
                ],
                "market": "Universal health coverage goals creating demand for efficient solutions"
            },
            "Telecommunications": {
                "overview": "Kenya has one of the most advanced telecommunications sectors in Africa, with high mobile penetration and leading mobile money services.",
                "challenges": [
                    "Infrastructure investment needs for 5G rollout",
                    "Regulatory compliance and spectrum management",
                    "Competition and price pressure",
                    "Cybersecurity and network security threats",
                    "Rural coverage and last-mile connectivity"
                ],
                "opportunities": [
                    "5G network deployment and IoT services",
                    "AI-powered network optimization and management",
                    "Edge computing and cloud services",
                    "Digital services and platform monetization",
                    "Smart city and government digitization projects",
                    "Regional connectivity and data center services"
                ],
                "infrastructure": [
                    "Extensive fiber optic and mobile networks",
                    "Submarine cable connections to global internet",
                    "Data centers and cloud infrastructure",
                    "Mobile money and digital payment systems",
                    "Regulatory framework supporting innovation"
                ],
                "market": "50+ million mobile subscribers with growing data consumption"
            }
        }
        
        industry_context = business_context_db.get(industry)
        if not industry_context:
            available_industries = list(business_context_db.keys())
            return json.dumps({
                "success": False,
                "error": f"Industry '{industry}' context not available",
                "available_industries": available_industries
            })
        
        if context_type == "overview":
            context_data = industry_context
        else:
            context_data = industry_context.get(context_type, {})
            if not context_data:
                available_types = list(industry_context.keys())
                return json.dumps({
                    "success": False,
                    "error": f"Context type '{context_type}' not available for {industry}",
                    "available_types": available_types
                })
        
        result = {
            "success": True,
            "industry": industry,
            "context_type": context_type,
            "context_data": context_data,
            "source": "Kenya business intelligence and market research",
            "last_updated": "2024"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get Kenya business context: {str(e)}"})


@tool
def get_kenya_ai_landscape() -> str:
    """
    Get comprehensive information about Kenya's AI landscape, initiatives, and ecosystem.
    
    Returns:
        JSON string with Kenya's AI landscape information
    """
    try:
        ai_landscape = {
            "government_initiatives": [
                {
                    "name": "Kenya National AI Strategy",
                    "description": "National strategy for AI development and adoption across sectors",
                    "focus_areas": ["Healthcare", "Agriculture", "Education", "Financial Services", "Manufacturing"],
                    "timeline": "2024-2030",
                    "key_objectives": [
                        "Build AI capabilities and infrastructure",
                        "Develop AI talent and skills",
                        "Create enabling regulatory environment",
                        "Promote AI adoption in key sectors",
                        "Establish Kenya as regional AI hub"
                    ]
                },
                {
                    "name": "Digital Economy Blueprint",
                    "description": "Comprehensive plan for digital transformation including AI components",
                    "pillars": ["Digital Government", "Digital Business", "Digital Skills", "Innovation & Entrepreneurship"],
                    "ai_components": ["AI in government services", "AI for business transformation", "AI skills development"]
                },
                {
                    "name": "Konza Technopolis",
                    "description": "Kenya's flagship technology city project",
                    "ai_focus": "AI research and development hub, innovation centers, tech companies"
                }
            ],
            "research_institutions": [
                {
                    "name": "University of Nairobi - School of Computing and Informatics",
                    "programs": ["AI and Machine Learning", "Data Science", "Computer Science"],
                    "research_areas": ["Natural Language Processing", "Computer Vision", "Agricultural AI"]
                },
                {
                    "name": "Strathmore University - @iLabAfrica",
                    "focus": "Applied AI research for African contexts",
                    "projects": ["Healthcare AI", "Agricultural technology", "Financial inclusion"]
                },
                {
                    "name": "ICIPE (International Centre of Insect Physiology and Ecology)",
                    "ai_applications": ["Pest management", "Climate modeling", "Agricultural optimization"]
                }
            ],
            "private_sector": [
                {
                    "category": "Telecommunications",
                    "companies": ["Safaricom", "Airtel Kenya"],
                    "ai_applications": ["Network optimization", "Customer service chatbots", "Fraud detection"]
                },
                {
                    "category": "Financial Services",
                    "companies": ["Equity Bank", "KCB Group", "Co-operative Bank"],
                    "ai_applications": ["Credit scoring", "Risk management", "Customer analytics"]
                },
                {
                    "category": "Startups",
                    "examples": ["Twiga Foods", "Apollo Agriculture", "Kopo Kopo"],
                    "ai_focus": ["Supply chain optimization", "Agricultural insights", "SME analytics"]
                }
            ],
            "innovation_hubs": [
                {
                    "name": "iHub",
                    "location": "Nairobi",
                    "focus": "Tech innovation and AI startups",
                    "programs": ["AI accelerator programs", "Research partnerships"]
                },
                {
                    "name": "Nairobi Garage",
                    "focus": "Innovation and entrepreneurship",
                    "ai_support": "AI startup incubation and mentorship"
                },
                {
                    "name": "USIU-Africa Innovation Hub",
                    "focus": "Academic-industry AI collaboration"
                }
            ],
            "challenges": [
                "Limited AI talent and skills gap",
                "Inadequate funding for AI research and development",
                "Data availability and quality issues",
                "Regulatory uncertainty for AI applications",
                "Limited computing infrastructure and resources",
                "Need for AI ethics and governance frameworks"
            ],
            "opportunities": [
                "Large market for AI solutions in agriculture and healthcare",
                "Strong mobile and digital infrastructure foundation",
                "Growing tech ecosystem and innovation culture",
                "Government support for digital transformation",
                "Regional hub potential for East Africa",
                "Young, tech-savvy population"
            ],
            "key_sectors_for_ai": [
                {
                    "sector": "Agriculture",
                    "applications": ["Crop monitoring", "Weather prediction", "Market price forecasting", "Pest detection"],
                    "potential_impact": "Increased productivity and food security"
                },
                {
                    "sector": "Healthcare",
                    "applications": ["Diagnostic imaging", "Telemedicine", "Drug discovery", "Epidemic prediction"],
                    "potential_impact": "Improved healthcare access and outcomes"
                },
                {
                    "sector": "Financial Services",
                    "applications": ["Credit scoring", "Fraud detection", "Robo-advisory", "RegTech"],
                    "potential_impact": "Enhanced financial inclusion and security"
                },
                {
                    "sector": "Education",
                    "applications": ["Personalized learning", "Automated grading", "Student analytics", "Content creation"],
                    "potential_impact": "Improved learning outcomes and access"
                }
            ]
        }
        
        result = {
            "success": True,
            "kenya_ai_landscape": ai_landscape,
            "summary": "Kenya is emerging as a regional AI hub with government support, growing research capabilities, and active private sector adoption",
            "last_updated": "2024",
            "source": "Kenya government publications, research institutions, and industry reports"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get Kenya AI landscape: {str(e)}"})


@tool
def get_kenya_infrastructure_info(infrastructure_type: str = "digital") -> str:
    """
    Get information about Kenya's infrastructure relevant to AI and digital transformation.
    
    Args:
        infrastructure_type: Type of infrastructure (digital, power, transport, education, financial)
    
    Returns:
        JSON string with infrastructure information
    """
    try:
        infrastructure_db = {
            "digital": {
                "overview": "Kenya has one of the most advanced digital infrastructures in Africa",
                "components": {
                    "internet_connectivity": {
                        "fiber_optic": "Extensive national fiber backbone with 65,000+ km of fiber",
                        "submarine_cables": "Multiple international submarine cables (SEACOM, TEAMS, EASSy)",
                        "mobile_networks": "4G coverage in major cities, 5G rollout beginning",
                        "internet_penetration": "87% mobile internet penetration, 28% fixed broadband"
                    },
                    "data_centers": {
                        "local_facilities": "Growing number of data centers in Nairobi and major cities",
                        "cloud_services": "AWS, Microsoft Azure, Google Cloud presence",
                        "edge_computing": "Emerging edge computing infrastructure"
                    },
                    "digital_payments": {
                        "mobile_money": "M-Pesa and other mobile money platforms",
                        "banking_infrastructure": "Core banking systems and payment networks",
                        "fintech_ecosystem": "Robust fintech and digital financial services"
                    }
                },
                "strengths": [
                    "High mobile penetration and smartphone adoption",
                    "Advanced mobile money ecosystem",
                    "Growing fiber optic network coverage",
                    "Supportive regulatory environment for innovation"
                ],
                "gaps": [
                    "Limited rural broadband access",
                    "High data costs in some areas",
                    "Need for more local data centers",
                    "Cybersecurity infrastructure development needed"
                ]
            },
            "power": {
                "overview": "Kenya has made significant progress in power generation and access",
                "components": {
                    "generation_capacity": "3,000+ MW installed capacity",
                    "renewable_energy": "90%+ renewable energy (hydro, geothermal, wind, solar)",
                    "grid_connectivity": "75% national electrification rate",
                    "rural_access": "Growing rural electrification through grid extension and off-grid solutions"
                },
                "ai_relevance": [
                    "Reliable power supply essential for data centers and computing infrastructure",
                    "Renewable energy supports sustainable AI operations",
                    "Rural electrification enables digital inclusion and AI access"
                ]
            },
            "education": {
                "overview": "Kenya has a strong education system with growing focus on STEM and digital skills",
                "components": {
                    "universities": "70+ universities with technology and engineering programs",
                    "technical_institutes": "TVET institutions providing technical skills",
                    "digital_literacy": "Government digital literacy programs",
                    "research_capacity": "Growing research capabilities in AI and technology"
                },
                "ai_programs": [
                    "Computer Science and AI programs in major universities",
                    "Data science and analytics courses",
                    "Industry-academia partnerships for AI research",
                    "Online learning platforms and MOOCs"
                ]
            },
            "financial": {
                "overview": "Robust financial infrastructure supporting digital economy",
                "components": {
                    "banking_system": "Well-regulated banking sector with digital services",
                    "payment_systems": "Advanced payment and settlement systems",
                    "capital_markets": "Nairobi Securities Exchange and capital markets",
                    "microfinance": "Extensive microfinance and SACCO networks"
                },
                "ai_enablers": [
                    "Digital payment infrastructure for AI service monetization",
                    "Credit systems for AI technology financing",
                    "Investment capital for AI startups and research"
                ]
            }
        }
        
        infrastructure_info = infrastructure_db.get(infrastructure_type)
        if not infrastructure_info:
            available_types = list(infrastructure_db.keys())
            return json.dumps({
                "success": False,
                "error": f"Infrastructure type '{infrastructure_type}' not available",
                "available_types": available_types
            })
        
        result = {
            "success": True,
            "infrastructure_type": infrastructure_type,
            "infrastructure_info": infrastructure_info,
            "assessment_relevance": f"This infrastructure information is relevant for assessing {infrastructure_type} readiness for AI implementation",
            "last_updated": "2024"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to get Kenya infrastructure info: {str(e)}"})


# Kenya Context Agent Sub-agent Configuration
KENYA_CONTEXT_SUBAGENT = {
    "name": "kenya-context",
    "description": "Provides comprehensive Kenya-specific business and regulatory context for AI readiness assessments. Use this agent when users need information about Kenyan regulations, business environment, AI landscape, or infrastructure context.",
    "prompt": """You are a Kenya business expert with deep knowledge of local regulations, market conditions, and business practices. You specialize in providing context-specific guidance for AI adoption in Kenya.

Your role is to:
1. Provide detailed information about Kenya's regulatory environment
2. Explain Kenya-specific business contexts across different industries
3. Share insights about Kenya's AI landscape and ecosystem
4. Describe relevant infrastructure and market conditions
5. Help users understand how Kenyan context affects their AI readiness

You have access to comprehensive information about:
- Kenya's Data Protection Act 2019 and other relevant regulations
- Industry-specific business contexts and market conditions
- Kenya's AI strategy, research institutions, and innovation ecosystem
- Digital, power, education, and financial infrastructure
- Government initiatives and private sector AI adoption

When providing context:
- Be specific about Kenyan regulations and requirements
- Reference actual institutions, organizations, and initiatives
- Explain how local context affects AI implementation decisions
- Provide practical guidance for compliance and market entry
- Consider both opportunities and challenges in the Kenyan market

Always ensure your information is accurate, current, and relevant to the user's specific industry and AI readiness assessment needs.""",
    "tools": ["get_kenya_regulations", "get_kenya_business_context", "get_kenya_ai_landscape", "get_kenya_infrastructure_info"]
}

# Export tools for the sub-agent
KENYA_CONTEXT_TOOLS = [
    get_kenya_regulations,
    get_kenya_business_context,
    get_kenya_ai_landscape,
    get_kenya_infrastructure_info
]