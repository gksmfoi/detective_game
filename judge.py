import os
from openai import OpenAI


def get_client():
    try:
        import streamlit as st
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key:
            return OpenAI(api_key=api_key)
    except Exception:
        pass
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def judge_accusation(case: dict, accused_id: str, reason: str, collected_clues: list) -> dict:
    client = get_client()
    truth = case["truth"]
    is_correct = accused_id == truth["culprit_id"]
    accused_name = next(
        (s["name"] for s in case["suspects"] if s["id"] == accused_id), accused_id
    )

    prompt = f"""당신은 추리 게임의 심판입니다. 자연스러운 한국어 구어체로 작성하세요.

[사건 진실]
진범: {truth['culprit_name']} | 동기: {truth['motive']}
결정적 증거: {truth['decisive_evidence']}

[플레이어 추리]
지목: {accused_name} | 이유: {reason}
수집 단서: {', '.join(collected_clues) if collected_clues else '없음'}
정답 여부: {'정답' if is_correct else '오답'}

3~5문장으로 탐정 평가를 작성하세요.
- 잘한 점과 놓친 점을 구체적으로 언급하세요
- 자연스러운 한국어 구어체로 작성하세요
- 격려하는 말로 마무리하세요"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        feedback = res.choices[0].message.content.strip()
    except Exception as e:
        print(f"[judge] 오류: {e}")
        feedback = "평가를 생성하는 중 오류가 발생했습니다."

    return {"is_correct": is_correct, "feedback": feedback}
