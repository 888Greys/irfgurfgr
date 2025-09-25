"""
Performance tests for concurrent assessment handling and system load
"""

import unittest
import json
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from ai_readiness_assessment.main_agent import orchestrate_assessment_flow, health_check
from ai_readiness_assessment.subagents.scoring_agent import calculate_section_score
from ai_readiness_assessment.subagents.recommendation_agent import generate_personalized_recommendations
from ai_readiness_assessment.persistence import save_assessment_state, load_assessment_state


class TestPerformanceBasics(unittest.TestCase):
    """Test basic performance characteristics"""
    
    def setUp(self):
        """Set up performance test data"""
        self.test_responses = {"q1": 4, "q2": 3, "q3": 5, "q4": 2, "q5": 4}
        self.test_business_info = {
            "name": "Performance Test Company",
            "industry": "Technology",
            "size": "Medium"
        }
        self.performance_thresholds = {
            "health_check": 2.0,  # seconds
            "section_score": 3.0,
            "start_assessment": 5.0,
            "generate_recommendations": 10.0
        }
    
    def test_health_check_performance(self):
        """Test health check response time"""
        start_time = time.time()
        
        result = health_check.invoke({})
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertLess(response_time, self.performance_thresholds["health_check"],
            f"Health check took {response_time:.2f}s, should be under {self.performance_thresholds['health_check']}s")
        
        self.assertIsInstance(result, str)
    
    def test_section_score_performance(self):
        """Test section score calculation performance"""
        start_time = time.time()
        
        result = calculate_section_score.invoke({
            "section_id": "data_infrastructure",
            "responses": json.dumps(self.test_responses)
        })
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertLess(response_time, self.performance_thresholds["section_score"],
            f"Section score calculation took {response_time:.2f}s, should be under {self.performance_thresholds['section_score']}s")
        
        self.assertIsInstance(result, str)
    
    def test_start_assessment_performance(self):
        """Test assessment start performance"""
        start_time = time.time()
        
        result = orchestrate_assessment_flow.invoke({
            "action": "start_assessment",
            "data": json.dumps({"business_info": self.test_business_info})
        })
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertLess(response_time, self.performance_thresholds["start_assessment"],
            f"Start assessment took {response_time:.2f}s, should be under {self.performance_thresholds['start_assessment']}s")
        
        self.assertIsInstance(result, str)
    
    def test_recommendation_generation_performance(self):
        """Test recommendation generation performance"""
        test_assessment_results = {
            "total_score": 75,
            "readiness_level": "Ready for Pilots",
            "section_scores": {
                "data_infrastructure": {"section_total": 18, "max_possible": 25}
            }
        }
        
        start_time = time.time()
        
        result = generate_personalized_recommendations.invoke({
            "assessment_results": json.dumps(test_assessment_results),
            "business_info": json.dumps(self.test_business_info)
        })
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertLess(response_time, self.performance_thresholds["generate_recommendations"],
            f"Recommendation generation took {response_time:.2f}s, should be under {self.performance_thresholds['generate_recommendations']}s")
        
        self.assertIsInstance(result, str)


