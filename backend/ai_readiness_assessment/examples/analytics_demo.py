#!/usr/bin/env python3
"""
Analytics and Insights Demonstration
Shows analytics capabilities and benchmarking features
"""

import json
from datetime import datetime
from ai_readiness_assessment.examples.sample_data import get_all_sample_assessments, SAMPLE_BUSINESSES
from ai_readiness_assessment.analytics import (
    calculate_aggregate_insights,
    generate_benchmarking_data,
    identify_common_patterns,
    generate_industry_analysis,
    generate_insights_dashboard
)


def demonstrate_aggregate_insights():
    """Demonstrate aggregate insights calculation"""
    print("📊 AGGREGATE INSIGHTS DEMONSTRATION")
    print("=" * 50)
    print()
    
    # Get sample assessment data
    sample_assessments = get_all_sample_assessments()
    
    print(f"📋 Sample Data Overview:")
    print(f"   Total Assessments: {len(sample_assessments)}")
    
    industries = set(assessment["industry"] for assessment in sample_assessments)
    print(f"   Industries: {', '.join(industries)}")
    
    readiness_levels = [assessment["readiness_level"] for assessment in sample_assessments]
    print(f"   Readiness Levels: {', '.join(set(readiness_levels))}")
    print()
    
    # Demonstrate comprehensive analysis
    print("🔍 Calculating Comprehensive Insights...")
    
    try:
        insights_result = calculate_aggregate_insights.invoke({
            "assessment_data_list": json.dumps(sample_assessments),
            "analysis_type": "comprehensive"
        })
        
        insights_data = json.loads(insights_result)
        
        if insights_data.get("success", True):
            insights = insights_data.get("insights", {})
            
            print("✅ Comprehensive insights calculated!")
            
            # Overview statistics
            if "overview" in insights:
                overview = insights["overview"]
                print("   📈 Overview Statistics:")
                print(f"      • Total Assessments: {overview.get('total_assessments', 'N/A')}")
                print(f"      • Completed Assessments: {overview.get('completed_assessments', 'N/A')}")
                print(f"      • Average Score: {overview.get('average_score', 'N/A'):.1f}")
                print(f"      • Completion Rate: {overview.get('completion_rate', 'N/A'):.1f}%")
            
            # Score analysis
            if "score_analysis" in insights:
                score_analysis = insights["score_analysis"]
                if "score_statistics" in score_analysis:
                    stats = score_analysis["score_statistics"]
                    print("   🎯 Score Analysis:")
                    print(f"      • Mean Score: {stats.get('mean', 'N/A'):.1f}")
                    print(f"      • Median Score: {stats.get('median', 'N/A'):.1f}")
                    print(f"      • Score Range: {stats.get('min', 'N/A')}-{stats.get('max', 'N/A')}")
            
            # Industry breakdown
            if "industry_breakdown" in insights:
                industry_breakdown = insights["industry_breakdown"]
                print("   🏭 Industry Breakdown:")
                for industry, data in industry_breakdown.items():
                    count = data.get("count", 0)
                    avg_score = data.get("average_score", 0)
                    print(f"      • {industry}: {count} assessments, avg score {avg_score:.1f}")
            
            # Readiness distribution
            if "readiness_distribution" in insights:
                readiness_dist = insights["readiness_distribution"]
                distribution = readiness_dist.get("distribution", {})
                print("   🎯 Readiness Distribution:")
                for level, count in distribution.items():
                    print(f"      • {level}: {count} organizations")
        else:
            print(f"❌ Insights calculation failed: {insights_data.get('error')}")
    except Exception as e:
        print(f"❌ Error calculating insights: {str(e)}")
    
    print()


