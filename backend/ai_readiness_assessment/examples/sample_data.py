#!/usr/bin/env python3
"""
Sample Assessment Data
Provides sample data for testing and demonstration purposes
"""

from datetime import datetime, timedelta
import json


# Sample business profiles for different industries and readiness levels
SAMPLE_BUSINESSES = {
    "startup_tech": {
        "business_info": {
            "name": "InnovateTech Kenya",
            "industry": "Technology",
            "size": "Small",
            "location": "Nairobi",
            "employees": 25,
            "annual_revenue": "KES 50M",
            "founded": "2020"
        },
        "responses": {
            "data_infrastructure": {"q1": 2, "q2": 3, "q3": 2, "q4": 2, "q5": 3},
            "technology_infrastructure": {"q1": 4, "q2": 4, "q3": 3, "q4": 3, "q5": 4},
            "human_resources": {"q1": 3, "q2": 4, "q3": 2, "q4": 2, "q5": 3},
            "business_process": {"q1": 2, "q2": 2, "q3": 3, "q4": 2, "q5": 2},
            "strategic_financial": {"q1": 3, "q2": 2, "q3": 2, "q4": 3, "q5": 2},
            "regulatory_compliance": {"q1": 2, "q2": 2, "q3": 1, "q4": 2, "q5": 2}
        },
        "expected_readiness": "Foundation Building",
        "total_score": 62
    },
    
    "manufacturing_medium": {
        "business_info": {
            "name": "Kenya Manufacturing Co Ltd",
            "industry": "Manufacturing",
            "size": "Medium",
            "location": "Mombasa",
            "employees": 200,
            "annual_revenue": "KES 800M",
            "founded": "1995"
        },
        "responses": {
            "data_infrastructure": {"q1": 3, "q2": 4, "q3": 3, "q4": 3, "q5": 4},
            "technology_infrastructure": {"q1": 4, "q2": 3, "q3": 4, "q4": 3, "q5": 4},
            "human_resources": {"q1": 3, "q2": 3, "q3": 2, "q4": 3, "q5": 3},
            "business_process": {"q1": 4, "q2": 4, "q3": 4, "q4": 3, "q5": 4},
            "strategic_financial": {"q1": 3, "q2": 4, "q3": 3, "q4": 3, "q5": 3},
            "regulatory_compliance": {"q1": 3, "q2": 3, "q3": 4, "q4": 3, "q5": 3}
        },
        "expected_readiness": "Ready for Pilots",
        "total_score": 102
    },
    
    "financial_advanced": {
        "business_info": {
            "name": "Premier Bank Kenya",
            "industry": "Financial Services",
            "size": "Large",
            "location": "Nairobi",
            "employees": 2500,
            "annual_revenue": "KES 15B",
            "founded": "1970"
        },
        "responses": {
            "data_infrastructure": {"q1": 4, "q2": 5, "q3": 4, "q4": 4, "q5": 5},
            "technology_infrastructure": {"q1": 4, "q2": 4, "q3": 5, "q4": 4, "q5": 4},
            "human_resources": {"q1": 4, "q2": 4, "q3": 3, "q4": 4, "q5": 4},
            "business_process": {"q1": 4, "q2": 5, "q3": 4, "q4": 4, "q5": 4},
            "strategic_financial": {"q1": 5, "q2": 4, "q3": 4, "q4": 5, "q5": 4},
            "regulatory_compliance": {"q1": 5, "q2": 5, "q3": 4, "q4": 5, "q5": 4}
        },
        "expected_readiness": "AI Ready",
        "total_score": 125
    },
    
    "agriculture_basic": {
        "business_info": {
            "name": "Rift Valley Agri Cooperative",
            "industry": "Agriculture",
            "size": "Medium",
            "location": "Nakuru",
            "employees": 80,
            "annual_revenue": "KES 200M",
            "founded": "1985"
        },
        "responses": {
            "data_infrastructure": {"q1": 1, "q2": 2, "q3": 1, "q4": 2, "q5": 2},
            "technology_infrastructure": {"q1": 2, "q2": 1, "q3": 2, "q4": 2, "q5": 2},
            "human_resources": {"q1": 2, "q2": 2, "q3": 1, "q4": 2, "q5": 2},
            "business_process": {"q1": 2, "q2": 3, "q3": 2, "q4": 2, "q5": 3},
            "strategic_financial": {"q1": 1, "q2": 1, "q3": 2, "q4": 1, "q5": 2},
            "regulatory_compliance": {"q1": 1, "q2": 1, "q3": 1, "q4": 2, "q5": 2}
        },
        "expected_readiness": "Not Ready",
        "total_score": 43
    },
    
    "healthcare_emerging": {
        "business_info": {
            "name": "Nairobi Medical Center",
            "industry": "Healthcare",
            "size": "Medium",
            "location": "Nairobi",
            "employees": 300,
            "annual_revenue": "KES 1.2B",
            "founded": "2005"
        },
        "responses": {
            "data_infrastructure": {"q1": 3, "q2": 4, "q3": 3, "q4": 3, "q5": 3},
            "technology_infrastructure": {"q1": 3, "q2": 3, "q3": 4, "q4": 3, "q5": 3},
            "human_resources": {"q1": 2, "q2": 3, "q3": 2, "q4": 3, "q5": 2},
            "business_process": {"q1": 3, "q2": 3, "q3": 4, "q4": 3, "q5": 3},
            "strategic_financial": {"q1": 2, "q2": 3, "q3": 2, "q4": 3, "q5": 2},
            "regulatory_compliance": {"q1": 4, "q2": 4, "q3": 3, "q4": 4, "q5": 4}
        },
        "expected_readiness": "Foundation Building",
        "total_score": 78
    }
}