class TestConcurrentOperations(unittest.TestCase):
    """Test concurrent operation handling"""
    
    def setUp(self):
        """Set up concurrent test data"""
        self.test_responses = {"q1": 4, "q2": 3, "q3": 5, "q4": 2, "q5": 4}
        self.concurrent_users = 5
        self.operations_per_user = 3
    
    def test_concurrent_health_checks(self):
        """Test concurrent health check operations"""
        results_queue = queue.Queue()
        
        def run_health_check(user_id):
            try:
                start_time = time.time()
                result = health_check.invoke({})
                end_time = time.time()
                
                results_queue.put({
                    "user_id": user_id,
                    "success": True,
                    "response_time": end_time - start_time,
                    "result_length": len(result)
                })
            except Exception as e:
                results_queue.put({
                    "user_id": user_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Start concurrent operations
        threads = []
        for user_id in range(self.concurrent_users):
            thread = threading.Thread(target=run_health_check, args=(user_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # Analyze results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # All operations should complete
        self.assertEqual(len(results), self.concurrent_users)
        
        # Most operations should succeed
        successful_operations = [r for r in results if r["success"]]
        success_rate = len(successful_operations) / len(results)
        self.assertGreaterEqual(success_rate, 0.8, "At least 80% of concurrent operations should succeed")
        
        # Response times should be reasonable
        if successful_operations:
            avg_response_time = sum(r["response_time"] for r in successful_operations) / len(successful_operations)
            self.assertLess(avg_response_time, 5.0, "Average response time should be under 5 seconds")
    
    def test_concurrent_section_scoring(self):
        """Test concurrent section scoring operations"""
        results_queue = queue.Queue()
        
        def run_section_scoring(user_id):
            try:
                start_time = time.time()
                result = calculate_section_score.invoke({
                    "section_id": f"data_infrastructure_{user_id}",
                    "responses": json.dumps(self.test_responses)
                })
                end_time = time.time()
                
                results_queue.put({
                    "user_id": user_id,
                    "success": True,
                    "response_time": end_time - start_time,
                    "result": result
                })
            except Exception as e:
                results_queue.put({
                    "user_id": user_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Start concurrent operations
        threads = []
        for user_id in range(self.concurrent_users):
            thread = threading.Thread(target=run_section_scoring, args=(user_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=15)
        
        # Analyze results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Check success rate
        successful_operations = [r for r in results if r["success"]]
        success_rate = len(successful_operations) / len(results) if results else 0
        self.assertGreaterEqual(success_rate, 0.7, "At least 70% of concurrent scoring operations should succeed")
    
    def test_concurrent_assessment_workflows(self):
        """Test concurrent complete assessment workflows"""
        with ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
            futures = []
            
            for user_id in range(self.concurrent_users):
                future = executor.submit(self._run_assessment_workflow, user_id)
                futures.append(future)
            
            # Collect results
            results = []
            for future in as_completed(futures, timeout=30):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({"success": False, "error": str(e)})
            
            # Analyze results
            successful_workflows = [r for r in results if r["success"]]
            success_rate = len(successful_workflows) / len(results) if results else 0
            
            self.assertGreaterEqual(success_rate, 0.6, "At least 60% of concurrent workflows should succeed")
    
    def _run_assessment_workflow(self, user_id):
        """Run a complete assessment workflow for performance testing"""
        try:
            # Step 1: Start assessment
            start_result = orchestrate_assessment_flow.invoke({
                "action": "start_assessment",
                "data": json.dumps({
                    "business_info": {
                        "name": f"Test Company {user_id}",
                        "industry": "Technology",
                        "size": "Medium"
                    }
                })
            })
            
            # Step 2: Submit responses
            submit_result = orchestrate_assessment_flow.invoke({
                "action": "submit_responses",
                "data": json.dumps({
                    "section": "data_infrastructure",
                    "responses": self.test_responses
                }),
                "assessment_id": f"test_assessment_{user_id}"
            })
            
            # Step 3: Calculate scores
            scores_result = orchestrate_assessment_flow.invoke({
                "action": "calculate_scores",
                "data": json.dumps({
                    "assessment_data": {
                        "sections": {
                            "data_infrastructure": {
                                "responses": self.test_responses,
                                "completed": True
                            }
                        }
                    }
                })
            })
            
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            return {"success": False, "user_id": user_id, "error": str(e)}


class TestMemoryUsage(unittest.TestCase):
    """Test memory usage patterns"""
    
    def setUp(self):
        """Set up memory test data"""
        self.large_responses = {f"q{i}": (i % 5) + 1 for i in range(1, 101)}  # 100 questions
        self.test_iterations = 50
    
    def test_memory_stability_repeated_operations(self):
        """Test memory stability with repeated operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform repeated operations
        for i in range(self.test_iterations):
            try:
                result = health_check.invoke({})
                
                # Occasionally check memory usage
                if i % 10 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_increase = current_memory - initial_memory
                    
                    # Memory increase should be reasonable (less than 100MB)
                    self.assertLess(memory_increase, 100,
                        f"Memory usage increased by {memory_increase:.1f}MB after {i} operations")
                
            except Exception:
                pass  # Continue testing even if some operations fail
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_memory_increase = final_memory - initial_memory
        
        # Total memory increase should be reasonable
        self.assertLess(total_memory_increase, 200,
            f"Total memory increase of {total_memory_increase:.1f}MB is too high")
    
    def test_large_data_handling(self):
        """Test handling of large assessment data"""
        large_assessment_data = {
            "assessment_id": "large_test",
            "user_id": "test_user",
            "business_name": "Large Data Test Company",
            "industry": "Technology",
            "sections": {}
        }
        
        # Create large sections data
        for section_id in range(10):  # 10 sections
            large_assessment_data["sections"][f"section_{section_id}"] = {
                "responses": self.large_responses,
                "completed": True
            }
        
        try:
            # Test saving large data
            start_time = time.time()
            
            save_result = save_assessment_state.invoke({
                "assessment_id": "large_test",
                "assessment_data": json.dumps(large_assessment_data),
                "auto_save": False
            })
            
            save_time = time.time() - start_time
            
            # Should complete within reasonable time
            self.assertLess(save_time, 10.0, "Large data save should complete within 10 seconds")
            
            # Test loading large data
            start_time = time.time()
            
            load_result = load_assessment_state.invoke({
                "assessment_id": "large_test",
                "include_history": False
            })
            
            load_time = time.time() - start_time
            
            # Should complete within reasonable time
            self.assertLess(load_time, 5.0, "Large data load should complete within 5 seconds")
            
        except Exception as e:
            self.fail(f"Large data handling failed: {str(e)}")


class TestScalabilityLimits(unittest.TestCase):
    """Test system scalability limits"""
    
    def test_maximum_concurrent_users(self):
        """Test system behavior with maximum concurrent users"""
        max_users = 20  # Test with 20 concurrent users
        
        def simple_operation(user_id):
            try:
                result = health_check.invoke({})
                return {"user_id": user_id, "success": True, "result_length": len(result)}
            except Exception as e:
                return {"user_id": user_id, "success": False, "error": str(e)}
        
        with ThreadPoolExecutor(max_workers=max_users) as executor:
            futures = [executor.submit(simple_operation, i) for i in range(max_users)]
            
            results = []
            for future in as_completed(futures, timeout=30):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({"success": False, "error": str(e)})
        
        # Analyze results
        successful_operations = [r for r in results if r.get("success")]
        success_rate = len(successful_operations) / len(results) if results else 0
        
        # Should handle at least 50% of maximum load
        self.assertGreaterEqual(success_rate, 0.5,
            f"System should handle at least 50% of {max_users} concurrent users")
        
        # Should complete most operations
        self.assertGreaterEqual(len(results), max_users * 0.8,
            "At least 80% of operations should complete")
    
    def test_rapid_sequential_operations(self):
        """Test rapid sequential operations"""
        operations_count = 100
        max_time_per_operation = 2.0  # seconds
        
        start_time = time.time()
        successful_operations = 0
        
        for i in range(operations_count):
            operation_start = time.time()
            
            try:
                result = health_check.invoke({})
                operation_time = time.time() - operation_start
                
                # Each operation should complete within time limit
                if operation_time <= max_time_per_operation:
                    successful_operations += 1
                
            except Exception:
                pass  # Continue with next operation
        
        total_time = time.time() - start_time
        
        # Should complete reasonable number of operations
        success_rate = successful_operations / operations_count
        self.assertGreaterEqual(success_rate, 0.7,
            f"Should complete at least 70% of {operations_count} rapid operations")
        
        # Average time per operation should be reasonable
        avg_time_per_operation = total_time / operations_count
        self.assertLess(avg_time_per_operation, 1.0,
            f"Average time per operation ({avg_time_per_operation:.2f}s) should be under 1s")


class TestResourceUtilization(unittest.TestCase):
    """Test resource utilization patterns"""
    
    def test_cpu_usage_patterns(self):
        """Test CPU usage during operations"""
        import psutil
        
        # Measure CPU usage during intensive operations
        cpu_percentages = []
        
        for i in range(10):
            cpu_before = psutil.cpu_percent(interval=0.1)
            
            # Perform operation
            try:
                result = calculate_section_score.invoke({
                    "section_id": "data_infrastructure",
                    "responses": json.dumps({"q1": 4, "q2": 3, "q3": 5, "q4": 2, "q5": 4})
                })
            except Exception:
                pass
            
            cpu_after = psutil.cpu_percent(interval=0.1)
            cpu_percentages.append(max(cpu_before, cpu_after))
        
        # CPU usage should be reasonable
        avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
        max_cpu = max(cpu_percentages)
        
        self.assertLess(avg_cpu, 80.0, f"Average CPU usage ({avg_cpu:.1f}%) should be under 80%")
        self.assertLess(max_cpu, 95.0, f"Maximum CPU usage ({max_cpu:.1f}%) should be under 95%")
    
    def test_response_time_consistency(self):
        """Test response time consistency across multiple operations"""
        response_times = []
        
        for i in range(20):
            start_time = time.time()
            
            try:
                result = health_check.invoke({})
                end_time = time.time()
                response_times.append(end_time - start_time)
            except Exception:
                pass
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Response times should be consistent
            time_variance = max_response_time - min_response_time
            self.assertLess(time_variance, 3.0,
                f"Response time variance ({time_variance:.2f}s) should be under 3s")
            
            # Average response time should be reasonable
            self.assertLess(avg_response_time, 2.0,
                f"Average response time ({avg_response_time:.2f}s) should be under 2s")


if __name__ == "__main__":
    # Run performance tests with increased verbosity
    unittest.main(verbosity=2)