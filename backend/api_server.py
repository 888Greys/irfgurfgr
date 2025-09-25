
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from ai_readiness_assessment.main_agent import orchestrate_assessment_flow

app = FastAPI()

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BusinessInfo(BaseModel):
    name: str
    industry: str
    size: str
    location: str

class AnswerPayload(BaseModel):
    section_id: str
    question_id: str
    score: int



import json
from fastapi.responses import JSONResponse


@app.post("/api/assessment/start")
def start_assessment(info: Dict[str, Any]):
    try:
        print(f"[DEBUG] FastAPI /api/assessment/start received: {info}")
        payload = {"business_info": info.get("business_info", {})}
        print(f"[DEBUG] Payload to orchestrator: {payload}")
        result = orchestrate_assessment_flow.invoke({"action": "start_assessment", "data": json.dumps(payload)})
        # result is a JSON string, parse and return as JSON
        result_data = json.loads(result)
        if not result_data.get("assessment_id"):
            # fallback: use business name or user_id as assessment_id if present
            result_data["assessment_id"] = result_data.get("user_id") or result_data.get("business_name")
        return JSONResponse(content=result_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assessment/{assessment_id}/next")
def get_next_question(assessment_id: str):
    try:
        result = orchestrate_assessment_flow.invoke({"action": "get_next_question", "assessment_id": assessment_id})
        result_data = json.loads(result)
        return JSONResponse(content=result_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assessment/{assessment_id}/answer")
def submit_answer(assessment_id: str, payload: AnswerPayload):
    try:
        # Transform the payload to match what the handler expects
        transformed_data = {
            "section": payload.section_id,
            "responses": {payload.question_id: payload.score}
        }
        result = orchestrate_assessment_flow.invoke({
            "action": "submit_responses",
            "data": json.dumps(transformed_data),
            "assessment_id": assessment_id
        })
        result_data = json.loads(result)
        return JSONResponse(content=result_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assessment/{assessment_id}/guidance")
def get_assessment_guidance(assessment_id: str, data: Dict[str, Any]):
    try:
        question_id = data.get("question_id")
        user_message = data.get("user_message", "")
        section = data.get("section", "")
        
        if not question_id:
            raise HTTPException(status_code=400, detail="question_id is required")
        
        # Import the assessment guide agent
        from ai_readiness_assessment.subagents.assessment_guide import get_question_explanation
        
        # Call the assessment guide agent
        result = get_question_explanation.invoke({
            "question_id": question_id,
            "section": section,
            "user_context": json.dumps({
                "user_message": user_message,
                "assessment_id": assessment_id
            })
        })
        
        guidance_data = json.loads(result)
        return JSONResponse(content=guidance_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assessment/{assessment_id}/results")
def get_results(assessment_id: str):
    try:
        result = orchestrate_assessment_flow.invoke({"action": "get_results", "assessment_id": assessment_id})
        result_data = json.loads(result)
        return JSONResponse(content=result_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