# Sample assessment results with different readiness levels
SAMPLE_ASSESSMENT_RESULTS = []

for business_key, business_data in SAMPLE_BUSINESSES.items():
    assessment_result = {
        "assessment_id": f"sample_{business_key}_{datetime.now().strftime('%Y%m%d')}",
        "user_id": f"user_{business_key}",
        "business_name": business_data["business_info"]["name"],
        "industry": business_data["business_info"]["industry"],
        "business_size": business_data["business_info"]["size"],
        "location": business_data["business_info"]["location"],
        "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
        "completed_at": (datetime.now() - timedelta(days=29)).isoformat(),
        "total_score": business_data["total_score"],
        "readiness_level": business_data["expected_readiness"],
        "completion_percentage": 100,
        "section_scores": {}
    }
    
    # Calculate section scores
    for section_id, responses in business_data["responses"].items():
        section_total = sum(responses.values())
        assessment_result["section_scores"][section_id] = {
            "section_total": section_total,
            "max_possible": len(responses) * 5,
            "responses": responses,
            "percentage": (section_total / (len(responses) * 5)) * 100
        }
    
    # Add sections data
    assessment_result["sections"] = {
        section_id: {
            "responses": responses,
            "completed": True,
            "completed_at": assessment_result["completed_at"]
        }
        for section_id, responses in business_data["responses"].items()
    }
    
    SAMPLE_ASSESSMENT_RESULTS.append(assessment_result)


