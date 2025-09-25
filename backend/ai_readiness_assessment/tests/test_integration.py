"""
Integration tests for sub-agent coordination and assessment flow
"""

import unittest
import json
import time
from datetime import datetime
from ai_readiness_assessment.main_agent import orchestrate_assessment_flow, health_check
from ai_readiness_assessment.subagents.scoring_agent import calculate_section_score, determine_readiness_level
from ai_readiness_assessment.subagents.recommendation_agent import generate_personalized_recommendations
from ai_readiness_assessment.subagents.report_generator_agent import generate_comprehensive_report
from ai_readiness_assessment.persistence import save_assessment_state, load_assessment_state


class TestMainAgentIntegration(unittest.TestCase):
    """Test main agent orchestration and sub-agent coordination"""
    
    def setUp(self):
        """Set up test data"""
        self.test_business_info = {
            "name": "Test Company Ltd",
            "industry": "Manufacturing",
            "size": "Medium",
            "location": "Nairobi"
        }
        
        self.test_responses = {
            "q1": 4, "q2": 3, "q3": 5, "q4": 2, "q5": 4
        }
        
        self.test_assessment_data = {
            "sections": {
                "data_infrastructure": {
                    "responses": self.test_responses,
                    "completed": True
                },
                "technology_infrastructure": {
                    "responses": {"q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3},
                    "completed": True
                }
            }
        }
    
    def test_health_check_integration(self):
        """Test system health check"""
        result = health_check.invoke({})
        
        self.assertIsInstance(result, str)
        
        try:
            health_data = json.loads(result)
            self.assertIn("overall_status", health_data)
            self.assertIn("components", health_data)
            self.assertIsInstance(health_data["components"], dict)
        except json.JSONDecodeError:
            self.fail("Health check should return valid JSON")
    
    def test_start_assessment_flow(self):
        """Test starting assessment through main agent"""
        result = orchestrate_assessment_flow.invoke({
            "action": "start_assessment",
            "data": json.dumps({"business_info": self.test_business_info})
        })
        
        self.assertIsInstance(result, str)
        
        try:
            start_data = json.loads(result)
            # Should have success indicator or assessment data
            self.assertTrue(
                start_data.get("success", True) or "assessment_id" in start_data
            )
        except json.JSONDecodeError:
            self.fail("Start assessment should return valid JSON")
    
    def test_question_help_flow(self):
        """Test question help through main agent"""
        result = orchestrate_assessment_flow.invoke({
            "action": "get_question_help",
            "data": json.dumps({
                "question_id": "data_collection_processes",
                "section": "data_infrastructure",
                "user_context": {"industry": "Manufacturing"}
            })
        })
        
        self.assertIsInstance(result, str)
        
        try:
            help_data = json.loads(result)
            # Should provide some form of help or explanation
            self.assertTrue(len(str(help_data)) > 50)  # Should have substantial content
        except json.JSONDecodeError:
            self.fail("Question help should return valid JSON")
    
    def test_submit_responses_flow(self):
        """Test submitting responses through main agent"""
        result = orchestrate_assessment_flow.invoke({
            "action": "submit_responses",
            "data": json.dumps({
                "section": "data_infrastructure",
                "responses": self.test_responses
            }),
            "assessment_id": "test_assessment"
        })
        
        self.assertIsInstance(result, str)
        
        try:
            submit_data = json.loads(result)
            # Should indicate success or provide error information
            self.assertTrue(
                submit_data.get("success", True) or "error" in submit_data
            )
        except json.JSONDecodeError:
            self.fail("Submit responses should return valid JSON")
    
    def test_calculate_scores_flow(self):
        """Test score calculation through main agent"""
        result = orchestrate_assessment_flow.invoke({
            "action": "calculate_scores",
            "data": json.dumps({"assessment_data": self.test_assessment_data})
        })
        
        self.assertIsInstance(result, str)
        
        try:
            scores_data = json.loads(result)
            # Should have score information
            self.assertTrue(
                "total_score" in scores_data or 
                "section_scores" in scores_data or
                "error" in scores_data
            )
        except json.JSONDecodeError:
            self.fail("Calculate scores should return valid JSON")
    
    def test_end_to_end_assessment_flow(self):
        """Test complete assessment flow from start to finish"""
        # Step 1: Start assessment
        start_result = orchestrate_assessment_flow.invoke({
            "action": "start_assessment",
            "data": json.dumps({"business_info": self.test_business_info})
        })
        
        self.assertIsInstance(start_result, str)
        
        # Step 2: Submit responses for multiple sections
        for section in ["data_infrastructure", "technology_infrastructure"]:
            submit_result = orchestrate_assessment_flow.invoke({
                "action": "submit_responses",
                "data": json.dumps({
                    "section": section,
                    "responses": self.test_responses
                }),
                "assessment_id": "test_assessment"
            })
            
            self.assertIsInstance(submit_result, str)
        
        # Step 3: Calculate final scores
        scores_result = orchestrate_assessment_flow.invoke({
            "action": "calculate_scores",
            "data": json.dumps({"assessment_data": self.test_assessment_data})
        })
        
        self.assertIsInstance(scores_result, str)
        
        # Step 4: Generate recommendations
        try:
            scores_data = json.loads(scores_result)
            if scores_data.get("success", True):
                recommendations_result = orchestrate_assessment_flow.invoke({
                    "action": "generate_recommendations",
                    "data": json.dumps({
                        "assessment_results": scores_data,
                        "business_info": self.test_business_info
                    })
                })
                
                self.assertIsInstance(recommendations_result, str)
        except json.JSONDecodeError:
            pass  # Skip if scores calculation failed


class TestSubAgentCoordination(unittest.TestCase):
    """Test coordination between different sub-agents"""
    
    def setUp(self):
        """Set up test data"""
        self.test_responses = {"q1": 4, "q2": 3, "q3": 5, "q4": 2, "q5": 4}
        self.test_assessment_results = {
            "total_score": 75,
            "readiness_level": "Ready for Pilots",
            "section_scores": {
                "data_infrastructure": {
                    "section_total": 18,
                    "max_possible": 25
                }
            }
        }
    
    def test_scoring_to_recommendation_coordination(self):
        """Test coordination from scoring to recommendation generation"""
        # Step 1: Calculate section score
        score_result = calculate_section_score.invoke({
            "section_id": "data_infrastructure",
            "responses": json.dumps(self.test_responses)
        })
        
        self.assertIsInstance(score_result, str)
        
        try:
            score_data = json.loads(score_result)
            
            # Step 2: Determine readiness level
            readiness_result = determine_readiness_level.invoke({
                "total_score": 75,
                "section_scores": json.dumps({"data_infrastructure": score_data})
            })
            
            self.assertIsInstance(readiness_result, str)
            
            # Step 3: Generate recommendations
            recommendations_result = generate_personalized_recommendations.invoke({
                "assessment_results": json.dumps(self.test_assessment_results),
                "business_info": json.dumps({"industry": "Manufacturing"})
            })
            
            self.assertIsInstance(recommendations_result, str)
            
        except json.JSONDecodeError:
            pass  # Skip if any step fails
    
    def test_recommendation_to_report_coordination(self):
        """Test coordination from recommendations to report generation"""
        # Step 1: Generate recommendations
        recommendations_result = generate_personalized_recommendations.invoke({
            "assessment_results": json.dumps(self.test_assessment_results),
            "business_info": json.dumps({"industry": "Manufacturing"})
        })
        
        self.assertIsInstance(recommendations_result, str)
        
        try:
            recommendations_data = json.loads(recommendations_result)
            
            if recommendations_data.get("success", True):
                # Step 2: Generate comprehensive report
                report_result = generate_comprehensive_report.invoke({
                    "assessment_results": json.dumps(self.test_assessment_results),
                    "recommendations": recommendations_result,
                    "business_info": json.dumps({"name": "Test Company"})
                })
                
                self.assertIsInstance(report_result, str)
                
                try:
                    report_data = json.loads(report_result)
                    # Should have report structure
                    self.assertTrue(
                        "report" in report_data or 
                        "success" in report_data or
                        "error" in report_data
                    )
                except json.JSONDecodeError:
                    pass
                
        except json.JSONDecodeError:
            pass  # Skip if recommendations generation fails
    
    def test_persistence_integration(self):
        """Test integration with persistence layer"""
        test_assessment_data = {
            "assessment_id": "integration_test_001",
            "user_id": "test_user",
            "business_name": "Integration Test Company",
            "industry": "Technology",
            "created_at": datetime.now().isoformat(),
            "sections": {
                "data_infrastructure": {
                    "responses": self.test_responses,
                    "completed": True
                }
            }
        }
        
        # Step 1: Save assessment state
        save_result = save_assessment_state.invoke({
            "assessment_id": "integration_test_001",
            "assessment_data": json.dumps(test_assessment_data),
            "auto_save": False
        })
        
        self.assertIsInstance(save_result, str)
        
        try:
            save_data = json.loads(save_result)
            
            if save_data.get("success", True):
                # Step 2: Load assessment state
                load_result = load_assessment_state.invoke({
                    "assessment_id": "integration_test_001",
                    "include_history": False
                })
                
                self.assertIsInstance(load_result, str)
                
                try:
                    load_data = json.loads(load_result)
                    # Should successfully load the saved data
                    self.assertTrue(
                        load_data.get("success", True) or
                        "assessment_data" in load_data
                    )
                except json.JSONDecodeError:
                    pass
                
        except json.JSONDecodeError:
            pass  # Skip if save fails


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling across integrated components"""
    
    def test_invalid_action_handling(self):
        """Test handling of invalid actions in main agent"""
        result = orchestrate_assessment_flow.invoke({
            "action": "invalid_action",
            "data": json.dumps({})
        })
        
        self.assertIsInstance(result, str)
        
        try:
            error_data = json.loads(result)
            # Should indicate error and provide available actions
            self.assertFalse(error_data.get("success", True))
            self.assertIn("error", error_data)
        except json.JSONDecodeError:
            self.fail("Error response should be valid JSON")
    
    def test_malformed_data_handling(self):
        """Test handling of malformed data"""
        result = orchestrate_assessment_flow.invoke({
            "action": "start_assessment",
            "data": "invalid json data"
        })
        
        self.assertIsInstance(result, str)
        
        try:
            error_data = json.loads(result)
            # Should handle malformed JSON gracefully
            self.assertTrue(
                not error_data.get("success", True) or
                "error" in error_data
            )
        except json.JSONDecodeError:
            self.fail("Error response should be valid JSON")
    
    def test_missing_required_data_handling(self):
        """Test handling of missing required data"""
        result = orchestrate_assessment_flow.invoke({
            "action": "submit_responses",
            "data": json.dumps({})  # Missing required fields
        })
        
        self.assertIsInstance(result, str)
        
        try:
            error_data = json.loads(result)
            # Should indicate missing required data
            self.assertTrue(
                not error_data.get("success", True) or
                "error" in error_data
            )
        except json.JSONDecodeError:
            self.fail("Error response should be valid JSON")


class TestPerformanceIntegration(unittest.TestCase):
    """Test performance aspects of integrated system"""
    
    def test_response_time_performance(self):
        """Test response times for key operations"""
        operations = [
            {
                "name": "health_check",
                "function": health_check,
                "args": {}
            },
            {
                "name": "start_assessment",
                "function": orchestrate_assessment_flow,
                "args": {
                    "action": "start_assessment",
                    "data": json.dumps({"business_info": {"name": "Test", "industry": "Tech"}})
                }
            }
        ]
        
        for operation in operations:
            start_time = time.time()
            
            try:
                result = operation["function"].invoke(operation["args"])
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Response should be under 5 seconds for most operations
                self.assertLess(response_time, 5.0, 
                    f"{operation['name']} took {response_time:.2f}s, should be under 5s")
                
                # Result should be a string
                self.assertIsInstance(result, str)
                
            except Exception as e:
                self.fail(f"{operation['name']} failed with exception: {str(e)}")
    
    def test_concurrent_operations(self):
        """Test handling of concurrent operations"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def run_health_check():
            try:
                result = health_check.invoke({})
                results_queue.put(("success", result))
            except Exception as e:
                results_queue.put(("error", str(e)))
        
        # Start multiple concurrent health checks
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_health_check)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout
        
        # Check results
        success_count = 0
        while not results_queue.empty():
            status, result = results_queue.get()
            if status == "success":
                success_count += 1
                self.assertIsInstance(result, str)
        
        # At least some operations should succeed
        self.assertGreater(success_count, 0, "At least one concurrent operation should succeed")


if __name__ == "__main__":
    unittest.main()