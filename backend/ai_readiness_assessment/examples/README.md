# AI Readiness Assessment - Examples and Demonstrations

This directory contains comprehensive examples and demonstrations of the AI Readiness Assessment system capabilities.

## 📁 Files Overview

### 🎯 Core Demonstrations
- **`complete_assessment_demo.py`** - Complete end-to-end assessment workflow demonstration
- **`sub_agent_demos.py`** - Individual sub-agent capabilities and usage examples
- **`analytics_demo.py`** - Analytics and insights capabilities demonstration
- **`usage_examples.py`** - Various usage scenarios and integration examples

### 📊 Sample Data
- **`sample_data.py`** - Sample business profiles and assessment data for testing and demonstrations

## 🚀 Quick Start

### Run Complete Assessment Demo
```bash
python ai_readiness_assessment/examples/complete_assessment_demo.py
```

### Run Sub-Agent Demonstrations
```bash
python ai_readiness_assessment/examples/sub_agent_demos.py
```

### Run Analytics Demo
```bash
python ai_readiness_assessment/examples/analytics_demo.py
```

### Run Usage Examples
```bash
python ai_readiness_assessment/examples/usage_examples.py
```

### Generate Sample Data
```bash
python ai_readiness_assessment/examples/sample_data.py
```

## 📋 What Each Demo Shows

### 🎯 Complete Assessment Demo
Demonstrates the full assessment workflow:
1. **Starting Assessment** - Business information collection and initialization
2. **Question Help** - Getting clarifications and Kenya-specific examples
3. **Section Responses** - Submitting responses for all 6 assessment sections
4. **Score Calculation** - Computing final scores and readiness levels
5. **Recommendations** - Generating personalized recommendations
6. **Report Generation** - Creating comprehensive assessment reports
7. **State Management** - Saving and loading assessment progress
8. **Analytics** - Generating insights from assessment data

**Expected Output:**
- Complete assessment workflow execution
- Final readiness level determination
- Personalized recommendations
- Comprehensive report generation
- Assessment state persistence

### 🔧 Sub-Agent Demonstrations
Shows individual capabilities of each sub-agent:

#### 🧮 Scoring Agent
- Section score calculation
- Overall readiness level determination
- Score validation and analysis

#### 💡 Recommendation Agent
- Personalized recommendation generation
- Recommendation templates by readiness level
- Timeline estimation for implementation

#### 📋 Report Generator
- Comprehensive report creation
- Visual chart data generation
- Multiple export formats (JSON, Markdown, HTML)

#### 🇰🇪 Kenya Context Agent
- Kenya-specific regulations and compliance
- Local business context and examples
- Industry-specific guidance for Kenya

#### 📚 Assessment Guide
- Question explanations and clarifications
- Section guidance and tips
- Assessment best practices

### 📊 Analytics Demo
Demonstrates analytics and insights capabilities:
- **Aggregate Insights** - Statistical analysis across multiple assessments
- **Benchmarking** - Industry and peer comparisons
- **Pattern Recognition** - Common gaps and strengths identification
- **Industry Analysis** - Sector-specific insights and recommendations
- **Insights Dashboard** - Executive, operational, and analytical views

### 📖 Usage Examples
Shows different usage scenarios:
- **Quick Assessment** - Rapid insights for decision making (~10 minutes)
- **Detailed Assessment** - Comprehensive analysis for planning (~45 minutes)
- **Multi-Organization Analysis** - Portfolio benchmarking and insights
- **API Integration** - Automated workflows and custom applications
- **Command-Line Usage** - Developer tools and system administration

## 📊 Sample Data

The `sample_data.py` file provides realistic sample data for 5 different business profiles:

1. **InnovateTech Kenya** (Technology, Small) - Foundation Building
2. **Kenya Manufacturing Co** (Manufacturing, Medium) - Ready for Pilots
3. **Premier Bank Kenya** (Financial Services, Large) - AI Ready
4. **Rift Valley Agri Cooperative** (Agriculture, Medium) - Not Ready
5. **Nairobi Medical Center** (Healthcare, Medium) - Foundation Building

Each profile includes:
- Complete business information
- Assessment responses for all sections
- Expected readiness levels and scores
- Industry-specific characteristics

## 🎯 Use Cases

### For Business Leaders
- **Quick Assessment Demo** - Understand AI readiness in 10 minutes
- **Complete Assessment Demo** - See full assessment process and outputs
- **Analytics Demo** - Understand benchmarking and industry insights

### For Developers
- **Sub-Agent Demos** - Understand individual component capabilities
- **Usage Examples** - Learn integration patterns and API usage
- **Sample Data** - Use realistic data for testing and development

### For Consultants
- **Multi-Organization Analysis** - Portfolio assessment and benchmarking
- **Industry Analysis** - Sector-specific insights and recommendations
- **Complete Workflow** - End-to-end client assessment process

### For System Administrators
- **Command-Line Usage** - Automation and batch processing
- **API Integration** - System integration and workflow automation
- **Testing and Validation** - System verification and performance testing

## 🔧 Technical Requirements

### Dependencies
- Python 3.8+
- All AI Readiness Assessment system components
- JSON processing capabilities
- File system access for report generation

### System Requirements
- Minimum 4GB RAM for full demonstrations
- 1GB free disk space for reports and sample data
- Network access for any external API calls (if configured)

## 📈 Expected Performance

### Demo Execution Times
- **Complete Assessment Demo**: ~2-3 minutes
- **Sub-Agent Demos**: ~3-4 minutes
- **Analytics Demo**: ~2-3 minutes
- **Usage Examples**: ~1-2 minutes
- **Sample Data Generation**: ~30 seconds

### Resource Usage
- **Memory**: 100-500MB during execution
- **CPU**: Low to moderate usage
- **Disk**: 10-50MB for generated reports and data

## 🛠️ Customization

### Adding New Sample Data
Edit `sample_data.py` to add new business profiles:

```python
"new_business": {
    "business_info": {
        "name": "New Business Name",
        "industry": "Industry",
        "size": "Size"
    },
    "responses": {
        "data_infrastructure": {"q1": 3, "q2": 4, ...},
        # ... other sections
    },
    "expected_readiness": "Ready for Pilots",
    "total_score": 85
}
```

### Modifying Demonstrations
Each demo script can be customized by:
- Changing sample data used
- Modifying output formats
- Adding new demonstration scenarios
- Adjusting verbosity levels

### Creating Custom Examples
Use the existing examples as templates to create custom demonstrations for specific use cases or industries.

## 📞 Support

For questions about the examples or demonstrations:
- Review the code comments for detailed explanations
- Check the main system documentation
- Run individual components to isolate issues
- Use the sample data for consistent testing

## 🔄 Updates

These examples are updated regularly to reflect:
- New system capabilities
- Additional use cases
- Performance improvements
- User feedback and requirements

Check the main repository for the latest versions and updates.