import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_suspect_response(suspect: dict, case: dict, history: list) -> tuple[str, str | None]:
    is_culprit = suspect.get("is_culprit", False)

    system_prompt = f"""You are a suspect in a Korean detective mystery game.

Character info:
- Name: {suspect['name']}
- Job: {suspect['job']}
- Personality: {suspect['personality']}
- Alibi: {suspect['alibi']}
- Hidden secret (never reveal directly): {suspect['secret']}

Role: {"You are the CULPRIT. Subtly include contradictions in your alibi. React defensively to sharp questions. Never confess." if is_culprit else "You are INNOCENT. Speak consistently and calmly explain your alibi."}

[CRITICAL LANGUAGE RULES - MUST FOLLOW]
- Always respond in natural, conversational Korean
- Use natural Korean expressions: 저는, 제가, 그날, 솔직히, 아무래도
- NEVER use translated/robotic expressions: 나는, 여러분, 참가자들, 본인은
- Speak exactly like a real Korean person being questioned by a detective
- Keep responses to 2-4 sentences maximum
- Show emotions naturally (nervousness, confusion, frustration)
- Never mention this is a game or that you are an AI

[Natural Korean response examples]
"그날은 저 혼자 사무실에 있었어요. 아무도 없었고... 좀 불리하게 들릴 수 있다는 거 알아요."
"저랑 피해자요? 그냥 아는 사이였어요. 특별한 관계는 아니었고요."
"왜 자꾸 그 부분을 물어보시는 거예요? 저는 아무것도 숨기는 게 없어요."
"솔직히 말씀드리면... 그날 제가 거기 있었던 건 맞는데, 그게 다예요."
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.8,
            max_tokens=300,
            messages=messages
        )
        reply = res.choices[0].message.content.strip()
    except Exception as e:
        print(f"[interrogation] 오류: {e}")
        reply = "잠깐만요... 지금 좀 혼란스럽네요."

    # 단서 공개 로직
    revealed_clue = None
    clues = case.get("clues", [])
    user_turns = sum(1 for m in history if m["role"] == "user")
    if user_turns >= 2 and clues:
        idx = ["S1", "S2", "S3"].index(suspect["id"]) if suspect["id"] in ["S1", "S2", "S3"] else 0
        if idx < len(clues):
            clue = clues[idx]
            revealed_clue = clue.get("description") if isinstance(clue, dict) else clue

    return reply, revealed_clue
