from fastapi import FastAPI
from pydantic import BaseModel
from .agentica_core import register_project_context, generate_initial_email, chatbot_handler, handle_email_rejection, \
    analyze_email_issues, generate_emails_for_multiple_leads, project_contexts
from typing import Dict, Any, List, Union

#fast api로 엔드포인트
app = FastAPI()

class ProjectRequest(BaseModel):
    project_id: int
    description: str

class EmailRequest(BaseModel):
    project_id: int
    leads: Union[dict, List[dict]]

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
    """
    하나 또는 여러 기업에 대해 초안 메일 생성

    ⚠️ 먼저 /register_project/ 로 해당 project_id의 사업 설명을 등록해야 합니다.
    """
    if req.project_id not in project_contexts:
        return {
            "error": f"{req.project_id}번 프로젝트에 대한 사업 설명이 등록되지 않았습니다. 먼저 /register_project/를 호출하세요."
        }

    if isinstance(req.leads, list):
        return generate_emails_for_multiple_leads(req.project_id, req.leads)
    else:
        return generate_initial_email(req.project_id, req.leads)

# 엔드포인트: /chatbot/ 사용자의 프롬프트 해석 함수와 연결(ai로 교체)
@app.post("/chatbot/")
async def handle_chatbot(req: ChatbotRequest):
    """
    사용자 프롬프트 기반 자동 처리:
    - 사업 등록
    - 초안/후속 메일 생성
    - 이메일 재작성
    - 프로젝트/기업 조회 등

    ⚠️ 프롬프트는 **자세히 입력할수록 결과 품질이 높습니다.**
    """
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