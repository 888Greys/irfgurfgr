"""
Test runner for the comprehensive testing suite
Orchestrates all test categories and provides reporting
"""

import unittest
import sys
import time
import json
from io import StringIO
from datetime import datetime
from typing import Dict, List, Any

# Import all test modules
from . import test_models
from . import test_integration
from . import test_scenarios
from . import test_performance


class TestResult:
    """Custom test result class for detailed reporting"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.tests_run = 0
        self.failures = []
        self.errors = []
        self.skipped = []
        self.successes = []
        self.test_details = {}
    
    def start_test(self, test):
        """Called when a test starts"""
        self.start_time = time.time()
        test_name = f"{test.__class__.__module__}.{test.__class__.__name__}.{test._testMethodName}"
        self.test_details[test_name] = {"start_time": self.start_time}
    
    def stop_test(self, test):
        """Called when a test ends"""
        self.end_time = time.time()
        test_name = f"{test.__class__.__module__}.{test.__class__.__name__}.{test._testMethodName}"
        if test_name in self.test_details:
            self.test_details[test_name]["end_time"] = self.end_time
            self.test_details[test_name]["duration"] = self.end_time - self.test_details[test_name]["start_time"]
    
    def add_success(self, test):
        """Called when a test passes"""
        self.tests_run += 1
        test_name = f"{test.__class__.__module__}.{test.__class__.__name__}.{test._testMethodName}"
        self.successes.append(test_name)
        if test_name in self.test_details:
            self.test_details[test_name]["status"] = "PASS"
    
    def add_error(self, test, err):
        """Called when a test has an error"""
        self.tests_run += 1
        test_name = f"{test.__class__.__module__}.{test.__class__.__name__}.{test._testMethodName}"
        self.errors.append((test_name, err))
        if test_name in self.test_details:
            self.test_details[test_name]["status"] = "ERROR"
            self.test_details[test_name]["error"] = str(err[1])
    
    def add_failure(self, test, err):
        """Called when a test fails"""
        self.tests_run += 1
        test_name = f"{test.__class__.__module__}.{test.__class__.__name__}.{test._testMethodName}"
        self.failures.append((test_name, err))
        if test_name in self.test_details:
            self.test_details[test_name]["status"] = "FAIL"
            self.test_details[test_name]["failure"] = str(err[1])
    
    def add_skip(self, test, reason):
        """Called when a test is skipped"""
        test_name = f"{test.__class__.__module__}.{test.__class__.__name__}.{test._testMethodName}"
        self.skipped.append((test_name, reason))
        if test_name in self.test_details:
            self.test_details[test_name]["status"] = "SKIP"
            self.test_details[test_name]["skip_reason"] = reason


class ComprehensiveTestRunner:
    """Comprehensive test runner with detailed reporting"""
    
    def __init__(self, verbosity=2):
        self.verbosity = verbosity
        self.test_suites = {
            "models": test_models,
            "integration": test_integration,
            "scenarios": test_scenarios,
            "performance": test_performance
        }
        self.results = {}
        self.overall_start_time = None
        self.overall_end_time = None
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and return comprehensive results"""
        print("=" * 80)
        print("AI READINESS ASSESSMENT - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.overall_start_time = time.time()
        
        # Run each test suite
        for suite_name, test_module in self.test_suites.items():
            print(f"Running {suite_name.upper()} tests...")
            print("-" * 50)
            
            suite_result = self._run_test_suite(suite_name, test_module)
            self.results[suite_name] = suite_result
            
            self._print_suite_summary(suite_name, suite_result)
            print()
        
        self.overall_end_time = time.time()
        
        # Generate comprehensive report
        overall_report = self._generate_overall_report()
        self._print_overall_summary(overall_report)
        
        return overall_report
    
    def _run_test_suite(self, suite_name: str, test_module) -> Dict[str, Any]:
        """Run a specific test suite"""
        # Capture stdout to get test output
        old_stdout = sys.stdout
        test_output = StringIO()
        
        try:
            # Create test loader and suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Create custom test result
            result = TestResult()
            
            # Run tests with custom result
            start_time = time.time()
            
            # Temporarily redirect stdout if not verbose
            if self.verbosity < 2:
                sys.stdout = test_output
            
            # Run the test suite
            for test_case in suite:
                for test in test_case:
                    result.start_test(test)
                    try:
                        test.debug()
                        result.add_success(test)
                    except AssertionError as e:
                        result.add_failure(test, (type(e), e, None))
                    except Exception as e:
                        result.add_error(test, (type(e), e, None))
                    finally:
                        result.stop_test(test)
            
            end_time = time.time()
            
            # Restore stdout
            sys.stdout = old_stdout
            
            # Compile results
            suite_result = {
                "suite_name": suite_name,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "tests_run": result.tests_run,
                "successes": len(result.successes),
                "failures": len(result.failures),
                "errors": len(result.errors),
                "skipped": len(result.skipped),
                "success_rate": (len(result.successes) / result.tests_run * 100) if result.tests_run > 0 else 0,
                "test_details": result.test_details,
                "failure_details": result.failures,
                "error_details": result.errors,
                "output": test_output.getvalue()
            }
            
            return suite_result
            
        except Exception as e:
            sys.stdout = old_stdout
            return {
                "suite_name": suite_name,
                "error": f"Failed to run test suite: {str(e)}",
                "tests_run": 0,
                "successes": 0,
                "failures": 0,
                "errors": 1,
                "skipped": 0,
                "success_rate": 0
            }
    
    def _print_suite_summary(self, suite_name: str, result: Dict[str, Any]):
        """Print summary for a test suite"""
        if "error" in result:
            print(f"❌ {suite_name.upper()} SUITE FAILED: {result['error']}")
            return
        
        tests_run = result["tests_run"]
        successes = result["successes"]
        failures = result["failures"]
        errors = result["errors"]
        success_rate = result["success_rate"]
        duration = result["duration"]
        
        status_icon = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 70 else "❌"
        
        print(f"{status_icon} {suite_name.upper()} RESULTS:")
        print(f"   Tests Run: {tests_run}")
        print(f"   Passed: {successes}")
        print(f"   Failed: {failures}")
        print(f"   Errors: {errors}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Duration: {duration:.2f}s")
        
        # Show failures and errors if any
        if failures > 0:
            print(f"   ⚠️  Failures:")
            for failure_name, failure_details in result["failure_details"][:3]:  # Show first 3
                print(f"      - {failure_name.split('.')[-1]}")
        
        if errors > 0:
            print(f"   ❌ Errors:")
            for error_name, error_details in result["error_details"][:3]:  # Show first 3
                print(f"      - {error_name.split('.')[-1]}")
    
    def _generate_overall_report(self) -> Dict[str, Any]:
        """Generate overall test report"""
        total_tests = sum(result.get("tests_run", 0) for result in self.results.values())
        total_successes = sum(result.get("successes", 0) for result in self.results.values())
        total_failures = sum(result.get("failures", 0) for result in self.results.values())
        total_errors = sum(result.get("errors", 0) for result in self.results.values())
        total_skipped = sum(result.get("skipped", 0) for result in self.results.values())
        
        overall_success_rate = (total_successes / total_tests * 100) if total_tests > 0 else 0
        total_duration = self.overall_end_time - self.overall_start_time
        
        # Calculate suite-specific metrics
        suite_metrics = {}
        for suite_name, result in self.results.items():
            if "error" not in result:
                suite_metrics[suite_name] = {
                    "success_rate": result["success_rate"],
                    "duration": result["duration"],
                    "tests_run": result["tests_run"],
                    "status": "PASS" if result["success_rate"] >= 90 else "WARN" if result["success_rate"] >= 70 else "FAIL"
                }
            else:
                suite_metrics[suite_name] = {
                    "success_rate": 0,
                    "duration": 0,
                    "tests_run": 0,
                    "status": "ERROR"
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "total_tests": total_tests,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "total_errors": total_errors,
            "total_skipped": total_skipped,
            "overall_success_rate": overall_success_rate,
            "suite_metrics": suite_metrics,
            "detailed_results": self.results,
            "system_status": self._determine_system_status(overall_success_rate, suite_metrics)
        }
    
    def _determine_system_status(self, overall_success_rate: float, suite_metrics: Dict) -> str:
        """Determine overall system status based on test results"""
        if overall_success_rate >= 95:
            return "EXCELLENT"
        elif overall_success_rate >= 85:
            return "GOOD"
        elif overall_success_rate >= 70:
            return "ACCEPTABLE"
        elif overall_success_rate >= 50:
            return "NEEDS_IMPROVEMENT"
        else:
            return "CRITICAL"
    
    def _print_overall_summary(self, report: Dict[str, Any]):
        """Print overall test summary"""
        print("=" * 80)
        print("OVERALL TEST RESULTS")
        print("=" * 80)
        
        status = report["system_status"]
        status_icons = {
            "EXCELLENT": "🟢",
            "GOOD": "🟡",
            "ACCEPTABLE": "🟠",
            "NEEDS_IMPROVEMENT": "🔴",
            "CRITICAL": "💀"
        }
        
        print(f"System Status: {status_icons.get(status, '❓')} {status}")
        print(f"Overall Success Rate: {report['overall_success_rate']:.1f}%")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['total_successes']}")
        print(f"Failed: {report['total_failures']}")
        print(f"Errors: {report['total_errors']}")
        print(f"Total Duration: {report['total_duration']:.2f}s")
        print()
        
        print("Suite Breakdown:")
        for suite_name, metrics in report["suite_metrics"].items():
            status_icon = "✅" if metrics["status"] == "PASS" else "⚠️" if metrics["status"] == "WARN" else "❌"
            print(f"  {status_icon} {suite_name.capitalize()}: {metrics['success_rate']:.1f}% ({metrics['tests_run']} tests)")
        
        print()
        print("Recommendations:")
        self._print_recommendations(report)
        
        print("=" * 80)
    
    def _print_recommendations(self, report: Dict[str, Any]):
        """Print recommendations based on test results"""
        recommendations = []
        
        overall_rate = report["overall_success_rate"]
        
        if overall_rate < 70:
            recommendations.append("🔴 CRITICAL: System has significant issues that need immediate attention")
        elif overall_rate < 85:
            recommendations.append("🟠 WARNING: System has some issues that should be addressed")
        elif overall_rate < 95:
            recommendations.append("🟡 GOOD: System is mostly stable with minor issues")
        else:
            recommendations.append("🟢 EXCELLENT: System is performing well")
        
        # Suite-specific recommendations
        for suite_name, metrics in report["suite_metrics"].items():
            if metrics["success_rate"] < 70:
                recommendations.append(f"   - Focus on fixing {suite_name} test failures")
            elif metrics["success_rate"] < 90:
                recommendations.append(f"   - Review {suite_name} test warnings")
        
        # Performance recommendations
        if "performance" in report["suite_metrics"]:
            perf_metrics = report["suite_metrics"]["performance"]
            if perf_metrics["success_rate"] < 80:
                recommendations.append("   - Performance optimization needed")
        
        for rec in recommendations:
            print(rec)
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save test report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Test report saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {str(e)}")


def run_specific_suite(suite_name: str):
    """Run a specific test suite"""
    runner = ComprehensiveTestRunner(verbosity=2)
    
    if suite_name not in runner.test_suites:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(runner.test_suites.keys())}")
        return
    
    print(f"Running {suite_name} test suite...")
    test_module = runner.test_suites[suite_name]
    result = runner._run_test_suite(suite_name, test_module)
    runner._print_suite_summary(suite_name, result)


def main():
    """Main entry point for test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Readiness Assessment Test Runner")
    parser.add_argument("--suite", help="Run specific test suite", 
                       choices=["models", "integration", "scenarios", "performance"])
    parser.add_argument("--save-report", help="Save detailed report to file", action="store_true")
    parser.add_argument("--verbose", "-v", help="Verbose output", action="store_true")
    
    args = parser.parse_args()
    
    if args.suite:
        run_specific_suite(args.suite)
    else:
        # Run all tests
        runner = ComprehensiveTestRunner(verbosity=2 if args.verbose else 1)
        report = runner.run_all_tests()
        
        if args.save_report:
            runner.save_report(report)


if __name__ == "__main__":
    main()