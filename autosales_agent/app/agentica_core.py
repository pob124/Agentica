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
        try:
            email = generate_initial_email(project_id, lead_info)
            result.append({
                "lead": lead_info,
                "email": email,
                "status": "success"
            })
        except Exception as e:
            # 개별 기업 처리 실패 시에도 다른 기업들은 계속 처리
            result.append({
                "lead": lead_info,
                "email": {
                    "subject": "제안드립니다",
                    "body": "안녕하세요, 고객님의 상황을 고려한 제안을 드리고자 연락드립니다..."
                },
                "status": "error",
                "error": str(e)
            })

    return result


def generate_followup_email(project_id: int, lead_id: int, feedback_summary: str) -> dict:
    """
    사용자 피드백 기반 이메일 재작성
    Returns: {"subject": str, "body": str}
    """

    context = project_contexts.get(project_id, "등록된 사업 설명이 없습니다.")

    messages = [
        {
            "role": "system",
            "content": (
                "너는 B2B 세일즈 이메일 재작성 전문가야.\n\n"
                "상황: 세일즈 담당자가 AI가 생성한 이메일을 검토한 후, 이메일 품질에 대한 피드백을 제공했어.\n"
                "역할: 세일즈 담당자의 피드백을 바탕으로 더 나은 이메일을 재작성하는 AI 어시스턴트\n\n"
                "다음은 특정 사업에 대한 설명과 세일즈 담당자의 피드백이야.\n"
                "이를 바탕으로 개선된 이메일을 작성해줘.\n\n"
                "반드시 아래 형식의 JSON으로만 응답해. JSON 외 설명은 절대 포함하지 마.\n\n"
                "예시:\n"
                "{\n"
                "  \"subject\": \"개선된 제안 - AI/ML 기업을 위한 맞춤형 솔루션\",\n"
                "  \"body\": \"안녕하세요, 귀사의 AI/ML 분야에서 직면하는 구체적인 문제점을 해결하는 솔루션을 제안드립니다...\"\n"
                "}\n\n"
                f"사업 설명:\n{context}"
            )
        },
        {
            "role": "user",
            "content": f"다음 세일즈 담당자 피드백을 바탕으로 개선된 이메일을 작성해줘:\n{feedback_summary}"
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
        "subject": "개선된 제안",
        "body": "사용자 피드백을 반영하여 이메일을 개선했습니다."
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


def extract_parameters_from_prompt(prompt: str, intent: str) -> dict:
    """
    프롬프트에서 특정 intent에 필요한 파라미터를 추출
    """
    if intent == "register_project":
        # "이런 사업 할거야: AI 솔루션 제공" → description 추출
        if ":" in prompt:
            description = prompt.split(":", 1)[1].strip()
            return {"description": description}
        return {}
    
    elif intent == "initial_email":
        # "프로젝트 1번에 테크스타트업 3곳에 메일 보내줘" → project_id 추출
        import re
        project_match = re.search(r'프로젝트\s*(\d+)', prompt)
        if project_match:
            return {"project_id": int(project_match.group(1))}
        return {}
    
    elif intent == "email_rewrite_request":
        # "메일이 이상하게 나왔어 다시 작성해줘" → 피드백 추출
        feedback_keywords = ["이상하게", "별로", "개선", "다시", "수정"]
        for keyword in feedback_keywords:
            if keyword in prompt:
                return {"user_feedback": f"사용자 피드백: {prompt}"}
        return {}
    
    return {}


# 프롬프트 해석 함수 (ai 기반)
def analyze_prompt_ai(prompt: str) -> dict:
    """
    GPT를 활용한 인텐트 분류 및 파라미터 추출
    Returns: {"intent": str, "extracted_params": dict, "confidence": float}
    """
    messages = [
        {
            "role": "system",
            "content": (
                "사용자 요청을 분석하여 의도(intent)와 필요한 파라미터를 추출해줘.\n"
                "다음 JSON 형식으로만 응답해:\n"
                "{\n"
                "  \"intent\": \"register_project|initial_email|followup_email|email_rewrite_request|list_projects|list_leads|add_lead|unknown\",\n"
                "  \"extracted_params\": {\n"
                "    \"project_id\": null,\n"
                "    \"description\": null,\n"
                "    \"leads\": null,\n"
                "    \"lead_id\": null,\n"
                "    \"feedback_text\": null,\n"
                "    \"user_feedback\": null\n"
                "  },\n"
                "  \"confidence\": 0.0\n"
                "}\n\n"
                "파라미터 사용 패턴:\n"
                "- register_project: description (사업 설명)\n"
                "- initial_email: project_id (프로젝트 ID), leads (기업 정보)\n"
                "- followup_email: project_id, lead_id, feedback_text (피드백 내용)\n"
                "- email_rewrite_request: user_feedback (개선 요청)\n"
                "- list_projects: 파라미터 없음\n"
                "- list_leads: 파라미터 없음\n"
                "- add_lead: 파라미터 없음\n\n"
                "자연스러운 표현 예시:\n"
                "- '이런 사업 할거야: AI 솔루션 제공' → intent: register_project, description: 'AI 솔루션 제공'\n"
                "- '프로젝트 1번에 메일 보내줘' → intent: initial_email, project_id: 1\n"
                "- '메일이 이상하게 나왔어 다시 작성해줘' → intent: email_rewrite_request, user_feedback: '메일이 이상하게 나왔어'\n"
                "- '지금 어떤 사업 하고 있는지 말해줘' → intent: list_projects\n\n"
                "파라미터가 명확하지 않으면 null로 설정해."
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
        content = response.choices[0].message.content
        
        # JSON 파싱 - 더 강건한 방식으로 개선
        import json
        import re
        
        # JSON 블록 찾기
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본값 반환
                return {
                    "intent": "unknown",
                    "extracted_params": {},
                    "confidence": 0.0
                }
        else:
            # JSON 블록을 찾지 못한 경우 기본값 반환
            return {
                "intent": "unknown",
                "extracted_params": {},
                "confidence": 0.0
            }
        
        # 추가 파라미터 추출
        intent = result.get("intent", "unknown")
        additional_params = extract_parameters_from_prompt(prompt, intent)
        
        # 추출된 파라미터를 기존 파라미터와 병합
        for key, value in additional_params.items():
            if value is not None:
                result["extracted_params"][key] = value
        
        return result
    except Exception as e:
        # 실패 시 기본값 반환
        return {
            "intent": "unknown",
            "extracted_params": {},
            "confidence": 0.0
        }


# 챗봇 핸들러 함수
def chatbot_handler(intent: str, user_prompt: str = "", payload: Dict[str, Any] = {}, debug: bool = False) -> Dict[str, Any]:
    # 사용자가 직접 선택한 intent 사용
    merged_payload = payload.copy()

    if intent == "register_project":
        project_id = merged_payload.get("project_id")
        description = merged_payload.get("description")
        if not project_id or not description:
            return {"error": "'project_id'와 'description'은 필수입니다.", "intent": intent if debug else None}
        return register_project_context(project_id, description)

    elif intent == "generate_initial_emails":
        project_id = merged_payload.get("project_id")
        leads = merged_payload.get("leads")  # list or dict

        if not project_id or not leads:
            return {"error": "'project_id'와 'leads'는 필수입니다.", "intent": intent if debug else None}

        # 다중 기업 처리 - 각 기업별로 개별 AI 호출
        if isinstance(leads, list):
            results = []
            for i, lead in enumerate(leads):
                try:
                    email = generate_initial_email(project_id, lead)
                    results.append({
                        "lead": lead,
                        "email": email,
                        "status": "success",
                        "lead_index": i + 1
                    })
                except Exception as e:
                    results.append({
                        "lead": lead,
                        "email": {
                            "subject": "제안드립니다",
                            "body": "안녕하세요, 고객님의 상황을 고려한 제안을 드리고자 연락드립니다..."
                        },
                        "status": "error",
                        "error": str(e),
                        "lead_index": i + 1
                    })
            
            return {
                "type": "multiple_initial_emails",
                "project_id": project_id,
                "total_leads": len(leads),
                "success_count": len([r for r in results if r["status"] == "success"]),
                "error_count": len([r for r in results if r["status"] == "error"]),
                "emails": results
            }
        else:
            # 단일 기업 객체인 경우
            return generate_initial_email(project_id, leads)

    elif intent == "generate_followup_emails":
        project_id = merged_payload.get("project_id")
        leads = merged_payload.get("leads")
        user_feedback = merged_payload.get("user_feedback")

        if not project_id or not leads or not user_feedback:
            return {"error": "'project_id', 'leads', 'user_feedback'는 필수입니다.", "intent": intent if debug else None}

        # 다중 기업 처리 - 각 기업별로 개별 AI 호출
        if isinstance(leads, list):
            results = []
            for i, lead in enumerate(leads):
                try:
                    # 사용자 피드백 기반 이메일 재생성
                    email = generate_followup_email(project_id, i + 1, user_feedback)
                    results.append({
                        "lead": lead,
                        "email": email,
                        "status": "success",
                        "lead_index": i + 1
                    })
                except Exception as e:
                    results.append({
                        "lead": lead,
                        "email": {
                            "subject": "개선된 제안",
                            "body": "사용자 피드백을 반영하여 이메일을 개선했습니다."
                        },
                        "status": "error",
                        "error": str(e),
                        "lead_index": i + 1
                    })
            
            return {
                "type": "multiple_followup_emails",
                "project_id": project_id,
                "total_leads": len(leads),
                "success_count": len([r for r in results if r["status"] == "success"]),
                "error_count": len([r for r in results if r["status"] == "error"]),
                "emails": results
            }
        else:
            # 단일 기업 객체인 경우
            return generate_followup_email(project_id, 1, user_feedback)

    elif intent == "generate_feedback_emails":
        project_id = merged_payload.get("project_id")
        leads = merged_payload.get("leads")
        user_feedback = merged_payload.get("user_feedback")
        original_email = merged_payload.get("original_email")

        if not project_id or not leads or not user_feedback:
            return {"error": "'project_id', 'leads', 'user_feedback'는 필수입니다.", "intent": intent if debug else None}

        # 다중 기업 처리 - 각 기업별로 개별 AI 호출
        if isinstance(leads, list):
            results = []
            for i, lead in enumerate(leads):
                try:
                    # 피드백 기반 이메일 재생성
                    email = regenerate_email_with_feedback(project_id, lead, original_email, user_feedback, "initial")
                    results.append({
                        "lead": lead,
                        "email": email,
                        "status": "success",
                        "lead_index": i + 1
                    })
                except Exception as e:
                    results.append({
                        "lead": lead,
                        "email": {
                            "subject": "개선된 제안",
                            "body": "사용자 피드백을 반영하여 이메일을 개선했습니다."
                        },
                        "status": "error",
                        "error": str(e),
                        "lead_index": i + 1
                    })
            
            return {
                "type": "multiple_feedback_emails",
                "project_id": project_id,
                "total_leads": len(leads),
                "success_count": len([r for r in results if r["status"] == "success"]),
                "error_count": len([r for r in results if r["status"] == "error"]),
                "emails": results
            }
        else:
            # 단일 기업 객체인 경우
            return regenerate_email_with_feedback(project_id, leads, original_email, user_feedback, "initial")

    elif intent == "improve_email":
        project_id = merged_payload.get("project_id")
        lead_info = merged_payload.get("lead_info")
        original_email = merged_payload.get("original_email")
        user_feedback = merged_payload.get("user_feedback")
        email_type = merged_payload.get("email_type", "initial")

        if not all([project_id, lead_info, original_email, user_feedback]):
            return {"error": "필수 파라미터 누락: 'project_id', 'lead_info', 'original_email', 'user_feedback'", "intent": intent if debug else None}

        return handle_email_rejection(project_id, lead_info, original_email, user_feedback, email_type)

    elif intent == "analyze_email":
        email_content = merged_payload.get("email_content")
        user_feedback = merged_payload.get("user_feedback")
        
        if not email_content or not user_feedback:
            return {"error": "'email_content'와 'user_feedback'는 필수입니다.", "intent": intent if debug else None}
        
        return analyze_email_issues(email_content, user_feedback)

    elif intent == "list_projects":
        return {"projects": list(project_contexts.keys()), "message": "등록된 프로젝트 목록입니다."}

    elif intent == "list_leads":
        return {"leads": [], "message": "기업 목록 조회 기능은 아직 구현되지 않았습니다."}

    else:
        return {
            "error": f"지원하지 않는 intent입니다: {intent}",
            "supported_intents": ["register_project", "generate_initial_emails", "generate_followup_emails", "generate_feedback_emails", "improve_email", "analyze_email", "list_projects", "list_leads"],
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