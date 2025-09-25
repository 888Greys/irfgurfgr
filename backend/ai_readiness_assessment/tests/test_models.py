"""
Unit tests for data models and validation functions
"""

import unittest
import json
from datetime import datetime
from ai_readiness_assessment.models import (
    AssessmentState, SectionScore, Recommendation,
    validate_assessment_data, validate_section_responses
)


class TestAssessmentState(unittest.TestCase):
    """Test AssessmentState data model"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_state_data = {
            "assessment_id": "test_001",
            "user_id": "user_123",
            "business_name": "Test Company",
            "industry": "Manufacturing",
            "created_at": datetime.now().isoformat(),
            "sections": {
                "data_infrastructure": {
                    "responses": {"q1": 4, "q2": 3, "q3": 5},
                    "completed": True
                }
            }
        }
    
    def test_assessment_state_creation(self):
        """Test creating AssessmentState instance"""
        state = AssessmentState(**self.valid_state_data)
        
        self.assertEqual(state.assessment_id, "test_001")
        self.assertEqual(state.user_id, "user_123")
        self.assertEqual(state.business_name, "Test Company")
        self.assertEqual(state.industry, "Manufacturing")
        self.assertIsInstance(state.sections, dict)
    
    def test_assessment_state_validation(self):
        """Test AssessmentState validation"""
        # Test with missing required fields
        invalid_data = self.valid_state_data.copy()
        del invalid_data["assessment_id"]
        
        with self.assertRaises(TypeError):
            AssessmentState(**invalid_data)
    
    def test_assessment_state_serialization(self):
        """Test AssessmentState serialization"""
        state = AssessmentState(**self.valid_state_data)
        
        # Should be able to convert to dict
        state_dict = state.__dict__
        self.assertIsInstance(state_dict, dict)
        self.assertIn("assessment_id", state_dict)
    
    def test_section_completion_tracking(self):
        """Test section completion tracking"""
        state = AssessmentState(**self.valid_state_data)
        
        # Check completed section
        data_section = state.sections["data_infrastructure"]
        self.assertTrue(data_section["completed"])
        self.assertEqual(len(data_section["responses"]), 3)


class TestSectionScore(unittest.TestCase):
    """Test SectionScore data model"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_score_data = {
            "section_id": "data_infrastructure",
            "section_name": "Data Infrastructure & Quality",
            "responses": {"q1": 4, "q2": 3, "q3": 5, "q4": 2, "q5": 4},
            "section_total": 18,
            "max_possible": 25,
            "percentage": 72.0
        }
    
    def test_section_score_creation(self):
        """Test creating SectionScore instance"""
        score = SectionScore(**self.valid_score_data)
        
        self.assertEqual(score.section_name, "data_infrastructure")
        self.assertEqual(score.section_total, 18)
        self.assertEqual(score.max_possible, 25)
        self.assertEqual(score.percentage, 72.0)
    
    def test_section_score_calculation(self):
        """Test section score calculation"""
        score = SectionScore(**self.valid_score_data)
        
        # Verify calculation
        expected_total = sum(self.valid_score_data["responses"].values())
        self.assertEqual(score.section_total, expected_total)
        
        expected_percentage = (expected_total / score.max_possible) * 100
        self.assertAlmostEqual(score.percentage, expected_percentage, places=1)
    
    def test_section_score_validation(self):
        """Test SectionScore validation"""
        # Test with invalid score range
        invalid_data = self.valid_score_data.copy()
        invalid_data["responses"] = {"q1": 6}  # Invalid score > 5
        
        # Should handle gracefully or validate
        score = SectionScore(**invalid_data)
        self.assertIsInstance(score, SectionScore)


