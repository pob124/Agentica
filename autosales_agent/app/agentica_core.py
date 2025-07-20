from openai import OpenAI, api_key
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)
from typing import Dict, Any
import re, json

# 아젠티카 함수
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# db연동 안되서 일단 배열로
project_contexts: Dict[int, str] = {}


def register_project_context(project_id: int, description: str):
    project_contexts[project_id] = description
    return {"message": f"프로젝트 {project_id} 설명 저장 완료"}


def generate_initial_email(project_id: int, lead_info: dict) -> dict:
    context = project_contexts.get(project_id, "등록된 사업 설명이 없습니다.")

    messages = [
        {
            "role": "system",
            "content": (
                "너는 B2B 세일즈 이메일 작성을 전문으로 하는 AI야.\n"
                "다음 JSON 형식으로만 응답해. 설명은 포함하지 마.\n"
                "{\n"
                "  \"subject\": \"이메일 제목\",\n"
                "  \"body\": \"이메일 본문 내용\"\n"
                "}\n\n"
                "이메일에는 다음 요소를 포함해:\n"
                "- 고객 상황 언급\n"
                "- 우리 사업/서비스의 핵심 가치 제안\n"
                "- 기대 효과 2~3가지\n"
                "- 회신 유도 문구"
            )
        },
        {
            "role": "user",
            "content": f"사업 설명: {context}\n고객 정보: {lead_info}\n위 조건을 기반으로 이메일 초안을 JSON 형식으로 작성해줘."
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            timeout=15
        )
        content = response.choices[0].message.content

        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return {
                "subject": result.get("subject", ""),
                "body": result.get("body", "")
            }

    except Exception as e:
        pass

    return {
        "subject": "제안드립니다",
        "body": "안녕하세요, 고객님의 상황을 고려한 제안을 드리고자 연락드립니다..."
    }

#email 다중 생성 함수
def generate_emails_for_multiple_leads(project_id: int, lead_info_list: list[dict]) -> list[dict]:
    """
    여러 기업에 대해 초안 이메일을 생성
    Args:
        project_id: 프로젝트 ID
        lead_info_list: 각 기업의 정보 리스트
    Returns:
        [{"lead": {}, "email": {"subject": str, "body": str}}, ...]
    """
    result = []

    for lead_info in lead_info_list:
        email = generate_initial_email(project_id, lead_info)
        result.append({
            "lead": lead_info,
            "email": email
        })

    return result


def generate_followup_email(project_id: int, lead_id: int, feedback_summary: str) -> dict:
    """
    피드백 기반 후속 메일 초안 생성
    Returns: {"subject": str, "body": str}
    """

    context = project_contexts.get(project_id, "등록된 사업 설명이 없습니다.")

    messages = [
        {
            "role": "system",
            "content": (
                "너는 B2B 세일즈 후속 이메일 작성 전문가야.\n\n"
                "다음은 특정 사업에 대한 설명과 고객 피드백이야.\n"
                "이를 바탕으로 후속 제안 메일을 작성해줘.\n\n"
                "반드시 아래 형식의 JSON으로만 응답해. JSON 외 설명은 절대 포함하지 마.\n\n"
                "예시:\n"
                "{\n"
                "  \"subject\": \"기존 제안에 대한 추가 제안 드립니다\",\n"
                "  \"body\": \"고객님의 피드백 감사드립니다. 제안해주신 내용을 반영하여 다음과 같은 조건을 추가 제안드립니다...\"\n"
                "}\n\n"
                f"사업 설명:\n{context}"
            )
        },
        {
            "role": "user",
            "content": f"다음 고객 피드백을 바탕으로 후속 메일을 작성해줘:\n{feedback_summary}"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    content = response.choices[0].message.content

    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return {
                "subject": result.get("subject", ""),
                "body": result.get("body", "")
            }
    except Exception as e:
        pass

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
        {
            "role": "system",
            "content": (
                "너는 B2B 고객 피드백 분석 전문가야.\n\n"
                "고객 응답을 요약하고, 긍정적/중립적/부정적 응답인지 분류해.\n"
                "반드시 아래 JSON 형식으로만 응답해. 그 외 문장은 절대 포함하지 마.\n\n"
                "예시:\n"
                "{\n"
                "  \"summary\": \"가격이 부담스럽다는 응답\",\n"
                "  \"response_type\": \"negative\"\n"
                "}\n\n"
                "response_type 값은 반드시 다음 중 하나여야 해: positive, neutral, negative"
            )
        },
        {
            "role": "user",
            "content": f"다음 고객 응답을 분석해줘:\n{feedback_text}"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    content = response.choices[0].message.content

    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return {
                "summary": result.get("summary", ""),
                "response_type": result.get("response_type", "neutral")
            }
    except Exception as e:
        pass

    # 실패 시 기본값
    return {
        "summary": "응답 분석 중 오류가 발생했습니다.",
        "response_type": "neutral"
    }


# 프롬프트 해석 함수 (ai 기반)
def analyze_prompt_ai(prompt: str) -> str:
    """
    GPT를 활용한 인텐트 분류 (명확한 intent key만 반환)
    """
    messages = [
        {
            "role": "system",
            "content": (
                "다음 사용자 요청이 어떤 의도(intent)에 해당하는지 분류해줘.\n"
                "다음 중 하나만 응답으로 줘:\n"
                "- register_project\n"
                "- initial_email\n"
                "- followup_email\n"
                "- email_rewrite_request\n"
                "- list_projects\n"
                "- list_leads\n"
                "- add_lead\n"
                "- unknown\n\n"
                "절대로 설명하지 마. 반드시 위 키워드 하나만 텍스트로 응답해."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            timeout=10
        )
        return response.choices[0].message.content.strip()
    except:
        return "unknown"


# 챗봇 핸들러 함수
def chatbot_handler(user_prompt: str, payload: Dict[str, Any], debug: bool = False) -> Dict[str, Any]:
    intent = analyze_prompt_ai(user_prompt)

    # fallback: email_rewrite_request인데 필수 항목이 없으면 initial_email로 강제 전환
    if intent == "email_rewrite_request":
        required = ["project_id", "lead_info", "original_email", "user_feedback"]
        if not all(k in payload for k in required):
            intent = "initial_email"

    if intent == "register_project":
        project_id = payload.get("project_id")
        description = payload.get("description")
        if not project_id or not description:
            return {"error": "'project_id'와 'description'은 필수입니다.", "intent": intent if debug else None}
        return register_project_context(project_id, description)

    elif intent == "initial_email":
        project_id = payload.get("project_id")
        leads = payload.get("leads")  # list or dict

        if not project_id or not leads:
            return {"error": "'project_id'와 'leads'는 필수입니다.", "intent": intent if debug else None}

        if isinstance(leads, list):
            return generate_emails_for_multiple_leads(project_id, leads)
        else:
            return generate_initial_email(project_id, leads)

    elif intent == "followup_email":
        project_id = payload.get("project_id")
        lead_id = payload.get("lead_id")
        feedback_text = payload.get("feedback_text")

        if not project_id or not lead_id or not feedback_text:
            return {"error": "'project_id', 'lead_id', 'feedback_text'는 필수입니다.", "intent": intent if debug else None}

        feedback = summarize_feedback(feedback_text)
        return generate_followup_email(project_id, lead_id, feedback["summary"])

    elif intent == "email_rewrite_request":
        project_id = payload.get("project_id")
        lead_info = payload.get("lead_info")
        original_email = payload.get("original_email")
        user_feedback = payload.get("user_feedback")
        email_type = payload.get("email_type", "initial")

        if not all([project_id, lead_info, original_email, user_feedback]):
            return {"error": "필수 파라미터 누락: 'project_id', 'lead_info', 'original_email', 'user_feedback'", "intent": intent if debug else None}

        return handle_email_rejection(project_id, lead_info, original_email, user_feedback, email_type)

    elif intent == "list_projects":
        return {"projects": []}  # TODO

    elif intent == "list_leads":
        return {"leads": []}  # TODO

    elif intent == "add_lead":
        return {"message": "기업 등록 기능은 아직 구현되지 않았습니다."}

    else:
        return {
            "error": "요청을 이해하지 못했습니다. 프롬프트를 구체적으로 작성해주세요.",
            "intent": intent if debug else None
        }


def analyze_email_issues(email_content: dict, user_feedback: str) -> dict:
    """
    사용자 피드백을 바탕으로 이메일의 문제점을 분석
    Returns: {"issues": list, "suggestions": list, "priority": str}
    """

    messages = [
        {
            "role": "system",
            "content": (
                "너는 B2B 이메일 품질 분석 전문가야.\n\n"
                "사용자의 피드백을 바탕으로 이메일의 문제점을 분석하고 개선 방안을 제시해.\n"
                "반드시 아래 JSON 형식으로만 응답해. 그 외 문장은 절대 포함하지 마.\n\n"
                "예시:\n"
                "{\n"
                "  \"issues\": [\"제목이 너무 일반적임\", \"본문이 너무 길어서 읽기 어려움\"],\n"
                "  \"suggestions\": [\"더 구체적인 제목으로 변경\", \"본문을 2-3문단으로 축약\"],\n"
                "  \"priority\": \"high\"\n"
                "}\n\n"
                "priority 값은 다음 중 하나여야 해: high, medium, low"
            )
        },
        {
            "role": "user",
            "content": f"이메일 내용:\n제목: {email_content.get('subject', '')}\n본문: {email_content.get('body', '')}\n\n사용자 피드백: {user_feedback}\n\n위 내용을 바탕으로 이메일의 문제점을 분석해줘."
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            timeout=15
        )
        content = response.choices[0].message.content

        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return {
                "issues": result.get("issues", []),
                "suggestions": result.get("suggestions", []),
                "priority": result.get("priority", "medium")
            }
    except Exception as e:
        pass

    return {
        "issues": ["분석 중 오류가 발생했습니다"],
        "suggestions": ["이메일을 다시 작성해주세요"],
        "priority": "medium"
    }


def regenerate_email_with_feedback(
        project_id: int,
        lead_info: dict,
        original_email: dict,
        user_feedback: str,
        email_type: str = "initial"
) -> dict:
    """
    사용자 피드백을 바탕으로 이메일을 재생성
    Args:
        project_id: 프로젝트 ID
        lead_info: 고객 정보
        original_email: 원본 이메일 {"subject": str, "body": str}
        user_feedback: 사용자 피드백
        email_type: "initial" 또는 "followup"
    Returns: {"subject": str, "body": str}
    """

    # 이메일 문제점 분석
    issues_analysis = analyze_email_issues(original_email, user_feedback)

    context = project_contexts.get(project_id, "등록된 사업 설명이 없습니다.")

    # 이메일 타입에 따른 시스템 메시지 설정
    if email_type == "initial":
        system_content = (
            "너는 B2B 세일즈 이메일 재작성 전문가야.\n"
            "사용자의 피드백을 바탕으로 이메일을 개선해.\n"
            "다음 JSON 형식으로만 응답해. 설명은 포함하지 마.\n"
            "{\n"
            "  \"subject\": \"개선된 이메일 제목\",\n"
            "  \"body\": \"개선된 이메일 본문\"\n"
            "}\n\n"
            "이메일에는 다음 요소를 포함해:\n"
            "- 고객 상황 언급\n"
            "- 우리 사업/서비스의 핵심 가치 제안\n"
            "- 기대 효과 2~3가지\n"
            "- 회신 유도 문구"
        )
    else:  # followup
        system_content = (
            "너는 B2B 세일즈 후속 이메일 재작성 전문가야.\n"
            "사용자의 피드백을 바탕으로 후속 이메일을 개선해.\n"
            "다음 JSON 형식으로만 응답해. 설명은 포함하지 마.\n"
            "{\n"
            "  \"subject\": \"개선된 후속 이메일 제목\",\n"
            "  \"body\": \"개선된 후속 이메일 본문\"\n"
            "}\n\n"
            "후속 이메일에는 다음 요소를 포함해:\n"
            "- 이전 제안에 대한 추가 정보\n"
            "- 고객의 우려사항 해결\n"
            "- 구체적인 다음 단계 제시"
        )

    messages = [
        {
            "role": "system",
            "content": system_content
        },
        {
            "role": "user",
            "content": (
                f"사업 설명: {context}\n"
                f"고객 정보: {lead_info}\n"
                f"원본 이메일:\n제목: {original_email.get('subject', '')}\n본문: {original_email.get('body', '')}\n"
                f"사용자 피드백: {user_feedback}\n"
                f"분석된 문제점: {issues_analysis['issues']}\n"
                f"개선 제안: {issues_analysis['suggestions']}\n\n"
                f"위 정보를 바탕으로 개선된 이메일을 작성해줘."
            )
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            timeout=20
        )
        content = response.choices[0].message.content

        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return {
                "subject": result.get("subject", ""),
                "body": result.get("body", "")
            }
    except Exception as e:
        pass

    # 실패 시 기본 응답
    return {
        "subject": "개선된 제안",
        "body": "사용자 피드백을 반영하여 이메일을 개선했습니다."
    }


def handle_email_rejection(
        project_id: int,
        lead_info: dict,
        original_email: dict,
        user_feedback: str,
        email_type: str = "initial"
) -> dict:
    """
    이메일 거부 시 처리하는 통합 함수
    Returns: {"action": str, "new_email": dict, "analysis": dict, "improvements": list}
    """

    # 이메일 문제점 분석
    analysis = analyze_email_issues(original_email, user_feedback)

    # 우선순위가 높거나 문제가 심각한 경우 새로 작성
    if analysis["priority"] == "high" or len(analysis["issues"]) > 2:
        new_email = regenerate_email_with_feedback(
            project_id, lead_info, original_email, user_feedback, email_type
        )
        return {
            "action": "regenerate",
            "new_email": new_email,
            "analysis": analysis,
            "improvements": analysis["suggestions"],
            "message": "문제점이 심각하여 이메일을 새로 작성했습니다."
        }
    else:
        # 문제가 경미한 경우 개선된 이메일 제공
        improved_email = regenerate_email_with_feedback(
            project_id, lead_info, original_email, user_feedback, email_type
        )
        return {
            "action": "improve",
            "new_email": improved_email,
            "analysis": analysis,
            "improvements": analysis["suggestions"],
            "message": "기존 이메일을 개선했습니다."
        }