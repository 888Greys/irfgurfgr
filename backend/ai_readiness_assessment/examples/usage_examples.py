#!/usr/bin/env python3
"""
Usage Examples and Documentation
Comprehensive examples showing different ways to use the assessment system
"""

import json
from datetime import datetime
from ai_readiness_assessment.main_agent import orchestrate_assessment_flow, health_check
from ai_readiness_assessment.examples.sample_data import get_sample_business, get_sample_assessment_result


def example_quick_assessment():
    """Example: Quick assessment for immediate insights"""
    print("⚡ QUICK ASSESSMENT EXAMPLE")
    print("=" * 40)
    print("Use case: Get rapid AI readiness insights for decision making")
    print()
    
    # Sample business data
    business_info = {
        "name": "QuickTech Solutions",
        "industry": "Technology",
        "size": "Small"
    }
    
    # Quick responses (simplified)
    quick_responses = {
        "data_infrastructure": {"q1": 3, "q2": 2, "q3": 3, "q4": 2, "q5": 3},
        "technology_infrastructure": {"q1": 4, "q2": 3, "q3": 4, "q4": 3, "q5": 3},
        "human_resources": {"q1": 2, "q2": 3, "q3": 2, "q4": 2, "q5": 3}
    }
    
    print("📋 Business Profile:")
    print(f"   Name: {business_info['name']}")
    print(f"   Industry: {business_info['industry']}")
    print(f"   Size: {business_info['size']}")
    print()
    
    print("📊 Quick Assessment Results:")
    total_score = 0
    max_possible = 0
    
    for section, responses in quick_responses.items():
        section_score = sum(responses.values())
        section_max = len(responses) * 5
        percentage = (section_score / section_max) * 100
        
        total_score += section_score
        max_possible += section_max
        
        print(f"   {section.replace('_', ' ').title()}: {section_score}/{section_max} ({percentage:.1f}%)")
    
    overall_percentage = (total_score / max_possible) * 100
    
    # Quick readiness determination
    if overall_percentage >= 80:
        readiness = "AI Ready"
    elif overall_percentage >= 60:
        readiness = "Ready for Pilots"
    elif overall_percentage >= 40:
        readiness = "Foundation Building"
    else:
        readiness = "Not Ready"
    
    print()
    print(f"🎯 Quick Readiness Assessment: {readiness}")
    print(f"📈 Overall Score: {total_score}/{max_possible} ({overall_percentage:.1f}%)")
    print()
    
    # Quick recommendations
    recommendations = {
        "Not Ready": ["Focus on basic digitization", "Improve data collection", "Build technical capacity"],
        "Foundation Building": ["Standardize processes", "Upgrade technology", "Develop AI strategy"],
        "Ready for Pilots": ["Launch pilot projects", "Build AI team", "Measure success"],
        "AI Ready": ["Scale AI solutions", "Optimize performance", "Lead innovation"]
    }
    
    print("💡 Quick Recommendations:")
    for i, rec in enumerate(recommendations[readiness][:3], 1):
        print(f"   {i}. {rec}")
    
    print()
    print("⏱️  Assessment Time: ~10 minutes")
    print("🎯 Use Case: Initial screening, budget planning, strategic discussions")
    print()


def example_detailed_assessment():
    """Example: Detailed assessment for comprehensive planning"""
    print("🔍 DETAILED ASSESSMENT EXAMPLE")
    print("=" * 40)
    print("Use case: Comprehensive analysis for detailed AI implementation planning")
    print()
    
    # Use sample data for detailed assessment
    sample_business = get_sample_business("manufacturing_medium")
    business_info = sample_business["business_info"]
    
    print("📋 Business Profile:")
    for key, value in business_info.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    print()
    
    print("📊 Detailed Assessment Process:")
    print("   1. Complete all 6 assessment sections (30 questions)")
    print("   2. Get section-by-section analysis")
    print("   3. Receive personalized recommendations")
    print("   4. Generate comprehensive report")
    print("   5. Create implementation roadmap")
    print()
    
    # Show detailed section analysis
    responses = sample_business["responses"]
    
    print("📈 Section Analysis:")
    section_names = {
        "data_infrastructure": "Data Infrastructure & Quality",
        "technology_infrastructure": "Technology Infrastructure",
        "human_resources": "Human Resources & Skills",
        "business_process": "Business Process Maturity",
        "strategic_financial": "Strategic & Financial Readiness",
        "regulatory_compliance": "Regulatory & Compliance Readiness"
    }
    
    total_score = 0
    for section_id, section_name in section_names.items():
        if section_id in responses:
            section_responses = responses[section_id]
            section_score = sum(section_responses.values())
            section_max = len(section_responses) * 5
            percentage = (section_score / section_max) * 100
            
            total_score += section_score
            
            # Status indicator
            if percentage >= 80:
                status = "🟢 Strong"
            elif percentage >= 60:
                status = "🟡 Good"
            elif percentage >= 40:
                status = "🟠 Needs Improvement"
            else:
                status = "🔴 Critical Gap"
            
            print(f"   {section_name}: {section_score}/{section_max} ({percentage:.1f}%) {status}")
    
    overall_percentage = (total_score / 150) * 100
    readiness_level = sample_business["expected_readiness"]
    
    print()
    print(f"🏆 Final Assessment Results:")
    print(f"   Total Score: {total_score}/150 ({overall_percentage:.1f}%)")
    print(f"   Readiness Level: {readiness_level}")
    print()
    
    print("📋 Detailed Outputs:")
    print("   • Executive summary with key findings")
    print("   • Section-by-section analysis and recommendations")
    print("   • Implementation roadmap with timelines")
    print("   • Resource requirements and budget estimates")
    print("   • Risk assessment and mitigation strategies")
    print("   • Kenya-specific compliance and context")
    print("   • Visual charts and benchmarking data")
    print()
    
    print("⏱️  Assessment Time: ~45 minutes")
    print("🎯 Use Case: Strategic planning, budget allocation, implementation roadmaps")
    print()