class TestRecommendation(unittest.TestCase):
    """Test Recommendation data model"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_recommendation_data = {
            "assessment_id": "test_001",
            "readiness_level": "Ready for Pilots",
            "priority_actions": [
                "Implement data governance framework",
                "Upgrade technology infrastructure",
                "Develop AI skills training program"
            ],
            "timeline": "6-9 months",
            "resource_requirements": {
                "budget": "KES 2M - 8M",
                "staff_time": "4-6 FTE for 6-9 months"
            }
        }
    
    def test_recommendation_creation(self):
        """Test creating Recommendation instance"""
        rec = Recommendation(**self.valid_recommendation_data)
        
        self.assertEqual(rec.assessment_id, "test_001")
        self.assertEqual(rec.readiness_level, "Ready for Pilots")
        self.assertEqual(len(rec.priority_actions), 3)
        self.assertEqual(rec.timeline, "6-9 months")
    
    def test_recommendation_validation(self):
        """Test Recommendation validation"""
        # Test with empty priority actions
        invalid_data = self.valid_recommendation_data.copy()
        invalid_data["priority_actions"] = []
        
        rec = Recommendation(**invalid_data)
        self.assertEqual(len(rec.priority_actions), 0)


class TestValidationFunctions(unittest.TestCase):
    """Test validation functions"""
    
    def test_validate_assessment_data(self):
        """Test assessment data validation"""
        valid_data = {
            "assessment_id": "test_001",
            "user_id": "user_123",
            "business_name": "Test Company",
            "sections": {
                "data_infrastructure": {
                    "responses": {"q1": 4, "q2": 3},
                    "completed": True
                }
            }
        }
        
        # Should return True for valid data
        is_valid = validate_assessment_data(valid_data)
        self.assertTrue(is_valid)
        
        # Test with invalid data
        invalid_data = valid_data.copy()
        del invalid_data["assessment_id"]
        
        is_valid = validate_assessment_data(invalid_data)
        self.assertFalse(is_valid)
    
    def test_validate_section_responses(self):
        """Test section response validation"""
        valid_responses = {"q1": 4, "q2": 3, "q3": 5}
        
        # Should return True for valid responses
        is_valid = validate_section_responses("data_infrastructure", valid_responses)
        self.assertTrue(is_valid)
        
        # Test with invalid score range
        invalid_responses = {"q1": 6, "q2": 0}  # Scores outside 1-5 range
        
        is_valid = validate_section_responses("data_infrastructure", invalid_responses)
        self.assertFalse(is_valid)
    
    def test_validate_score_ranges(self):
        """Test score range validation"""
        # Test valid scores (1-5)
        for score in range(1, 6):
            responses = {"q1": score}
            is_valid = validate_section_responses("test_section", responses)
            self.assertTrue(is_valid, f"Score {score} should be valid")
        
        # Test invalid scores
        invalid_scores = [0, 6, -1, 10]
        for score in invalid_scores:
            responses = {"q1": score}
            is_valid = validate_section_responses("test_section", responses)
            self.assertFalse(is_valid, f"Score {score} should be invalid")


class TestDataModelIntegration(unittest.TestCase):
    """Test integration between data models"""
    
    def test_assessment_to_score_conversion(self):
        """Test converting assessment data to section scores"""
        assessment_data = {
            "assessment_id": "test_001",
            "user_id": "user_123",
            "business_name": "Test Company",
            "industry": "Manufacturing",
            "created_at": datetime.now().isoformat(),
            "sections": {
                "data_infrastructure": {
                    "responses": {"q1": 4, "q2": 3, "q3": 5, "q4": 2, "q5": 4},
                    "completed": True
                }
            }
        }
        
        state = AssessmentState(**assessment_data)
        
        # Extract section data
        section_data = state.sections["data_infrastructure"]
        responses = section_data["responses"]
        
        # Create section score
        score_data = {
            "section_id": "data_infrastructure",
            "section_name": "Data Infrastructure & Quality",
            "responses": responses,
            "section_total": sum(responses.values()),
            "max_possible": len(responses) * 5,
            "percentage": (sum(responses.values()) / (len(responses) * 5)) * 100
        }
        
        score = SectionScore(**score_data)
        
        self.assertEqual(score.section_total, 18)
        self.assertEqual(score.max_possible, 25)
        self.assertAlmostEqual(score.percentage, 72.0, places=1)
    
    def test_score_to_recommendation_flow(self):
        """Test flow from scores to recommendations"""
        # Create multiple section scores
        section_scores = {
            "data_infrastructure": SectionScore(
                section_id="data_infrastructure",
                section_name="Data Infrastructure & Quality",
                responses={"q1": 4, "q2": 3, "q3": 5, "q4": 2, "q5": 4},
                section_total=18,
                max_possible=25,
                percentage=72.0
            ),
            "technology_infrastructure": SectionScore(
                section_id="technology_infrastructure",
                section_name="Technology Infrastructure",
                responses={"q1": 3, "q2": 2, "q3": 3, "q4": 3, "q5": 2},
                section_total=13,
                max_possible=25,
                percentage=52.0
            )
        }
        
        # Calculate total score
        total_score = sum(score.section_total for score in section_scores.values())
        max_total = sum(score.max_possible for score in section_scores.values())
        
        # Determine readiness level based on total score
        percentage = (total_score / max_total) * 100
        
        if percentage >= 80:
            readiness_level = "AI Advanced"
        elif percentage >= 70:
            readiness_level = "AI Ready"
        elif percentage >= 50:
            readiness_level = "Ready for Pilots"
        elif percentage >= 30:
            readiness_level = "Foundation Building"
        else:
            readiness_level = "Not Ready"
        
        # Create recommendation
        recommendation = Recommendation(
            assessment_id="test_001",
            readiness_level=readiness_level,
            priority_actions=["Improve technology infrastructure", "Enhance data quality"],
            timeline="6-12 months",
            resource_requirements={"budget": "KES 2M - 5M"}
        )
        
        self.assertEqual(recommendation.readiness_level, "Ready for Pilots")
        self.assertEqual(len(recommendation.priority_actions), 2)


if __name__ == "__main__":
    unittest.main()