def demonstrate_benchmarking():
    """Demonstrate benchmarking capabilities"""
    print("📊 BENCHMARKING DEMONSTRATION")
    print("=" * 50)
    print()
    
    # Use a sample assessment for benchmarking
    sample_assessments = get_all_sample_assessments()
    manufacturing_assessment = None
    
    for assessment in sample_assessments:
        if assessment["industry"] == "Manufacturing":
            manufacturing_assessment = assessment
            break
    
    if not manufacturing_assessment:
        print("❌ No manufacturing assessment found for benchmarking")
        return
    
    print("🏭 Sample Assessment for Benchmarking:")
    print(f"   Business: {manufacturing_assessment['business_name']}")
    print(f"   Industry: {manufacturing_assessment['industry']}")
    print(f"   Total Score: {manufacturing_assessment['total_score']}/150")
    print(f"   Readiness Level: {manufacturing_assessment['readiness_level']}")
    print()
    
    # Generate benchmarking data
    print("📈 Generating Benchmarking Data...")
    
    try:
        benchmark_result = generate_benchmarking_data.invoke({
            "assessment_results": json.dumps(manufacturing_assessment),
            "industry": "Manufacturing",
            "comparison_scope": "industry"
        })
        
        benchmark_data = json.loads(benchmark_result)
        
        if benchmark_data.get("success", True):
            benchmarking = benchmark_data.get("benchmarking_data", {})
            
            print("✅ Benchmarking data generated!")
            
            # Performance comparison
            if "benchmark_comparison" in benchmarking:
                comparison = benchmarking["benchmark_comparison"]
                
                if "score_vs_benchmark" in comparison:
                    score_comp = comparison["score_vs_benchmark"]
                    print("   📊 Score vs Benchmark:")
                    print(f"      • Your Score: {score_comp.get('score', 'N/A')}")
                    print(f"      • Industry Benchmark: {score_comp.get('benchmark', 'N/A')}")
                    print(f"      • Performance Level: {score_comp.get('performance_level', 'N/A')}")
                    print(f"      • Difference: {score_comp.get('difference', 'N/A')} points")
                
                if "readiness_vs_typical" in comparison:
                    readiness_comp = comparison["readiness_vs_typical"]
                    print("   🎯 Readiness vs Typical:")
                    print(f"      • Your Level: {readiness_comp.get('current_level', 'N/A')}")
                    print(f"      • Typical Level: {readiness_comp.get('typical_level', 'N/A')}")
                    print(f"      • Comparison: {readiness_comp.get('comparison', 'N/A')}")
            
            # Competitive position
            if "competitive_position" in benchmarking:
                position = benchmarking["competitive_position"]
                print("   🏆 Competitive Position:")
                print(f"      • Position: {position.get('position', 'N/A')}")
                print(f"      • Description: {position.get('description', 'N/A')}")
                print(f"      • Estimated Percentile: {position.get('percentile_estimate', 'N/A')}")
            
            # Improvement opportunities
            if "improvement_opportunities" in benchmarking:
                opportunities = benchmarking["improvement_opportunities"]
                print("   🚀 Top Improvement Opportunities:")
                for i, opp in enumerate(opportunities[:3], 1):
                    section = opp.get("section", "Unknown")
                    potential = opp.get("improvement_potential", 0)
                    priority = opp.get("priority", "Unknown")
                    print(f"      {i}. {section}: {potential} points potential ({priority} priority)")
        else:
            print(f"❌ Benchmarking failed: {benchmark_data.get('error')}")
    except Exception as e:
        print(f"❌ Error generating benchmarking: {str(e)}")
    
    print()


