import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

try:
    import streamlit as st
    api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
except Exception:
    api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """당신은 텍스트 기반 추리 게임의 사건 설계자입니다.
사용자는 탐정 역할을 수행합니다.
당신은 매번 새로운 가상의 사건을 생성해야 합니다.

반드시 지켜야 할 규칙:
1. 사건은 완전히 허구이며 실제 인물, 실제 사건과 직접 연결하지 않습니다.
2. 폭력적·선정적 묘사는 피하고 대학 수업 시연에 적합한 수준으로 작성합니다.
3. 특정 성별, 국적, 직업이 반복적으로 범인이 되지 않도록 균형 있게 구성합니다.
4. 용의자는 정확히 3명, 진범은 1명입니다.
5. 출력은 반드시 JSON 형식으로만 작성합니다.
6. 사건, 알리바이, 단서, 범행 동기는 서로 논리적으로 일관되어야 합니다.

Respond only in Korean. Write naturally as a native Korean speaker would."""

USER_PROMPT = """새로운 추리 사건을 만들어주세요.
- 무고한 용의자 2명은 검증 가능한 알리바이를 주세요.
- 진범의 알리바이에만 허점이 있어야 합니다.

아래 JSON 구조로만 출력하세요 (다른 텍스트 없이):
{
  "case_title": "사건 제목",
  "case_overview": "사건 개요 (3~4문장)",
  "victim": {"name": "피해자 이름", "description": "피해자 설명"},
  "suspects": [
    {
      "id": "S1", "name": "이름", "gender": "성별", "job": "직업",
      "personality": "성격", "public_description": "공개 설명",
      "alibi": "알리바이", "secret": "숨겨진 비밀", "is_culprit": false
    },
    {
      "id": "S2", "name": "이름", "gender": "성별", "job": "직업",
      "personality": "성격", "public_description": "공개 설명",
      "alibi": "알리바이", "secret": "숨겨진 비밀", "is_culprit": true
    },
    {
      "id": "S3", "name": "이름", "gender": "성별", "job": "직업",
      "personality": "성격", "public_description": "공개 설명",
      "alibi": "알리바이", "secret": "숨겨진 비밀", "is_culprit": false
    }
  ],
  "clues": ["핵심 단서 1", "핵심 단서 2", "핵심 단서 3"],
  "truth": {
    "culprit_id": "S2", "culprit_name": "진범 이름",
    "motive": "동기", "full_story": "전체 진실", "decisive_evidence": "결정적 증거"
  }
}"""


def generate_case() -> dict | None:
    for attempt in range(3):
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=2048,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT},
                ]
            )
            raw = res.choices[0].message.content.strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            case = json.loads(raw.strip())

            # 검증
            assert "case_title" in case
            assert "suspects" in case and len(case["suspects"]) == 3
            assert "truth" in case
            assert any(s["is_culprit"] for s in case["suspects"])

            return case
        except Exception as e:
            print(f"[case_generator] 시도 {attempt+1} 실패: {e}")
    return None
