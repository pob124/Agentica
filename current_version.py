from openai import OpenAI, api_key
import os
import json
from dotenv import load_dotenv
load_dotenv(override=True)
from typing import Dict, Any
import re,json

#?꾩젨?곗뭅 ?⑥닔
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#db?곕룞 ?덈릺???쇰떒 諛곗뿴濡?project_contexts: Dict[int, str] = {}

def register_project_context(project_id: int, description: str):
    project_contexts[project_id] = description
    return {"message": f"?꾨줈?앺듃 {project_id} ?ㅻ챸 ????꾨즺"}

def generate_initial_email(project_id: int, lead_info: dict) -> dict:
    context = project_contexts.get(project_id, "?깅줉???ъ뾽 ?ㅻ챸???놁뒿?덈떎.")

    messages = [
        {
            "role": "system",
            "content": (
                "?덈뒗 B2B ?몄씪利??대찓???묒꽦???꾨Ц?쇰줈 ?섎뒗 AI??\n"
                "?ㅼ쓬 JSON ?뺤떇?쇰줈留??묐떟?? ?ㅻ챸? ?ы븿?섏? 留?\n"
                "{\n"
                "  \"subject\": \"?대찓???쒕ぉ\",\n"
                "  \"body\": \"?대찓??蹂몃Ц ?댁슜\"\n"
                "}\n\n"
                "?대찓?쇱뿉???ㅼ쓬 ?붿냼瑜??ы븿??\n"
                "- 怨좉컼 ?곹솴 ?멸툒\n"
                "- ?곕━ ?ъ뾽/?쒕퉬?ㅼ쓽 ?듭떖 媛移??쒖븞\n"
                "- 湲곕? ?④낵 2~3媛吏\n"
                "- ?뚯떊 ?좊룄 臾멸뎄"
            )
        },
        {
            "role": "user",
            "content": f"?ъ뾽 ?ㅻ챸: {context}\n怨좉컼 ?뺣낫: {lead_info}\n??議곌굔??湲곕컲?쇰줈 ?대찓??珥덉븞??JSON ?뺤떇?쇰줈 ?묒꽦?댁쨾."
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
        "subject": "?쒖븞?쒕┰?덈떎",
        "body": "?덈뀞?섏꽭?? 怨좉컼?섏쓽 ?곹솴??怨좊젮???쒖븞???쒕━怨좎옄 ?곕씫?쒕┰?덈떎..."
    }

def generate_followup_email(project_id: int, lead_id: int, feedback_summary: str) -> dict:
    """
    ?쇰뱶諛?湲곕컲 ?꾩냽 硫붿씪 珥덉븞 ?앹꽦
    Returns: {"subject": str, "body": str}
    """

    context = project_contexts.get(project_id, "?깅줉???ъ뾽 ?ㅻ챸???놁뒿?덈떎.")

    messages = [
        {
            "role": "system",
            "content": (
                "?덈뒗 B2B ?몄씪利??꾩냽 ?대찓???묒꽦 ?꾨Ц媛??\n\n"
                "?ㅼ쓬? ?뱀젙 ?ъ뾽??????ㅻ챸怨?怨좉컼 ?쇰뱶諛깆씠??\n"
                "?대? 諛뷀깢?쇰줈 ?꾩냽 ?쒖븞 硫붿씪???묒꽦?댁쨾.\n\n"
                "諛섎뱶???꾨옒 ?뺤떇??JSON?쇰줈留??묐떟?? JSON ???ㅻ챸? ?덈? ?ы븿?섏? 留?\n\n"
                "?덉떆:\n"
                "{\n"
                "  \"subject\": \"湲곗〈 ?쒖븞?????異붽? ?쒖븞 ?쒕┰?덈떎\",\n"
                "  \"body\": \"怨좉컼?섏쓽 ?쇰뱶諛?媛먯궗?쒕┰?덈떎. ?쒖븞?댁＜???댁슜??諛섏쁺?섏뿬 ?ㅼ쓬怨?媛숈? 議곌굔??異붽? ?쒖븞?쒕┰?덈떎...\"\n"
                "}\n\n"
                f"?ъ뾽 ?ㅻ챸:\n{context}"
            )
        },
        {
            "role": "user",
            "content": f"?ㅼ쓬 怨좉컼 ?쇰뱶諛깆쓣 諛뷀깢?쇰줈 ?꾩냽 硫붿씪???묒꽦?댁쨾:\n{feedback_summary}"
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
        "subject": "?꾩냽 ?쒖븞",
        "body": "怨좉컼?섏쓽 ?쇰뱶諛깆쓣 諛뷀깢?쇰줈 異붽? ?쒖븞???쒕┰?덈떎."
    }

def summarize_feedback(feedback_text: str) -> dict:
    """
    怨좉컼 ?묐떟 ?붿빟 諛?媛먯젙 遺꾨쪟
    Returns: {"summary": str, "response_type": str}
    """

    messages = [
        {
            "role": "system",
            "content": (
                "?덈뒗 B2B 怨좉컼 ?쇰뱶諛?遺꾩꽍 ?꾨Ц媛??\n\n"
                "怨좉컼 ?묐떟???붿빟?섍퀬, 湲띿젙??以묐┰??遺?뺤쟻 ?묐떟?몄? 遺꾨쪟??\n"
                "諛섎뱶???꾨옒 JSON ?뺤떇?쇰줈留??묐떟?? 洹???臾몄옣? ?덈? ?ы븿?섏? 留?\n\n"
                "?덉떆:\n"
                "{\n"
                "  \"summary\": \"媛寃⑹씠 遺?댁뒪?쎈떎???묐떟\",\n"
                "  \"response_type\": \"negative\"\n"
                "}\n\n"
                "response_type 媛믪? 諛섎뱶???ㅼ쓬 以??섎굹?ъ빞 ?? positive, neutral, negative"
            )
        },
        {
            "role": "user",
            "content": f"?ㅼ쓬 怨좉컼 ?묐떟??遺꾩꽍?댁쨾:\n{feedback_text}"
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

    # ?ㅽ뙣 ??湲곕낯媛?    return {
        "summary": "?묐떟 遺꾩꽍 以??ㅻ쪟媛 諛쒖깮?덉뒿?덈떎.",
        "response_type": "neutral"
    }

# ?꾨＼?꾪듃 ?댁꽍 ?⑥닔 (議곌굔臾?湲곕컲)
def analyze_prompt_intent(prompt: str) -> str:
    prompt = prompt.lower()

    if any(keyword in prompt for keyword in ["?ъ뾽 ?ㅻ챸", "?꾨줈?앺듃 ?ㅻ챸", "context"]):
        return "register_project"
    elif any(keyword in prompt for keyword in ["泥?硫붿씪", "?쒖븞", "?뚭컻"]):
        return "initial_email"
    elif any(keyword in prompt for keyword in ["?꾩냽", "follow up", "?듭옣"]):
        return "followup_email"
    else:
        return "unknown"

# 梨쀫큸 ?몃뱾???⑥닔
def chatbot_handler(user_prompt: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    intent = analyze_prompt_intent(user_prompt)

    if intent == "register_project":
        project_id = payload.get("project_id")
        description = payload.get("description")

        if not project_id or not description:
            return {"error": "'project_id'? 'description'? ?꾩닔?낅땲??"}

        return register_project_context(project_id, description)

    elif intent == "initial_email":
        project_id = payload.get("project_id")
        lead_info = payload.get("lead_info")

        if not project_id or not lead_info:
            return {"error": "'project_id'? 'lead_info'???꾩닔?낅땲??"}

        return generate_initial_email(project_id, lead_info)


    elif intent == "followup_email":

        project_id = payload.get("project_id")

        lead_id = payload.get("lead_id")

        feedback_text = payload.get("feedback_text")

        if not project_id or not lead_id or not feedback_text:
            return {"error": "'project_id', 'lead_id', 'feedback_text'???꾩닔?낅땲??"}

        feedback = summarize_feedback(feedback_text)

        return generate_followup_email(project_id, lead_id, feedback["summary"])

    else:
        return {
            "error": (
                "?붿껌???댄빐?섏? 紐삵뻽?듬땲?? ?ㅼ쓬 以??섎굹濡??ㅼ떆 ?쒕룄?댁＜?몄슂:\n"
                "- '?대윴 ?ъ뾽???섎젮怨???..'\n"
                "- '??怨좉컼?먭쾶 泥??쒖븞 硫붿씪 ?묒꽦?댁쨾'\n"
                "- '?꾩냽 硫붿씪 ?묒꽦?댁쨾'"
            )
        }

def analyze_email_issues(email_content: dict, user_feedback: str) -> dict:
    """
    ?ъ슜???쇰뱶諛깆쓣 諛뷀깢?쇰줈 ?대찓?쇱쓽 臾몄젣?먯쓣 遺꾩꽍
    Returns: {"issues": list, "suggestions": list, "priority": str}
    """
    
    messages = [
        {
            "role": "system",
            "content": (
                "?덈뒗 B2B ?대찓???덉쭏 遺꾩꽍 ?꾨Ц媛??\n\n"
                "?ъ슜?먯쓽 ?쇰뱶諛깆쓣 諛뷀깢?쇰줈 ?대찓?쇱쓽 臾몄젣?먯쓣 遺꾩꽍?섍퀬 媛쒖꽑 諛⑹븞???쒖떆??\n"
                "諛섎뱶???꾨옒 JSON ?뺤떇?쇰줈留??묐떟?? 洹???臾몄옣? ?덈? ?ы븿?섏? 留?\n\n"
                "?덉떆:\n"
                "{\n"
                "  \"issues\": [\"?쒕ぉ???덈Т ?쇰컲?곸엫\", \"蹂몃Ц???덈Т 湲몄뼱???쎄린 ?대젮?\"],\n"
                "  \"suggestions\": [\"??援ъ껜?곸씤 ?쒕ぉ?쇰줈 蹂寃?", \"蹂몃Ц??2-3臾몃떒?쇰줈 異뺤빟\"],\n"
                "  \"priority\": \"high\"\n"
                "}\n\n"
                "priority 媛믪? ?ㅼ쓬 以??섎굹?ъ빞 ?? high, medium, low"
            )
        },
        {
            "role": "user",
            "content": f"?대찓???댁슜:\n?쒕ぉ: {email_content.get('subject', '')}\n蹂몃Ц: {email_content.get('body', '')}\n\n?ъ슜???쇰뱶諛? {user_feedback}\n\n???댁슜??諛뷀깢?쇰줈 ?대찓?쇱쓽 臾몄젣?먯쓣 遺꾩꽍?댁쨾."
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
        "issues": ["遺꾩꽍 以??ㅻ쪟媛 諛쒖깮?덉뒿?덈떎"],
        "suggestions": ["?대찓?쇱쓣 ?ㅼ떆 ?묒꽦?댁＜?몄슂"],
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
    ?ъ슜???쇰뱶諛깆쓣 諛뷀깢?쇰줈 ?대찓?쇱쓣 ?ъ깮??    Args:
        project_id: ?꾨줈?앺듃 ID
        lead_info: 怨좉컼 ?뺣낫
        original_email: ?먮낯 ?대찓??{"subject": str, "body": str}
        user_feedback: ?ъ슜???쇰뱶諛?        email_type: "initial" ?먮뒗 "followup"
    Returns: {"subject": str, "body": str}
    """
    
    # ?대찓??臾몄젣??遺꾩꽍
    issues_analysis = analyze_email_issues(original_email, user_feedback)
    
    context = project_contexts.get(project_id, "?깅줉???ъ뾽 ?ㅻ챸???놁뒿?덈떎.")
    
    # ?대찓????낆뿉 ?곕Ⅸ ?쒖뒪??硫붿떆吏 ?ㅼ젙
    if email_type == "initial":
        system_content = (
            "?덈뒗 B2B ?몄씪利??대찓???ъ옉???꾨Ц媛??\n"
            "?ъ슜?먯쓽 ?쇰뱶諛깆쓣 諛뷀깢?쇰줈 ?대찓?쇱쓣 媛쒖꽑??\n"
            "?ㅼ쓬 JSON ?뺤떇?쇰줈留??묐떟?? ?ㅻ챸? ?ы븿?섏? 留?\n"
            "{\n"
            "  \"subject\": \"媛쒖꽑???대찓???쒕ぉ\",\n"
            "  \"body\": \"媛쒖꽑???대찓??蹂몃Ц\"\n"
            "}\n\n"
            "?대찓?쇱뿉???ㅼ쓬 ?붿냼瑜??ы븿??\n"
            "- 怨좉컼 ?곹솴 ?멸툒\n"
            "- ?곕━ ?ъ뾽/?쒕퉬?ㅼ쓽 ?듭떖 媛移??쒖븞\n"
            "- 湲곕? ?④낵 2~3媛吏\n"
            "- ?뚯떊 ?좊룄 臾멸뎄"
        )
    else:  # followup
        system_content = (
            "?덈뒗 B2B ?몄씪利??꾩냽 ?대찓???ъ옉???꾨Ц媛??\n"
            "?ъ슜?먯쓽 ?쇰뱶諛깆쓣 諛뷀깢?쇰줈 ?꾩냽 ?대찓?쇱쓣 媛쒖꽑??\n"
            "?ㅼ쓬 JSON ?뺤떇?쇰줈留??묐떟?? ?ㅻ챸? ?ы븿?섏? 留?\n"
            "{\n"
            "  \"subject\": \"媛쒖꽑???꾩냽 ?대찓???쒕ぉ\",\n"
            "  \"body\": \"媛쒖꽑???꾩냽 ?대찓??蹂몃Ц\"\n"
            "}\n\n"
            "?꾩냽 ?대찓?쇱뿉???ㅼ쓬 ?붿냼瑜??ы븿??\n"
            "- ?댁쟾 ?쒖븞?????異붽? ?뺣낫\n"
            "- 怨좉컼???곕젮?ы빆 ?닿껐\n"
            "- 援ъ껜?곸씤 ?ㅼ쓬 ?④퀎 ?쒖떆"
        )

    messages = [
        {
            "role": "system",
            "content": system_content
        },
        {
            "role": "user",
            "content": (
                f"?ъ뾽 ?ㅻ챸: {context}\n"
                f"怨좉컼 ?뺣낫: {lead_info}\n"
                f"?먮낯 ?대찓??\n?쒕ぉ: {original_email.get('subject', '')}\n蹂몃Ц: {original_email.get('body', '')}\n"
                f"?ъ슜???쇰뱶諛? {user_feedback}\n"
                f"遺꾩꽍??臾몄젣?? {issues_analysis['issues']}\n"
                f"媛쒖꽑 ?쒖븞: {issues_analysis['suggestions']}\n\n"
                f"???뺣낫瑜?諛뷀깢?쇰줈 媛쒖꽑???대찓?쇱쓣 ?묒꽦?댁쨾."
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

    # ?ㅽ뙣 ??湲곕낯 ?묐떟
    return {
        "subject": "媛쒖꽑???쒖븞",
        "body": "?ъ슜???쇰뱶諛깆쓣 諛섏쁺?섏뿬 ?대찓?쇱쓣 媛쒖꽑?덉뒿?덈떎."
    }

def handle_email_rejection(
    project_id: int,
    lead_info: dict,
    original_email: dict,
    user_feedback: str,
    email_type: str = "initial"
) -> dict:
    """
    ?대찓??嫄곕? ??泥섎━?섎뒗 ?듯빀 ?⑥닔
    Returns: {"action": str, "new_email": dict, "analysis": dict, "improvements": list}
    """
    
    # ?대찓??臾몄젣??遺꾩꽍
    analysis = analyze_email_issues(original_email, user_feedback)
    
    # ?곗꽑?쒖쐞媛 ?믨굅??臾몄젣媛 ?ш컖??寃쎌슦 ?덈줈 ?묒꽦
    if analysis["priority"] == "high" or len(analysis["issues"]) > 2:
        new_email = regenerate_email_with_feedback(
            project_id, lead_info, original_email, user_feedback, email_type
        )
        return {
            "action": "regenerate",
            "new_email": new_email,
            "analysis": analysis,
            "improvements": analysis["suggestions"],
            "message": "臾몄젣?먯씠 ?ш컖?섏뿬 ?대찓?쇱쓣 ?덈줈 ?묒꽦?덉뒿?덈떎."
        }
    else:
        # 臾몄젣媛 寃쎈???寃쎌슦 媛쒖꽑???대찓???쒓났
        improved_email = regenerate_email_with_feedback(
            project_id, lead_info, original_email, user_feedback, email_type
        )
        return {
            "action": "improve",
            "new_email": improved_email,
            "analysis": analysis,
            "improvements": analysis["suggestions"],
            "message": "湲곗〈 ?대찓?쇱쓣 媛쒖꽑?덉뒿?덈떎."
        }