def example_multi_organization_analysis():
    """Example: Multi-organization analysis for benchmarking"""
    print("🏢 MULTI-ORGANIZATION ANALYSIS EXAMPLE")
    print("=" * 40)
    print("Use case: Analyze multiple organizations for benchmarking and insights")
    print()
    
    # Sample organizations
    organizations = [
        {"name": "TechStart Kenya", "industry": "Technology", "score": 62, "level": "Foundation Building"},
        {"name": "Manufacturing Co", "industry": "Manufacturing", "score": 102, "level": "Ready for Pilots"},
        {"name": "Premier Bank", "industry": "Financial Services", "score": 125, "level": "AI Ready"},
        {"name": "Agri Cooperative", "industry": "Agriculture", "score": 43, "level": "Not Ready"},
        {"name": "Medical Center", "industry": "Healthcare", "score": 78, "level": "Foundation Building"}
    ]
    
    print("📊 Organization Portfolio:")
    for org in organizations:
        print(f"   • {org['name']} ({org['industry']}): {org['score']}/150 - {org['level']}")
    print()
    
    # Calculate aggregate statistics
    total_orgs = len(organizations)
    avg_score = sum(org["score"] for org in organizations) / total_orgs
    
    # Readiness distribution
    readiness_dist = {}
    for org in organizations:
        level = org["level"]
        readiness_dist[level] = readiness_dist.get(level, 0) + 1
    
    # Industry analysis
    industry_scores = {}
    for org in organizations:
        industry = org["industry"]
        if industry not in industry_scores:
            industry_scores[industry] = []
        industry_scores[industry].append(org["score"])
    
    print("📈 Aggregate Analysis:")
    print(f"   Total Organizations: {total_orgs}")
    print(f"   Average Score: {avg_score:.1f}/150 ({avg_score/150*100:.1f}%)")
    print()
    
    print("🎯 Readiness Distribution:")
    for level, count in readiness_dist.items():
        percentage = (count / total_orgs) * 100
        print(f"   • {level}: {count} orgs ({percentage:.1f}%)")
    print()
    
    print("🏭 Industry Performance:")
    for industry, scores in industry_scores.items():
        avg_industry_score = sum(scores) / len(scores)
        print(f"   • {industry}: {avg_industry_score:.1f} average score")
    print()
    
    print("💡 Key Insights:")
    print("   • Most organizations are in Foundation Building phase")
    print("   • Financial Services shows highest readiness")
    print("   • Agriculture sector needs significant support")
    print("   • Technology companies vary widely in readiness")
    print()
    
    print("📋 Multi-Organization Outputs:")
    print("   • Portfolio readiness dashboard")
    print("   • Industry benchmarking reports")
    print("   • Common gap and strength analysis")
    print("   • Best practice sharing recommendations")
    print("   • Investment prioritization guidance")
    print()
    
    print("⏱️  Analysis Time: ~15 minutes (after individual assessments)")
    print("🎯 Use Case: Portfolio management, industry analysis, policy making")
    print()


