"""
Assessment content and question management system
Contains all assessment questions, scoring rubrics, and content management functions
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .models import SectionScore


@dataclass
class Question:
    """Represents a single assessment question"""
    id: str
    question: str
    description: str
    scoring_rubric: Dict[int, str]  # score -> description
    section_id: str
    section_name: str


@dataclass
class AssessmentSection:
    """Represents a complete assessment section"""
    id: str
    name: str
    description: str
    max_points: int
    questions: List[Question]


class AssessmentContent:
    """Manages all assessment content and questions"""
    
    def __init__(self):
        self.sections = self._load_assessment_sections()
        self.questions_by_id = self._build_question_index()
    
    def _load_assessment_sections(self) -> List[AssessmentSection]:
        """Load all assessment sections and questions"""
        
        # Section 1: Data Infrastructure & Quality (25 points)
        section1_questions = [
            Question(
                id="data_collection_processes",
                question="How systematic and structured are your data collection processes?",
                description="Data Collection Processes",
                scoring_rubric={
                    1: "Ad-hoc: No formal processes, data collected inconsistently when needed",
                    2: "Basic: Some informal processes, limited standardization across departments",
                    3: "Structured: Defined processes for key data types, some automation in place",
                    4: "Systematic: Well-defined processes with quality controls and regular validation",
                    5: "Advanced: Fully automated, standardized processes with real-time quality monitoring"
                },
                section_id="section1",
                section_name="Data Infrastructure & Quality"
            ),
            Question(
                id="1.1",
                question="How much business data do you currently collect and store digitally?",
                description="Data Availability",
                scoring_rubric={
                    1: "Minimal: Less than 20% of business processes generate digital data",
                    2: "Limited: 20-40% of processes generate digital data, mostly basic records",
                    3: "Moderate: 40-60% of processes digitized, some customer and operational data",
                    4: "Good: 60-80% digital, comprehensive customer, sales, and operational data",
                    5: "Excellent: 80%+ fully digital operations with rich, detailed data across all functions"
                },
                section_id="section1",
                section_name="Data Infrastructure & Quality"
            ),
            Question(
                id="1.2",
                question="How would you rate the accuracy, completeness, and consistency of your business data?",
                description="Data Quality",
                scoring_rubric={
                    1: "Poor: Significant gaps, errors, and inconsistencies in most data",
                    2: "Below Average: Some data quality issues, requires substantial cleaning",
                    3: "Average: Generally reliable but needs regular cleaning and validation",
                    4: "Good: High quality with minor issues, occasional cleaning needed",
                    5: "Excellent: Very high quality, standardized, regularly validated data"
                },
                section_id="section1",
                section_name="Data Infrastructure & Quality"
            ),
            Question(
                id="1.3",
                question="How well are your different business systems connected and able to share data?",
                description="Data Integration",
                scoring_rubric={
                    1: "Isolated: Systems operate in silos, manual data transfer required",
                    2: "Limited: Some basic integrations, mostly manual processes",
                    3: "Moderate: Key systems connected, some automated data flow",
                    4: "Good: Most systems integrated with automated data sharing",
                    5: "Excellent: Fully integrated data ecosystem with real-time synchronization"
                },
                section_id="section1",
                section_name="Data Infrastructure & Quality"
            ),
            Question(
                id="1.4",
                question="Do you have policies and procedures for managing data access, quality, and security?",
                description="Data Governance",
                scoring_rubric={
                    1: "None: No formal data governance policies or procedures",
                    2: "Basic: Informal practices, no documented policies",
                    3: "Developing: Some policies documented, inconsistent implementation",
                    4: "Established: Clear policies and procedures, mostly followed",
                    5: "Mature: Comprehensive governance framework, consistently enforced"
                },
                section_id="section1",
                section_name="Data Infrastructure & Quality"
            ),
            Question(
                id="1.5",
                question="What is your current capacity for storing and processing large amounts of data?",
                description="Data Storage & Processing Capacity",
                scoring_rubric={
                    1: "Limited: Basic storage, manual processing, frequent capacity issues",
                    2: "Basic: Adequate storage for current needs, limited processing power",
                    3: "Moderate: Good storage and processing for current operations",
                    4: "Good: Scalable infrastructure that can handle growth",
                    5: "Excellent: Advanced cloud/hybrid infrastructure with auto-scaling capabilities"
                },
                section_id="section1",
                section_name="Data Infrastructure & Quality"
            )
        ]
        
        # Section 2: Technology Infrastructure (20 points)
        section2_questions = [
            Question(
                id="2.1",
                question="How modern and capable are your current IT systems?",
                description="IT Systems Maturity",
                scoring_rubric={
                    1: "Legacy: Outdated systems, limited functionality, frequent issues",
                    2: "Basic: Older systems that meet basic needs with some limitations",
                    3: "Standard: Modern systems for core functions, some integration possible",
                    4: "Advanced: Up-to-date systems with good integration capabilities",
                    5: "Cutting-edge: Latest technology stack with AI-ready architecture"
                },
                section_id="section2",
                section_name="Technology Infrastructure"
            ),
            Question(
                id="2.2",
                question="What is your current cloud computing adoption level?",
                description="Cloud Readiness",
                scoring_rubric={
                    1: "None: All systems on-premise, no cloud experience",
                    2: "Minimal: Limited cloud usage (email, basic storage)",
                    3: "Moderate: Some applications in cloud, hybrid approach",
                    4: "Significant: Most systems cloud-based or cloud-ready",
                    5: "Full: Cloud-native operations with advanced services usage"
                },
                section_id="section2",
                section_name="Technology Infrastructure"
            ),
            Question(
                id="2.3",
                question="How reliable and fast is your internet connectivity?",
                description="Internet & Connectivity",
                scoring_rubric={
                    1: "Poor: Frequent outages, very slow speeds, limits operations",
                    2: "Unreliable: Occasional outages, adequate speeds for basic operations",
                    3: "Adequate: Generally reliable, sufficient for current needs",
                    4: "Good: Reliable high-speed connection with backup options",
                    5: "Excellent: Enterprise-grade connectivity with redundancy and high availability"
                },
                section_id="section2",
                section_name="Technology Infrastructure"
            ),
            Question(
                id="2.4",
                question="How comprehensive are your current cybersecurity measures?",
                description="Security Infrastructure",
                scoring_rubric={
                    1: "Minimal: Basic antivirus, limited security measures",
                    2: "Basic: Standard security software, basic access controls",
                    3: "Standard: Good security practices, some advanced measures",
                    4: "Advanced: Comprehensive security suite, regular updates and monitoring",
                    5: "Enterprise: Advanced threat detection, incident response, compliance frameworks"
                },
                section_id="section2",
                section_name="Technology Infrastructure"
            )
        ]
        
        # Section 3: Human Resources & Skills (20 points)
        section3_questions = [
            Question(
                id="3.1",
                question="What level of technical expertise exists in your organization?",
                description="Technical Skills",
                scoring_rubric={
                    1: "Limited: Basic computer skills, no advanced technical capabilities",
                    2: "Basic: Some technical skills, can manage standard software",
                    3: "Moderate: Good technical skills, can learn and adapt to new tools",
                    4: "Advanced: Strong technical team, some data analysis capabilities",
                    5: "Expert: Data scientists, developers, or AI specialists on staff"
                },
                section_id="section3",
                section_name="Human Resources & Skills"
            ),
            Question(
                id="3.2",
                question="How comfortable is your team with analyzing and using data for decision-making?",
                description="Data Literacy",
                scoring_rubric={
                    1: "Low: Decisions based on intuition, limited data usage",
                    2: "Basic: Some data analysis, mostly basic reports",
                    3: "Moderate: Regular use of data for decisions, basic analytics",
                    4: "Good: Data-driven culture, advanced analytics usage",
                    5: "High: Strong analytical capabilities, data science expertise"
                },
                section_id="section3",
                section_name="Human Resources & Skills"
            ),
            Question(
                id="3.3",
                question="How well does your organization adapt to new technologies and processes?",
                description="Change Management Capability",
                scoring_rubric={
                    1: "Resistant: Strong resistance to change, slow adoption of new tools",
                    2: "Cautious: Slow to adopt new technologies, prefers familiar methods",
                    3: "Moderate: Open to change with proper support and training",
                    4: "Adaptable: Quick to learn and implement new technologies",
                    5: "Innovative: Embraces change, actively seeks new technological solutions"
                },
                section_id="section3",
                section_name="Human Resources & Skills"
            ),
            Question(
                id="3.4",
                question="How committed is senior leadership to digital transformation and AI adoption?",
                description="Leadership Support",
                scoring_rubric={
                    1: "Skeptical: Leadership questions value of new technology investments",
                    2: "Cautious: Some interest but limited commitment to change",
                    3: "Supportive: Generally supportive with adequate budget allocation",
                    4: "Championing: Strong support with significant resource commitment",
                    5: "Visionary: AI/digital transformation is a strategic priority with full backing"
                },
                section_id="section3",
                section_name="Human Resources & Skills"
            )
        ]
        
        # Section 4: Business Process Maturity (15 points)
        section4_questions = [
            Question(
                id="4.1",
                question="How well are your business processes documented and standardized?",
                description="Process Documentation",
                scoring_rubric={
                    1: "Informal: Processes exist in people's heads, no documentation",
                    2: "Basic: Some key processes documented informally",
                    3: "Standard: Most processes documented with basic standardization",
                    4: "Comprehensive: Well-documented, standardized processes",
                    5: "Optimized: Detailed process documentation with continuous improvement"
                },
                section_id="section4",
                section_name="Business Process Maturity"
            ),
            Question(
                id="4.2",
                question="What percentage of your routine business processes are currently automated?",
                description="Process Automation Level",
                scoring_rubric={
                    1: "Manual: Less than 10% automation, mostly manual processes",
                    2: "Limited: 10-25% automation, basic tools usage",
                    3: "Moderate: 25-50% automation, some workflow tools",
                    4: "Significant: 50-75% automation, advanced workflow systems",
                    5: "High: 75%+ automation, sophisticated process management"
                },
                section_id="section4",
                section_name="Business Process Maturity"
            ),
            Question(
                id="4.3",
                question="How well do you measure and track business process performance?",
                description="Performance Measurement",
                scoring_rubric={
                    1: "Minimal: Limited measurement, mostly financial metrics",
                    2: "Basic: Some KPIs tracked, irregular monitoring",
                    3: "Standard: Regular KPI tracking, basic performance management",
                    4: "Advanced: Comprehensive metrics, dashboards, regular analysis",
                    5: "Sophisticated: Real-time monitoring, predictive analytics, continuous optimization"
                },
                section_id="section4",
                section_name="Business Process Maturity"
            )
        ]
        
        # Section 5: Strategic & Financial Readiness (10 points)
        section5_questions = [
            Question(
                id="5.1",
                question="How clear is your organization's digital transformation strategy?",
                description="Strategic Vision",
                scoring_rubric={
                    1: "None: No digital strategy or vision",
                    2: "Vague: Some ideas but no formal strategy",
                    3: "Developing: Strategy in development, some clarity",
                    4: "Clear: Well-defined digital transformation strategy",
                    5: "Comprehensive: Detailed AI/digital strategy with clear roadmap"
                },
                section_id="section5",
                section_name="Strategic & Financial Readiness"
            ),
            Question(
                id="5.2",
                question="What percentage of your annual budget is allocated to technology and innovation?",
                description="Budget Allocation",
                scoring_rubric={
                    1: "Minimal: Less than 2% of budget for technology",
                    2: "Limited: 2-5% budget allocation for technology",
                    3: "Standard: 5-10% allocated to technology improvements",
                    4: "Significant: 10-15% budget for technology and innovation",
                    5: "Strategic: 15%+ investment in technology as competitive advantage"
                },
                section_id="section5",
                section_name="Strategic & Financial Readiness"
            )
        ]
        
        # Section 6: Regulatory & Compliance Readiness (10 points)
        section6_questions = [
            Question(
                id="6.1",
                question="How well does your organization comply with Kenya's Data Protection Act 2019?",
                description="Data Protection Compliance",
                scoring_rubric={
                    1: "Unaware: Not familiar with requirements, no compliance measures",
                    2: "Aware: Know requirements exist but limited compliance",
                    3: "Developing: Working towards compliance, some measures in place",
                    4: "Compliant: Generally compliant with most requirements",
                    5: "Exemplary: Full compliance with best practices implementation"
                },
                section_id="section6",
                section_name="Regulatory & Compliance Readiness"
            ),
            Question(
                id="6.2",
                question="How mature is your organization's approach to managing technology and data risks?",
                description="Risk Management Framework",
                scoring_rubric={
                    1: "Informal: No formal risk management for technology",
                    2: "Basic: Some awareness of risks, informal management",
                    3: "Developing: Risk assessment processes being developed",
                    4: "Established: Formal risk management framework in place",
                    5: "Mature: Comprehensive risk management with regular assessments"
                },
                section_id="section6",
                section_name="Regulatory & Compliance Readiness"
            )
        ]
        
        # Create sections
        sections = [
            AssessmentSection(
                id="section1",
                name="Data Infrastructure & Quality",
                description="Evaluate your organization's data collection, quality, integration, governance, and processing capabilities",
                max_points=25,
                questions=section1_questions
            ),
            AssessmentSection(
                id="section2", 
                name="Technology Infrastructure",
                description="Assess your IT systems maturity, cloud readiness, connectivity, and security infrastructure",
                max_points=20,
                questions=section2_questions
            ),
            AssessmentSection(
                id="section3",
                name="Human Resources & Skills",
                description="Evaluate technical skills, data literacy, change management capability, and leadership support",
                max_points=20,
                questions=section3_questions
            ),
            AssessmentSection(
                id="section4",
                name="Business Process Maturity",
                description="Assess process documentation, automation level, and performance measurement capabilities",
                max_points=15,
                questions=section4_questions
            ),
            AssessmentSection(
                id="section5",
                name="Strategic & Financial Readiness",
                description="Evaluate strategic vision and budget allocation for digital transformation",
                max_points=10,
                questions=section5_questions
            ),
            AssessmentSection(
                id="section6",
                name="Regulatory & Compliance Readiness",
                description="Assess compliance with data protection laws and risk management frameworks",
                max_points=10,
                questions=section6_questions
            )
        ]
        
        return sections
    
    def _build_question_index(self) -> Dict[str, Question]:
        """Build an index of all questions by ID for quick lookup"""
        index = {}
        for section in self.sections:
            for question in section.questions:
                index[question.id] = question
        return index
    
    def get_section(self, section_id: str) -> Optional[AssessmentSection]:
        """Get a section by ID"""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """Get a question by ID"""
        return self.questions_by_id.get(question_id)
    
    def get_all_sections(self) -> List[AssessmentSection]:
        """Get all assessment sections"""
        return self.sections
    
    def get_section_questions(self, section_id: str) -> List[Question]:
        """Get all questions for a specific section"""
        section = self.get_section(section_id)
        return section.questions if section else []
    
    def validate_section_responses(self, section_id: str, responses: Dict[str, int]) -> tuple[bool, List[str]]:
        """Validate responses for a section"""
        errors = []
        section = self.get_section(section_id)
        
        if not section:
            return False, [f"Invalid section ID: {section_id}"]
        
        # Check all questions are answered
        expected_questions = {q.id for q in section.questions}
        provided_questions = set(responses.keys())
        
        missing = expected_questions - provided_questions
        if missing:
            errors.append(f"Missing responses for questions: {', '.join(missing)}")
        
        extra = provided_questions - expected_questions
        if extra:
            errors.append(f"Unexpected question responses: {', '.join(extra)}")
        
        # Validate score ranges
        for question_id, score in responses.items():
            if question_id in expected_questions:
                if not isinstance(score, int) or score < 1 or score > 5:
                    errors.append(f"Question {question_id}: Score must be between 1 and 5, got {score}")
        
        return len(errors) == 0, errors
    
    def create_section_score(self, section_id: str, responses: Dict[str, int]) -> Optional[SectionScore]:
        """Create a SectionScore object from responses"""
        section = self.get_section(section_id)
        if not section:
            return None
        
        is_valid, errors = self.validate_section_responses(section_id, responses)
        if not is_valid:
            raise ValueError(f"Invalid responses: {'; '.join(errors)}")
        
        section_score = SectionScore(
            section_name=section.name,
            questions=responses
        )
        section_score.calculate_totals()
        
        return section_score
    
    def get_total_possible_score(self) -> int:
        """Get the total possible score across all sections"""
        return sum(section.max_points for section in self.sections)
    
    def get_section_summary(self) -> Dict[str, Any]:
        """Get a summary of all sections"""
        return {
            "total_sections": len(self.sections),
            "total_questions": sum(len(section.questions) for section in self.sections),
            "total_possible_score": self.get_total_possible_score(),
            "sections": [
                {
                    "id": section.id,
                    "name": section.name,
                    "description": section.description,
                    "max_points": section.max_points,
                    "question_count": len(section.questions)
                }
                for section in self.sections
            ]
        }