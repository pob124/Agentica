import openai
import os
import json
from dotenv import load_dotenv

#아젠티카 함수
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#db연동 안되서 일단 배열로
project_contexts = {}

def register_project_context(project_id: int, description: str):
    project_contexts[project_id] = description
    return {"message": f"프로젝트 {project_id} 설명 저장 완료"}

def generate_initial_email(project_id: int, lead_info: dict) -> dict:
    context = project_contexts.get(project_id, "등록된 사업 설명이 없습니다.")

    messages = [
        {"role": "system", "content": f"너는 B2B 세일즈 이메일 작성을 전문으로 하는 에이전트야.\n\n사업 설명:\n{context}"},
        {"role": "user", "content": f"다음 고객 정보에 맞게 첫 제안 메일을 작성해줘:\n{lead_info}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    content = response['choices'][0]['message']['content']
    return {"email_body": content}

def generate_followup_email(project_id: int, lead_id: int, feedback_summary: str) -> dict:
    """
    피드백 기반 후속 메일 초안 생성
    Returns: {"subject": str, "body": str}
    """
    context = project_contexts.get(project_id, "등록된 사업 설명이 없습니다.")

    messages = [
        {"role": "system", "content": f"너는 B2B 세일즈 후속 이메일 작성을 전문으로 하는 에이전트야.\n\n사업 설명:\n{context}\n\n고객 피드백을 바탕으로 적절한 후속 메일을 작성해줘.\n다음 JSON 형식으로만 응답해줘: {{\"subject\": \"이메일 제목\", \"body\": \"이메일 본문 내용\"}}" },
        {"role": "user", "content": f"다음 고객 피드백을 바탕으로 후속 메일을 작성해줘:\n{feedback_summary}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    content = response['choices'][0]['message']['content']
    
    try:
        # JSON 파싱 시도
        result = json.loads(content)
        return {
            "subject": result.get("subject", ""),
            "body": result.get("body", "")
        }
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 기본값 반환
        return {
            "subject": "후속 제안",
            "body": "고객님의 피드백을 바탕으로 추가 제안을 드립니다."
        }

def summarize_feedback(feedback_text: str) -> dict:
    """
    고객 응답 요약 및 감정 분류
    Returns: {"summary": str, "response_type": str}
    """
    messages = [
        {"role": "system", "content": "다음 JSON 형식으로만 응답해줘: {\"summary\": \"고객 응답의 핵심 요약\", \"response_type\": \"positive/neutral/negative\"}"},
        {"role": "user", "content": f"다음 고객 응답을 분석해줘:\n{feedback_text}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    content = response['choices'][0]['message']['content']
    
    try:
        # JSON 파싱 시도
        result = json.loads(content)
        return {
            "summary": result.get("summary", ""),
            "response_type": result.get("response_type", "neutral")
        }
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 기본값 반환
        return {
            "summary": "응답 분석 중 오류가 발생했습니다.",
            "response_type": "neutral"
        }