def demonstrate_pattern_identification():
    """Demonstrate pattern identification capabilities"""
    print("🔍 PATTERN IDENTIFICATION DEMONSTRATION")
    print("=" * 50)
    print()
    
    sample_assessments = get_all_sample_assessments()
    
    print(f"📋 Analyzing Patterns in {len(sample_assessments)} Assessments...")
    print()
    
    # Demonstrate gap pattern identification
    print("🔴 Identifying Common Gaps...")
    
    try:
        gaps_result = identify_common_patterns.invoke({
            "assessment_data_list": json.dumps(sample_assessments),
            "pattern_type": "gaps"
        })
        
        gaps_data = json.loads(gaps_result)
        
        if gaps_data.get("success", True):
            patterns = gaps_data.get("patterns", {})
            
            print("✅ Gap patterns identified!")
            
            if "most_common_gaps" in patterns:
                common_gaps = patterns["most_common_gaps"]
                print("   🔴 Most Common Gaps:")
                for i, (section, gap_info) in enumerate(common_gaps[:3], 1):
                    frequency = gap_info.get("frequency", 0)
                    affected = gap_info.get("affected_assessments", 0)
                    severity = gap_info.get("severity", "Unknown")
                    print(f"      {i}. {section}: {frequency:.1%} frequency, {affected} assessments ({severity} severity)")
            
            print(f"   🎯 Confidence Level: {gaps_data.get('confidence_level', 'Unknown')}")
        else:
            print(f"❌ Gap pattern identification failed: {gaps_data.get('error')}")
    except Exception as e:
        print(f"❌ Error identifying gap patterns: {str(e)}")
    
    print()
    
    # Demonstrate strength pattern identification
    print("🟢 Identifying Common Strengths...")
    
    try:
        strengths_result = identify_common_patterns.invoke({
            "assessment_data_list": json.dumps(sample_assessments),
            "pattern_type": "strengths"
        })
        
        strengths_data = json.loads(strengths_result)
        
        if strengths_data.get("success", True):
            patterns = strengths_data.get("patterns", {})
            
            print("✅ Strength patterns identified!")
            
            if "most_common_strengths" in patterns:
                common_strengths = patterns["most_common_strengths"]
                print("   🟢 Most Common Strengths:")
                for i, (section, strength_info) in enumerate(common_strengths[:3], 1):
                    frequency = strength_info.get("frequency", 0)
                    strong_assessments = strength_info.get("strong_assessments", 0)
                    consistency = strength_info.get("consistency", "Unknown")
                    print(f"      {i}. {section}: {frequency:.1%} frequency, {strong_assessments} strong assessments ({consistency} consistency)")
        else:
            print(f"❌ Strength pattern identification failed: {strengths_data.get('error')}")
    except Exception as e:
        print(f"❌ Error identifying strength patterns: {str(e)}")
    
    print()


def demonstrate_industry_analysis():
    """Demonstrate industry-specific analysis"""
    print("🏭 INDUSTRY ANALYSIS DEMONSTRATION")
    print("=" * 50)
    print()
    
    # Analyze Manufacturing industry
    industry = "Manufacturing"
    sample_assessments = get_all_sample_assessments()
    manufacturing_assessments = [a for a in sample_assessments if a["industry"] == industry]
    
    print(f"🔍 Analyzing {industry} Industry...")
    print(f"   Sample Assessments: {len(manufacturing_assessments)}")
    print()
    
    try:
        industry_result = generate_industry_analysis.invoke({
            "industry": industry,
            "assessment_data_list": json.dumps(manufacturing_assessments)
        })
        
        industry_data = json.loads(industry_result)
        
        if industry_data.get("success", True):
            analysis = industry_data.get("industry_analysis", {})
            
            print("✅ Industry analysis completed!")
            
            # Benchmark data
            if "benchmark_data" in analysis:
                benchmark = analysis["benchmark_data"]
                print("   📊 Industry Benchmarks:")
                print(f"      • Average Score: {benchmark.get('average_score', 'N/A')}")
                print(f"      • Typical Readiness: {benchmark.get('typical_readiness', 'N/A')}")
                
                common_strengths = benchmark.get("common_strengths", [])
                if common_strengths:
                    print(f"      • Common Strengths: {', '.join(common_strengths[:3])}")
                
                common_gaps = benchmark.get("common_gaps", [])
                if common_gaps:
                    print(f"      • Common Gaps: {', '.join(common_gaps[:3])}")
            
            # AI opportunities
            if "ai_opportunities" in analysis:
                opportunities = analysis["ai_opportunities"]
                print("   🚀 AI Opportunities:")
                for i, opportunity in enumerate(opportunities[:3], 1):
                    print(f"      {i}. {opportunity}")
            
            # Challenges
            if "ai_adoption_challenges" in analysis:
                challenges = analysis["ai_adoption_challenges"]
                print("   ⚠️  Key Challenges:")
                for i, challenge in enumerate(challenges[:3], 1):
                    print(f"      {i}. {challenge}")
            
            # Success factors
            if "success_factors" in analysis:
                success_factors = analysis["success_factors"]
                print("   ✅ Success Factors:")
                for i, factor in enumerate(success_factors[:3], 1):
                    print(f"      {i}. {factor}")
            
            # Case studies
            if "case_studies" in analysis:
                case_studies = analysis["case_studies"]
                print("   📚 Case Studies:")
                for i, case_study in enumerate(case_studies[:2], 1):
                    company = case_study.get("company", "Unknown")
                    use_case = case_study.get("use_case", "Unknown")
                    outcome = case_study.get("outcome", "Unknown")
                    print(f"      {i}. {company}: {use_case} - {outcome}")
        else:
            print(f"❌ Industry analysis failed: {industry_data.get('error')}")
    except Exception as e:
        print(f"❌ Error in industry analysis: {str(e)}")
    
    print()


