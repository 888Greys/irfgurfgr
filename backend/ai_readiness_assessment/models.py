"""
Core data models for the AI Readiness Assessment Tool
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class SectionScore(BaseModel):
    """Represents the score for a single assessment section"""
    section_name: str = Field(..., description="Name of the assessment section", alias="section_id")
    questions: Dict[str, int] = Field(default_factory=dict, description="Question ID to score mapping (1-5)")
    section_total: int = Field(default=0, description="Total score for this section")
    max_possible: int = Field(default=0, description="Maximum possible score for this section")
    completion_status: bool = Field(default=False, description="Whether this section is completed")
    
    class Config:
        validate_by_name = True
    
    @validator('questions')
    def validate_question_scores(cls, v):
        """Validate that all scores are between 1 and 5"""
        for question_id, score in v.items():
            if not isinstance(score, int) or score < 1 or score > 5:
                raise ValueError(f"Score for question {question_id} must be between 1 and 5, got {score}")
        return v
    
    def calculate_totals(self):
        """Calculate section total and max possible scores"""
        self.section_total = sum(self.questions.values())
        self.max_possible = len(self.questions) * 5
        self.completion_status = len(self.questions) > 0
        return self
    
    @property
    def percentage(self) -> float:
        """Calculate percentage score"""
        if self.max_possible == 0:
            return 0.0
        return round((self.section_total / self.max_possible) * 100, 1)


class Recommendation(BaseModel):
    """Represents personalized recommendations based on assessment results"""
    readiness_level: str = Field(..., description="AI readiness level (Not Ready, Foundation Building, etc.)")
    priority_actions: List[str] = Field(default_factory=list, description="High-priority actions to take")
    timeline: str = Field(..., description="Recommended timeline for implementation")
    immediate_actions: List[str] = Field(default_factory=list, description="Actions to take in next 30 days")
    short_term_goals: List[str] = Field(default_factory=list, description="Goals for 3-6 months")
    long_term_vision: List[str] = Field(default_factory=list, description="Vision for 12+ months")
    kenya_specific_notes: List[str] = Field(default_factory=list, description="Kenya-specific recommendations")


class AssessmentState(BaseModel):
    """Main state object for tracking assessment progress"""
    user_id: str = Field(..., description="Unique identifier for the user")
    business_name: str = Field(..., description="Name of the business being assessed")
    industry: str = Field(..., description="Industry sector of the business")
    assessment_sections: Dict[str, SectionScore] = Field(default_factory=dict, description="Scores for each section")
    current_section: int = Field(default=0, description="Current section index (0-5)")
    total_score: int = Field(default=0, description="Total assessment score")
    readiness_level: str = Field(default="", description="Determined readiness level")
    started_at: datetime = Field(default_factory=datetime.now, description="When assessment was started")
    completed_at: Optional[datetime] = Field(default=None, description="When assessment was completed")
    progress: float = Field(default=0.0, description="Assessment completion progress (0.0-1.0)")
    
    @validator('current_section')
    def validate_current_section(cls, v):
        """Validate that current section is within valid range"""
        if v < 0 or v > 5:
            raise ValueError(f"Current section must be between 0 and 5, got {v}")
        return v
    
    @validator('progress')
    def validate_progress(cls, v):
        """Validate that progress is between 0.0 and 1.0"""
        if v < 0.0 or v > 1.0:
            raise ValueError(f"Progress must be between 0.0 and 1.0, got {v}")
        return v
    
    def calculate_total_score(self):
        """Calculate total score across all sections"""
        self.total_score = sum(section.section_total for section in self.assessment_sections.values())
        return self.total_score
    
    def calculate_progress(self):
        """Calculate assessment completion progress"""
        completed_sections = sum(1 for section in self.assessment_sections.values() if section.completion_status)
        self.progress = completed_sections / 6.0  # 6 total sections
        return self.progress
    
    def is_completed(self) -> bool:
        """Check if assessment is fully completed"""
        return len(self.assessment_sections) == 6 and all(
            section.completion_status for section in self.assessment_sections.values()
        )
    
    def get_readiness_level(self) -> str:
        """Determine readiness level based on total score"""
        total = self.calculate_total_score()
        
        if total <= 40:
            return "🔴 Not Ready"
        elif total <= 60:
            return "🟡 Foundation Building"
        elif total <= 75:
            return "🟠 Ready for Pilots"
        elif total <= 85:
            return "🟢 AI Ready"
        else:
            return "🔵 AI Advanced"

# Validation functions
def validate_assessment_data(data: dict) -> bool:
    """Validate assessment data structure"""
    try:
        required_fields = ["assessment_id", "user_id", "business_name"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                return False
        
        # Check sections structure
        if "sections" in data:
            sections = data["sections"]
            if not isinstance(sections, dict):
                return False
            
            for section_id, section_data in sections.items():
                if not isinstance(section_data, dict):
                    return False
                if "responses" not in section_data:
                    return False
        
        return True
        
    except Exception:
        return False


def validate_section_responses(section_id: str, responses: dict) -> bool:
    """Validate section responses"""
    try:
        # Check if responses is a dictionary
        if not isinstance(responses, dict):
            return False
        
        # Check score ranges (1-5)
        for question_id, score in responses.items():
            if not isinstance(score, int):
                return False
            if score < 1 or score > 5:
                return False
        
        return True
        
    except Exception:
        return False