"""
Assessment Persistence and State Management
Handles save/resume functionality and assessment history
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class AssessmentPersistence:
    """Handles assessment data persistence using virtual file system"""
    
    def __init__(self, base_path: str = "assessments"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.base_path / "active").mkdir(exist_ok=True)
        (self.base_path / "completed").mkdir(exist_ok=True)
        (self.base_path / "history").mkdir(exist_ok=True)
        (self.base_path / "exports").mkdir(exist_ok=True)
    
    def get_assessment_path(self, assessment_id: str, status: str = "active") -> Path:
        """Get file path for assessment data"""
        return self.base_path / status / f"{assessment_id}.json"
    
    def get_history_path(self, user_id: str) -> Path:
        """Get file path for user assessment history"""
        return self.base_path / "history" / f"{user_id}_history.json"


@tool
def save_assessment_state(assessment_id: str, assessment_data: str, auto_save: bool = True) -> str:
    """
    Save assessment state with auto-save functionality.
    
    Args:
        assessment_id: Unique identifier for the assessment
        assessment_data: JSON string with complete assessment data
        auto_save: Whether this is an automatic save (default: True)
    
    Returns:
        JSON string with save confirmation
    """
    try:
        persistence = AssessmentPersistence()
        
        # Parse assessment data
        data = json.loads(assessment_data)
        
        # Add metadata
        save_metadata = {
            "assessment_id": assessment_id,
            "last_saved": datetime.now().isoformat(),
            "save_type": "auto" if auto_save else "manual",
            "version": data.get("version", 1) + (1 if auto_save else 0)
        }
        
        # Merge with existing data
        data.update(save_metadata)
        
        # Determine status and save location
        completion_percentage = _calculate_completion_percentage(data)
        status = "completed" if completion_percentage >= 100 else "active"
        
        file_path = persistence.get_assessment_path(assessment_id, status)
        
        # Save assessment data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update user history
        user_id = data.get("user_id", "unknown")
        _update_user_history(persistence, user_id, assessment_id, data)
        
        # Auto-save cleanup (keep only last 5 auto-saves)
        if auto_save:
            _cleanup_old_saves(persistence, assessment_id)
        
        return json.dumps({
            "success": True,
            "assessment_id": assessment_id,
            "saved_at": save_metadata["last_saved"],
            "save_type": save_metadata["save_type"],
            "version": save_metadata["version"],
            "completion_percentage": completion_percentage,
            "status": status,
            "file_path": str(file_path)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to save assessment: {str(e)}",
            "assessment_id": assessment_id
        })


@tool
def load_assessment_state(assessment_id: str, include_history: bool = False) -> str:
    """
    Load assessment state from storage.
    
    Args:
        assessment_id: Unique identifier for the assessment
        include_history: Whether to include assessment history (default: False)
    
    Returns:
        JSON string with assessment data
    """
    try:
        persistence = AssessmentPersistence()
        
        # Try to load from active assessments first
        active_path = persistence.get_assessment_path(assessment_id, "active")
        completed_path = persistence.get_assessment_path(assessment_id, "completed")
        
        assessment_data = None
        status = None
        
        if active_path.exists():
            with open(active_path, 'r') as f:
                assessment_data = json.load(f)
            status = "active"
        elif completed_path.exists():
            with open(completed_path, 'r') as f:
                assessment_data = json.load(f)
            status = "completed"
        else:
            return json.dumps({
                "success": False,
                "error": f"Assessment {assessment_id} not found",
                "assessment_id": assessment_id
            })
        
        # Add current status
        assessment_data["current_status"] = status
        assessment_data["loaded_at"] = datetime.now().isoformat()
        
        # Include history if requested
        if include_history:
            user_id = assessment_data.get("user_id", "unknown")
            history_data = _load_user_history(persistence, user_id)
            assessment_data["user_history"] = history_data
        
        return json.dumps({
            "success": True,
            "assessment_data": assessment_data,
            "status": status,
            "loaded_at": assessment_data["loaded_at"]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to load assessment: {str(e)}",
            "assessment_id": assessment_id
        })


@tool
def resume_assessment(assessment_id: str, user_context: str = None) -> str:
    """
    Resume an existing assessment with context restoration.
    
    Args:
        assessment_id: Unique identifier for the assessment
        user_context: Optional JSON string with additional user context
    
    Returns:
        JSON string with resume information and next steps
    """
    try:
        # Load assessment state
        load_result = load_assessment_state.invoke({
            "assessment_id": assessment_id,
            "include_history": True
        })
        
        load_data = json.loads(load_result)
        
        if not load_data.get("success"):
            return load_result
        
        assessment_data = load_data["assessment_data"]
        
        # Calculate resume information
        completion_info = _analyze_completion_status(assessment_data)
        next_steps = _determine_next_steps(assessment_data)
        
        # Parse user context if provided
        context = {}
        if user_context:
            try:
                context = json.loads(user_context)
            except:
                pass
        
        resume_info = {
            "success": True,
            "assessment_id": assessment_id,
            "resumed_at": datetime.now().isoformat(),
            "last_activity": assessment_data.get("last_saved"),
            "completion_status": completion_info,
            "next_steps": next_steps,
            "assessment_data": assessment_data,
            "user_context": context,
            "resume_guidance": _generate_resume_guidance(completion_info, next_steps)
        }
        
        # Update last accessed time
        assessment_data["last_accessed"] = datetime.now().isoformat()
        assessment_data["access_count"] = assessment_data.get("access_count", 0) + 1
        
        # Save updated access info
        save_assessment_state.invoke({
            "assessment_id": assessment_id,
            "assessment_data": json.dumps(assessment_data),
            "auto_save": True
        })
        
        return json.dumps(resume_info, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to resume assessment: {str(e)}",
            "assessment_id": assessment_id
        })


@tool
def export_assessment_data(assessment_id: str, export_format: str = "json", include_metadata: bool = True) -> str:
    """
    Export assessment data in various formats.
    
    Args:
        assessment_id: Unique identifier for the assessment
        export_format: Export format (json, csv, xml)
        include_metadata: Whether to include metadata (default: True)
    
    Returns:
        JSON string with export data or file path
    """
    try:
        persistence = AssessmentPersistence()
        
        # Load assessment data
        load_result = load_assessment_state.invoke({
            "assessment_id": assessment_id,
            "include_history": False
        })
        
        load_data = json.loads(load_result)
        
        if not load_data.get("success"):
            return load_result
        
        assessment_data = load_data["assessment_data"]
        
        # Prepare export data
        export_data = _prepare_export_data(assessment_data, include_metadata)
        
        # Generate export based on format
        if export_format.lower() == "json":
            exported_content = json.dumps(export_data, indent=2)
            file_extension = "json"
        elif export_format.lower() == "csv":
            exported_content = _export_to_csv(export_data)
            file_extension = "csv"
        elif export_format.lower() == "xml":
            exported_content = _export_to_xml(export_data)
            file_extension = "xml"
        else:
            return json.dumps({
                "success": False,
                "error": f"Unsupported export format: {export_format}",
                "supported_formats": ["json", "csv", "xml"]
            })
        
        # Save export file
        export_filename = f"{assessment_id}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        export_path = persistence.base_path / "exports" / export_filename
        
        with open(export_path, 'w') as f:
            f.write(exported_content)
        
        return json.dumps({
            "success": True,
            "assessment_id": assessment_id,
            "export_format": export_format,
            "export_path": str(export_path),
            "export_filename": export_filename,
            "exported_at": datetime.now().isoformat(),
            "file_size": len(exported_content),
            "content": exported_content if export_format == "json" else None
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to export assessment: {str(e)}",
            "assessment_id": assessment_id
        })


@tool
def import_assessment_data(import_data: str, assessment_id: str = None, overwrite: bool = False) -> str:
    """
    Import assessment data from external source.
    
    Args:
        import_data: JSON string with assessment data to import
        assessment_id: Optional assessment ID (will generate if not provided)
        overwrite: Whether to overwrite existing assessment (default: False)
    
    Returns:
        JSON string with import confirmation
    """
    try:
        # Parse import data
        data = json.loads(import_data)
        
        # Generate assessment ID if not provided
        if not assessment_id:
            assessment_id = f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Check if assessment exists
        persistence = AssessmentPersistence()
        active_path = persistence.get_assessment_path(assessment_id, "active")
        completed_path = persistence.get_assessment_path(assessment_id, "completed")
        
        if (active_path.exists() or completed_path.exists()) and not overwrite:
            return json.dumps({
                "success": False,
                "error": f"Assessment {assessment_id} already exists. Use overwrite=True to replace.",
                "assessment_id": assessment_id
            })
        
        # Validate import data
        validation_result = _validate_import_data(data)
        if not validation_result["valid"]:
            return json.dumps({
                "success": False,
                "error": "Invalid import data",
                "validation_errors": validation_result["errors"],
                "assessment_id": assessment_id
            })
        
        # Add import metadata
        data["imported_at"] = datetime.now().isoformat()
        data["import_source"] = "external"
        data["assessment_id"] = assessment_id
        
        # Save imported assessment
        save_result = save_assessment_state.invoke({
            "assessment_id": assessment_id,
            "assessment_data": json.dumps(data),
            "auto_save": False
        })
        
        save_data = json.loads(save_result)
        
        if save_data.get("success"):
            return json.dumps({
                "success": True,
                "assessment_id": assessment_id,
                "imported_at": data["imported_at"],
                "import_status": "completed",
                "validation_passed": True,
                "save_details": save_data
            }, indent=2)
        else:
            return save_result
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to import assessment: {str(e)}",
            "assessment_id": assessment_id
        })


@tool
def get_assessment_history(user_id: str, limit: int = 10, include_details: bool = False) -> str:
    """
    Get assessment history for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of assessments to return (default: 10)
        include_details: Whether to include full assessment details (default: False)
    
    Returns:
        JSON string with assessment history
    """
    try:
        persistence = AssessmentPersistence()
        
        # Load user history
        history_data = _load_user_history(persistence, user_id)
        
        if not history_data:
            return json.dumps({
                "success": True,
                "user_id": user_id,
                "total_assessments": 0,
                "assessments": [],
                "message": "No assessment history found"
            })
        
        # Sort by date (most recent first)
        assessments = sorted(
            history_data.get("assessments", []),
            key=lambda x: x.get("last_saved", ""),
            reverse=True
        )
        
        # Limit results
        limited_assessments = assessments[:limit]
        
        # Include details if requested
        if include_details:
            for assessment in limited_assessments:
                try:
                    load_result = load_assessment_state.invoke({
                        "assessment_id": assessment["assessment_id"],
                        "include_history": False
                    })
                    
                    load_data = json.loads(load_result)
                    if load_data.get("success"):
                        assessment["full_data"] = load_data["assessment_data"]
                except:
                    # Continue without details if load fails
                    pass
        
        return json.dumps({
            "success": True,
            "user_id": user_id,
            "total_assessments": len(assessments),
            "returned_assessments": len(limited_assessments),
            "assessments": limited_assessments,
            "history_summary": _generate_history_summary(assessments)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get assessment history: {str(e)}",
            "user_id": user_id
        })


@tool
def compare_assessments(assessment_ids: str, comparison_type: str = "scores") -> str:
    """
    Compare multiple assessments.
    
    Args:
        assessment_ids: JSON array string with assessment IDs to compare
        comparison_type: Type of comparison (scores, progress, timeline)
    
    Returns:
        JSON string with comparison results
    """
    try:
        # Parse assessment IDs
        ids = json.loads(assessment_ids)
        
        if len(ids) < 2:
            return json.dumps({
                "success": False,
                "error": "At least 2 assessments required for comparison"
            })
        
        # Load all assessments
        assessments = []
        for assessment_id in ids:
            load_result = load_assessment_state.invoke({
                "assessment_id": assessment_id,
                "include_history": False
            })
            
            load_data = json.loads(load_result)
            if load_data.get("success"):
                assessments.append(load_data["assessment_data"])
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to load assessment {assessment_id}",
                    "failed_assessment": assessment_id
                })
        
        # Perform comparison based on type
        if comparison_type == "scores":
            comparison_result = _compare_scores(assessments)
        elif comparison_type == "progress":
            comparison_result = _compare_progress(assessments)
        elif comparison_type == "timeline":
            comparison_result = _compare_timeline(assessments)
        else:
            return json.dumps({
                "success": False,
                "error": f"Unsupported comparison type: {comparison_type}",
                "supported_types": ["scores", "progress", "timeline"]
            })
        
        return json.dumps({
            "success": True,
            "comparison_type": comparison_type,
            "assessments_compared": len(assessments),
            "assessment_ids": ids,
            "comparison_results": comparison_result,
            "compared_at": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to compare assessments: {str(e)}"
        })


# Helper functions

def _calculate_completion_percentage(assessment_data: Dict) -> float:
    """Calculate assessment completion percentage"""
    sections = assessment_data.get("sections", {})
    if not sections:
        return 0.0
    
    completed_sections = sum(1 for section in sections.values() if section.get("completed", False))
    total_sections = len(sections)
    
    return (completed_sections / total_sections * 100) if total_sections > 0 else 0.0


def _update_user_history(persistence: AssessmentPersistence, user_id: str, assessment_id: str, assessment_data: Dict):
    """Update user assessment history"""
    history_path = persistence.get_history_path(user_id)
    
    # Load existing history
    history_data = {"user_id": user_id, "assessments": []}
    if history_path.exists():
        try:
            with open(history_path, 'r') as f:
                history_data = json.load(f)
        except:
            pass
    
    # Update or add assessment entry
    assessments = history_data.get("assessments", [])
    
    # Find existing entry
    existing_index = None
    for i, assessment in enumerate(assessments):
        if assessment.get("assessment_id") == assessment_id:
            existing_index = i
            break
    
    # Create assessment summary
    assessment_summary = {
        "assessment_id": assessment_id,
        "business_name": assessment_data.get("business_name", "Unknown"),
        "industry": assessment_data.get("industry", "Unknown"),
        "created_at": assessment_data.get("created_at"),
        "last_saved": assessment_data.get("last_saved"),
        "completion_percentage": _calculate_completion_percentage(assessment_data),
        "status": assessment_data.get("current_status", "active"),
        "total_score": assessment_data.get("total_score"),
        "readiness_level": assessment_data.get("readiness_level")
    }
    
    if existing_index is not None:
        assessments[existing_index] = assessment_summary
    else:
        assessments.append(assessment_summary)
    
    history_data["assessments"] = assessments
    history_data["last_updated"] = datetime.now().isoformat()
    
    # Save updated history
    with open(history_path, 'w') as f:
        json.dump(history_data, f, indent=2)


def _load_user_history(persistence: AssessmentPersistence, user_id: str) -> Optional[Dict]:
    """Load user assessment history"""
    history_path = persistence.get_history_path(user_id)
    
    if not history_path.exists():
        return None
    
    try:
        with open(history_path, 'r') as f:
            return json.load(f)
    except:
        return None


def _cleanup_old_saves(persistence: AssessmentPersistence, assessment_id: str, keep_count: int = 5):
    """Clean up old auto-save files"""
    # This is a simplified version - in a real implementation,
    # you might want to keep versioned saves
    pass


def _analyze_completion_status(assessment_data: Dict) -> Dict[str, Any]:
    """Analyze assessment completion status"""
    sections = assessment_data.get("sections", {})
    
    completed_sections = []
    incomplete_sections = []
    
    for section_id, section_data in sections.items():
        if section_data.get("completed", False):
            completed_sections.append(section_id)
        else:
            incomplete_sections.append(section_id)
    
    completion_percentage = _calculate_completion_percentage(assessment_data)
    
    return {
        "completion_percentage": completion_percentage,
        "completed_sections": completed_sections,
        "incomplete_sections": incomplete_sections,
        "total_sections": len(sections),
        "is_complete": completion_percentage >= 100,
        "next_section": incomplete_sections[0] if incomplete_sections else None
    }


def _determine_next_steps(assessment_data: Dict) -> List[str]:
    """Determine next steps for assessment"""
    completion_info = _analyze_completion_status(assessment_data)
    
    if completion_info["is_complete"]:
        return [
            "Review your assessment results",
            "Generate comprehensive report",
            "Implement recommended actions"
        ]
    elif completion_info["completion_percentage"] > 50:
        return [
            f"Complete remaining sections: {', '.join(completion_info['incomplete_sections'])}",
            "Review completed sections if needed",
            "Prepare for final scoring"
        ]
    else:
        return [
            f"Continue with next section: {completion_info['next_section']}",
            "Take your time to provide accurate responses",
            "Use help features if you need clarification"
        ]


def _generate_resume_guidance(completion_info: Dict, next_steps: List[str]) -> List[str]:
    """Generate guidance for resuming assessment"""
    guidance = []
    
    if completion_info["completion_percentage"] == 0:
        guidance.append("Welcome back! You can start with any section that interests you most.")
    elif completion_info["completion_percentage"] < 25:
        guidance.append("You've made a good start. Continue building momentum by completing more sections.")
    elif completion_info["completion_percentage"] < 75:
        guidance.append("You're making great progress! You're over halfway through the assessment.")
    elif completion_info["completion_percentage"] < 100:
        guidance.append("You're almost done! Just a few more sections to complete.")
    else:
        guidance.append("Congratulations! Your assessment is complete. You can now generate your report.")
    
    guidance.extend([
        f"You have completed {len(completion_info['completed_sections'])} out of {completion_info['total_sections']} sections.",
        "All your previous responses have been saved and are ready for you to continue."
    ])
    
    return guidance


def _prepare_export_data(assessment_data: Dict, include_metadata: bool) -> Dict[str, Any]:
    """Prepare data for export"""
    export_data = {
        "assessment_id": assessment_data.get("assessment_id"),
        "business_info": {
            "name": assessment_data.get("business_name"),
            "industry": assessment_data.get("industry"),
            "size": assessment_data.get("business_size")
        },
        "sections": assessment_data.get("sections", {}),
        "scores": {
            "total_score": assessment_data.get("total_score"),
            "readiness_level": assessment_data.get("readiness_level"),
            "section_scores": assessment_data.get("section_scores", {})
        },
        "completion_info": {
            "completion_percentage": _calculate_completion_percentage(assessment_data),
            "completed_at": assessment_data.get("completed_at"),
            "last_saved": assessment_data.get("last_saved")
        }
    }
    
    if include_metadata:
        export_data["metadata"] = {
            "version": assessment_data.get("version"),
            "created_at": assessment_data.get("created_at"),
            "last_accessed": assessment_data.get("last_accessed"),
            "access_count": assessment_data.get("access_count"),
            "save_type": assessment_data.get("save_type")
        }
    
    return export_data


def _export_to_csv(export_data: Dict) -> str:
    """Export data to CSV format"""
    csv_lines = []
    
    # Header
    csv_lines.append("Section,Question,Response,Score")
    
    # Data rows
    sections = export_data.get("sections", {})
    for section_id, section_data in sections.items():
        responses = section_data.get("responses", {})
        for question_id, response in responses.items():
            csv_lines.append(f"{section_id},{question_id},{response},")
    
    return "\n".join(csv_lines)


def _export_to_xml(export_data: Dict) -> str:
    """Export data to XML format"""
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<assessment>')
    
    # Basic info
    xml_lines.append(f'  <assessment_id>{export_data.get("assessment_id", "")}</assessment_id>')
    
    # Business info
    business_info = export_data.get("business_info", {})
    xml_lines.append('  <business_info>')
    xml_lines.append(f'    <name>{business_info.get("name", "")}</name>')
    xml_lines.append(f'    <industry>{business_info.get("industry", "")}</industry>')
    xml_lines.append('  </business_info>')
    
    # Sections
    xml_lines.append('  <sections>')
    sections = export_data.get("sections", {})
    for section_id, section_data in sections.items():
        xml_lines.append(f'    <section id="{section_id}">')
        responses = section_data.get("responses", {})
        for question_id, response in responses.items():
            xml_lines.append(f'      <question id="{question_id}">{response}</question>')
        xml_lines.append('    </section>')
    xml_lines.append('  </sections>')
    
    xml_lines.append('</assessment>')
    return "\n".join(xml_lines)


def _validate_import_data(data: Dict) -> Dict[str, Any]:
    """Validate imported assessment data"""
    errors = []
    
    # Check required fields
    required_fields = ["assessment_id", "sections"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate sections structure
    if "sections" in data:
        sections = data["sections"]
        if not isinstance(sections, dict):
            errors.append("Sections must be a dictionary")
        else:
            for section_id, section_data in sections.items():
                if not isinstance(section_data, dict):
                    errors.append(f"Section {section_id} must be a dictionary")
                elif "responses" not in section_data:
                    errors.append(f"Section {section_id} missing responses")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def _generate_history_summary(assessments: List[Dict]) -> Dict[str, Any]:
    """Generate summary of assessment history"""
    if not assessments:
        return {"total": 0, "completed": 0, "in_progress": 0}
    
    completed = sum(1 for a in assessments if a.get("completion_percentage", 0) >= 100)
    in_progress = len(assessments) - completed
    
    # Calculate average completion time for completed assessments
    completed_assessments = [a for a in assessments if a.get("completion_percentage", 0) >= 100]
    
    industries = {}
    for assessment in assessments:
        industry = assessment.get("industry", "Unknown")
        industries[industry] = industries.get(industry, 0) + 1
    
    return {
        "total": len(assessments),
        "completed": completed,
        "in_progress": in_progress,
        "most_common_industry": max(industries.items(), key=lambda x: x[1])[0] if industries else "Unknown",
        "industries_assessed": list(industries.keys())
    }


def _compare_scores(assessments: List[Dict]) -> Dict[str, Any]:
    """Compare scores across assessments"""
    comparison = {
        "total_scores": [],
        "readiness_levels": [],
        "section_comparisons": {}
    }
    
    for assessment in assessments:
        comparison["total_scores"].append({
            "assessment_id": assessment.get("assessment_id"),
            "total_score": assessment.get("total_score", 0),
            "readiness_level": assessment.get("readiness_level", "Unknown")
        })
        
        comparison["readiness_levels"].append(assessment.get("readiness_level", "Unknown"))
        
        # Section scores
        section_scores = assessment.get("section_scores", {})
        for section_id, section_data in section_scores.items():
            if section_id not in comparison["section_comparisons"]:
                comparison["section_comparisons"][section_id] = []
            
            comparison["section_comparisons"][section_id].append({
                "assessment_id": assessment.get("assessment_id"),
                "score": section_data.get("section_total", 0)
            })
    
    return comparison


def _compare_progress(assessments: List[Dict]) -> Dict[str, Any]:
    """Compare progress across assessments"""
    comparison = {
        "completion_rates": [],
        "time_comparisons": []
    }
    
    for assessment in assessments:
        completion_percentage = _calculate_completion_percentage(assessment)
        comparison["completion_rates"].append({
            "assessment_id": assessment.get("assessment_id"),
            "completion_percentage": completion_percentage,
            "status": "completed" if completion_percentage >= 100 else "in_progress"
        })
        
        created_at = assessment.get("created_at")
        last_saved = assessment.get("last_saved")
        if created_at and last_saved:
            try:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                saved = datetime.fromisoformat(last_saved.replace('Z', '+00:00'))
                duration = (saved - created).total_seconds() / 3600  # hours
                
                comparison["time_comparisons"].append({
                    "assessment_id": assessment.get("assessment_id"),
                    "duration_hours": duration,
                    "completion_percentage": completion_percentage
                })
            except:
                pass
    
    return comparison


def _compare_timeline(assessments: List[Dict]) -> Dict[str, Any]:
    """Compare timeline across assessments"""
    comparison = {
        "creation_dates": [],
        "completion_dates": [],
        "duration_analysis": []
    }
    
    for assessment in assessments:
        comparison["creation_dates"].append({
            "assessment_id": assessment.get("assessment_id"),
            "created_at": assessment.get("created_at"),
            "business_name": assessment.get("business_name")
        })
        
        if assessment.get("completed_at"):
            comparison["completion_dates"].append({
                "assessment_id": assessment.get("assessment_id"),
                "completed_at": assessment.get("completed_at"),
                "readiness_level": assessment.get("readiness_level")
            })
    
    return comparison