# Sample recommendations for different readiness levels
SAMPLE_RECOMMENDATIONS = {
    "Not Ready": {
        "priority_actions": [
            "Establish basic data collection processes",
            "Implement foundational technology infrastructure",
            "Develop digital literacy training programs",
            "Create data governance framework",
            "Secure leadership commitment for digital transformation"
        ],
        "timeline": "12-18 months",
        "resource_requirements": {
            "budget_range": "KES 500K - 2M",
            "staff_time": "2-3 FTE for 12-18 months",
            "external_support": "High - consultants and training providers"
        },
        "kenya_specific_notes": [
            "Ensure compliance with Kenya's Data Protection Act 2019",
            "Leverage government digitization initiatives",
            "Partner with local tech training providers",
            "Consider mobile-first technology solutions"
        ]
    },
    
    "Foundation Building": {
        "priority_actions": [
            "Improve data quality and standardization",
            "Upgrade core technology systems",
            "Implement process documentation and automation",
            "Develop AI awareness and training programs",
            "Establish performance measurement systems"
        ],
        "timeline": "9-12 months",
        "resource_requirements": {
            "budget_range": "KES 1M - 5M",
            "staff_time": "3-5 FTE for 9-12 months",
            "external_support": "Medium - specialized consultants"
        },
        "kenya_specific_notes": [
            "Leverage Kenya's growing tech ecosystem",
            "Consider partnerships with local universities",
            "Explore government AI initiatives and support",
            "Implement local data residency requirements"
        ]
    },
    
    "Ready for Pilots": {
        "priority_actions": [
            "Select and launch AI pilot projects",
            "Develop AI governance and ethics framework",
            "Expand AI skills and capabilities",
            "Implement success measurement systems",
            "Create change management processes"
        ],
        "timeline": "6-9 months",
        "resource_requirements": {
            "budget_range": "KES 2M - 8M",
            "staff_time": "4-6 FTE for 6-9 months",
            "external_support": "Medium - pilot implementation support"
        },
        "kenya_specific_notes": [
            "Focus on use cases relevant to Kenyan market",
            "Ensure regulatory compliance from the start",
            "Consider regional expansion opportunities",
            "Leverage local AI talent and expertise"
        ]
    },
    
    "AI Ready": {
        "priority_actions": [
            "Scale successful AI pilots across organization",
            "Implement advanced AI governance framework",
            "Optimize AI ROI and business value",
            "Develop AI innovation capabilities",
            "Create AI center of excellence"
        ],
        "timeline": "3-6 months",
        "resource_requirements": {
            "budget_range": "KES 5M - 15M",
            "staff_time": "5-8 FTE for 3-6 months",
            "external_support": "Low - occasional specialized support"
        },
        "kenya_specific_notes": [
            "Position as AI leader in East Africa",
            "Share best practices with industry peers",
            "Contribute to Kenya's AI ecosystem development",
            "Explore cross-border AI opportunities"
        ]
    },
    
    "AI Advanced": {
        "priority_actions": [
            "Lead AI innovation in industry",
            "Develop cutting-edge AI solutions",
            "Mentor other organizations in AI adoption",
            "Contribute to AI research and development",
            "Establish AI partnerships and ecosystems"
        ],
        "timeline": "Ongoing",
        "resource_requirements": {
            "budget_range": "KES 10M+",
            "staff_time": "8+ FTE ongoing",
            "external_support": "Low - innovation partnerships"
        },
        "kenya_specific_notes": [
            "Lead Kenya's AI transformation",
            "Establish AI research partnerships",
            "Contribute to AI policy development",
            "Mentor emerging AI companies"
        ]
    }
}


def get_sample_business(business_type: str = "manufacturing_medium"):
    """Get sample business data"""
    return SAMPLE_BUSINESSES.get(business_type, SAMPLE_BUSINESSES["manufacturing_medium"])


def get_sample_assessment_result(readiness_level: str = "Ready for Pilots"):
    """Get sample assessment result by readiness level"""
    for result in SAMPLE_ASSESSMENT_RESULTS:
        if result["readiness_level"] == readiness_level:
            return result
    return SAMPLE_ASSESSMENT_RESULTS[0]  # Return first if not found


def get_sample_recommendations(readiness_level: str = "Ready for Pilots"):
    """Get sample recommendations by readiness level"""
    return SAMPLE_RECOMMENDATIONS.get(readiness_level, SAMPLE_RECOMMENDATIONS["Ready for Pilots"])


def get_all_sample_assessments():
    """Get all sample assessment results"""
    return SAMPLE_ASSESSMENT_RESULTS


def create_sample_assessment_file(filename: str = "sample_assessments.json"):
    """Create a JSON file with all sample assessment data"""
    sample_data = {
        "businesses": SAMPLE_BUSINESSES,
        "assessment_results": SAMPLE_ASSESSMENT_RESULTS,
        "recommendations": SAMPLE_RECOMMENDATIONS,
        "generated_at": datetime.now().isoformat(),
        "description": "Sample data for AI Readiness Assessment demonstrations"
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(sample_data, f, indent=2)
        print(f"✅ Sample data saved to {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to save sample data: {str(e)}")
        return None


if __name__ == "__main__":
    print("📊 AI Readiness Assessment - Sample Data")
    print("=" * 50)
    print()
    
    print("Available sample businesses:")
    for key, business in SAMPLE_BUSINESSES.items():
        info = business["business_info"]
        print(f"  • {key}: {info['name']} ({info['industry']}, {info['size']})")
        print(f"    Expected readiness: {business['expected_readiness']}")
        print(f"    Total score: {business['total_score']}/150")
        print()
    
    print("Creating sample data file...")
    create_sample_assessment_file()
    
    print("\nSample data is ready for use in demonstrations and testing!")