def example_api_integration():
    """Example: API integration for automated workflows"""
    print("🔌 API INTEGRATION EXAMPLE")
    print("=" * 40)
    print("Use case: Integrate assessment system into existing business applications")
    print()
    
    print("📡 API Endpoints Available:")
    print("   • POST /assessment/start - Start new assessment")
    print("   • POST /assessment/submit - Submit section responses")
    print("   • GET /assessment/{id}/status - Get assessment status")
    print("   • POST /assessment/calculate - Calculate scores")
    print("   • POST /recommendations/generate - Generate recommendations")
    print("   • POST /reports/create - Create comprehensive report")
    print("   • GET /analytics/insights - Get aggregate insights")
    print()
    
    print("🔧 Integration Example (Python):")
    print("""
    import requests
    import json
    
    # Start assessment
    response = requests.post('/api/assessment/start', json={
        'business_info': {
            'name': 'My Company',
            'industry': 'Technology',
            'size': 'Medium'
        }
    })
    assessment_id = response.json()['assessment_id']
    
    # Submit responses
    requests.post(f'/api/assessment/{assessment_id}/submit', json={
        'section': 'data_infrastructure',
        'responses': {'q1': 4, 'q2': 3, 'q3': 5, 'q4': 2, 'q5': 4}
    })
    
    # Get results
    results = requests.get(f'/api/assessment/{assessment_id}/results')
    print(f"Readiness Level: {results.json()['readiness_level']}")
    """)
    
    print("🔧 Integration Example (JavaScript):")
    print("""
    // Start assessment
    const assessment = await fetch('/api/assessment/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            business_info: {
                name: 'My Company',
                industry: 'Technology',
                size: 'Medium'
            }
        })
    });
    
    const {assessment_id} = await assessment.json();
    
    // Submit responses
    await fetch(`/api/assessment/${assessment_id}/submit`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            section: 'data_infrastructure',
            responses: {q1: 4, q2: 3, q3: 5, q4: 2, q5: 4}
        })
    });
    """)
    
    print("📋 Integration Benefits:")
    print("   • Automated assessment workflows")
    print("   • Real-time readiness monitoring")
    print("   • Custom dashboard integration")
    print("   • Bulk assessment processing")
    print("   • Automated reporting and alerts")
    print()
    
    print("🎯 Use Case: Enterprise systems, SaaS platforms, consulting tools")
    print()


def example_command_line_usage():
    """Example: Command-line usage for developers and administrators"""
    print("💻 COMMAND-LINE USAGE EXAMPLE")
    print("=" * 40)
    print("Use case: Developer tools, automation scripts, system administration")
    print()
    
    print("🔧 Command-Line Interface:")
    print("   python -m ai_readiness_assessment.interface")
    print("   python -m ai_readiness_assessment.interface --resume assessment_123")
    print("   python -m ai_readiness_assessment.interface --no-progress")
    print()
    
    print("🧪 Testing Commands:")
    print("   python -m ai_readiness_assessment.tests.test_runner")
    print("   python -m ai_readiness_assessment.tests.test_runner --suite models")
    print("   python -m ai_readiness_assessment.tests.test_runner --save-report")
    print()
    
    print("📊 Analytics Commands:")
    print("   python -m ai_readiness_assessment.examples.analytics_demo")
    print("   python -m ai_readiness_assessment.examples.complete_assessment_demo")
    print("   python -m ai_readiness_assessment.examples.sub_agent_demos")
    print()
    
    print("📋 Batch Processing Example:")
    print("""
    #!/bin/bash
    # Batch process multiple assessments
    
    for company in company1 company2 company3; do
        echo "Processing $company..."
        python -m ai_readiness_assessment.interface \\
            --batch-mode \\
            --input-file "${company}_responses.json" \\
            --output-file "${company}_report.json"
    done
    
    # Generate aggregate report
    python -m ai_readiness_assessment.analytics \\
        --input-dir ./reports \\
        --output-file aggregate_analysis.json
    """)
    
    print("🔧 Configuration Example:")
    print("""
    # config.json
    {
        "assessment_settings": {
            "auto_save": true,
            "progress_indicators": true,
            "detailed_feedback": true
        },
        "output_settings": {
            "default_format": "json",
            "include_charts": true,
            "kenya_context": true
        },
        "analytics_settings": {
            "benchmark_data": true,
            "industry_comparison": true,
            "trend_analysis": true
        }
    }
    """)
    
    print("📋 Command-Line Benefits:")
    print("   • Scriptable and automatable")
    print("   • Batch processing capabilities")
    print("   • Integration with CI/CD pipelines")
    print("   • System administration tools")
    print("   • Development and testing workflows")
    print()
    
    print("🎯 Use Case: DevOps, automation, system integration, testing")
    print()


def run_all_usage_examples():
    """Run all usage examples"""
    print("📚 AI READINESS ASSESSMENT - USAGE EXAMPLES")
    print("=" * 70)
    print()
    print("This guide shows different ways to use the AI Readiness Assessment system")
    print("for various use cases and integration scenarios.")
    print()
    
    # Run all examples
    example_quick_assessment()
    print("=" * 50 + "\n")
    
    example_detailed_assessment()
    print("=" * 50 + "\n")
    
    example_multi_organization_analysis()
    print("=" * 50 + "\n")
    
    example_api_integration()
    print("=" * 50 + "\n")
    
    example_command_line_usage()
    
    print("🎉 USAGE EXAMPLES COMPLETED!")
    print("=" * 70)
    print()
    print("📋 USAGE SCENARIOS SUMMARY:")
    print("   ⚡ Quick Assessment: Rapid insights for decision making")
    print("   🔍 Detailed Assessment: Comprehensive analysis and planning")
    print("   🏢 Multi-Organization: Portfolio analysis and benchmarking")
    print("   🔌 API Integration: Automated workflows and custom applications")
    print("   💻 Command-Line: Developer tools and system administration")
    print()
    print("Choose the approach that best fits your needs and technical requirements.")
    print("All methods provide the same core assessment capabilities with different")
    print("levels of detail and integration options.")
    print()
    print("For more information and documentation, visit: www.aireadiness.ke")
    print("=" * 70)


if __name__ == "__main__":
    run_all_usage_examples()