def demonstrate_insights_dashboard():
    """Demonstrate insights dashboard generation"""
    print("📊 INSIGHTS DASHBOARD DEMONSTRATION")
    print("=" * 50)
    print()
    
    sample_assessments = get_all_sample_assessments()
    
    print(f"📋 Generating Dashboard from {len(sample_assessments)} Assessments...")
    print()
    
    # Generate executive dashboard
    print("👔 Executive Dashboard...")
    
    try:
        dashboard_result = generate_insights_dashboard.invoke({
            "assessment_data_list": json.dumps(sample_assessments),
            "dashboard_type": "executive"
        })
        
        dashboard_data = json.loads(dashboard_result)
        
        if dashboard_data.get("success", True):
            dashboard = dashboard_data.get("dashboard_data", {})
            
            print("✅ Executive dashboard generated!")
            
            # Key metrics
            if "key_metrics" in dashboard:
                metrics = dashboard["key_metrics"]
                print("   📈 Key Metrics:")
                print(f"      • Total Assessments: {metrics.get('total_assessments', 'N/A')}")
                print(f"      • Average Score: {metrics.get('average_score', 'N/A')}")
                print(f"      • Score Range: {metrics.get('score_range', 'N/A')}")
                print(f"      • Most Common Readiness: {metrics.get('most_common_readiness', 'N/A')}")
            
            # Readiness overview
            if "readiness_overview" in dashboard:
                readiness = dashboard["readiness_overview"]
                print("   🎯 Readiness Overview:")
                for level, count in readiness.items():
                    print(f"      • {level}: {count} organizations")
            
            # Top insights
            if "top_insights" in dashboard:
                insights = dashboard["top_insights"]
                print("   💡 Top Insights:")
                for i, insight in enumerate(insights[:3], 1):
                    print(f"      {i}. {insight}")
            
            # Action items
            if "action_items" in dashboard:
                actions = dashboard["action_items"]
                print("   🎯 Action Items:")
                for i, action in enumerate(actions[:3], 1):
                    print(f"      {i}. {action}")
        else:
            print(f"❌ Executive dashboard failed: {dashboard_data.get('error')}")
    except Exception as e:
        print(f"❌ Error generating executive dashboard: {str(e)}")
    
    print()


def run_analytics_demonstration():
    """Run complete analytics demonstration"""
    print("📊 AI READINESS ASSESSMENT - ANALYTICS DEMONSTRATION")
    print("=" * 70)
    print()
    print("This demonstration shows the analytics and insights capabilities")
    print("of the AI Readiness Assessment system.")
    print()
    
    # Run all analytics demonstrations
    demonstrate_aggregate_insights()
    print("=" * 50 + "\n")
    
    demonstrate_benchmarking()
    print("=" * 50 + "\n")
    
    demonstrate_pattern_identification()
    print("=" * 50 + "\n")
    
    demonstrate_industry_analysis()
    print("=" * 50 + "\n")
    
    demonstrate_insights_dashboard()
    
    print("🎉 ANALYTICS DEMONSTRATION COMPLETED!")
    print("=" * 70)
    print()
    print("📋 ANALYTICS CAPABILITIES SUMMARY:")
    print("   📊 Aggregate Insights: Statistical analysis across multiple assessments")
    print("   📈 Benchmarking: Compare individual assessments against industry standards")
    print("   🔍 Pattern Recognition: Identify common gaps, strengths, and trends")
    print("   🏭 Industry Analysis: Sector-specific insights and recommendations")
    print("   📊 Insights Dashboard: Executive, operational, and analytical views")
    print()
    print("These analytics help organizations understand their position")
    print("relative to peers and identify improvement opportunities.")
    print()
    print("For more information, visit: www.aireadiness.ke")
    print("=" * 70)


if __name__ == "__main__":
    run_analytics_demonstration()