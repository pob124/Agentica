from fastapi import FastAPI
from pydantic import BaseModel
from .agentica_core import register_project_context, generate_initial_email, chatbot_handler, handle_email_rejection, analyze_email_issues
from typing import Dict, Any

#fast api로 엔드포인트
app = FastAPI()

class ProjectRequest(BaseModel):
    project_id: int
    description: str

class EmailRequest(BaseModel):
    project_id: int
    lead: dict  # {"company": ..., "contact_name": ..., ...}

class ChatbotRequest(BaseModel):
    prompt: str
    payload: Dict[str, Any] = {}

class EmailRejectionRequest(BaseModel):
    project_id: int
    lead_info: dict
    original_email: dict  # {"subject": str, "body": str}
    user_feedback: str
    email_type: str = "initial"  # "initial" 또는 "followup"
    # 응답: {"action": str, "new_email": dict, "analysis": dict, "improvements": list, "message": str}

class EmailAnalysisRequest(BaseModel):
    email_content: dict  # {"subject": str, "body": str}
    user_feedback: str

@app.post("/register_project/")
def register_project(req: ProjectRequest):
    return register_project_context(req.project_id, req.description)

@app.post("/generate_email/")
def generate_email(req: EmailRequest):
    return generate_initial_email(req.project_id, req.lead)

# 엔드포인트: /chatbot/ 사용자의 프롬프트 해석 함수와 연결(현재는 조건문이지만 추후 기능 개발되면 ai로 바꿈)
@app.post("/chatbot/")
async def handle_chatbot(req: ChatbotRequest):
    try:
        result = chatbot_handler(req.prompt, req.payload)
        return result
    except Exception as e:
        return {"error": f"서버 오류: {str(e)}"}

@app.post("/analyze_email_issues/")
async def analyze_email(req: EmailAnalysisRequest):
    """
    이메일 문제점 분석 엔드포인트
    """
    try:
        result = analyze_email_issues(req.email_content, req.user_feedback)
        return result
    except Exception as e:
        return {"error": f"분석 중 오류 발생: {str(e)}"}

@app.post("/handle_email_rejection/")
async def handle_rejection(req: EmailRejectionRequest):
    """
    이메일 거부 처리 엔드포인트
    """
    try:
        result = handle_email_rejection(
            req.project_id,
            req.lead_info,
            req.original_email,
            req.user_feedback,
            req.email_type
        )
        return result
    except Exception as e:
        return {"error": f"처리 중 오류 발생: {str(e)}"}