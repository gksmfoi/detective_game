import streamlit as st
from case_generator import generate_case
from interrogation import get_suspect_response
from judge import judge_accusation

st.set_page_config(page_title="AI 탐정", page_icon="🔍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&family=Noto+Sans+KR:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: #f5f0e8;
    color: #1a1a1a;
}
h1, h2, h3 { font-family: 'Noto Serif KR', serif; color: #1a1a1a; }
header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1200px; }

.stButton > button {
    background: #2c2c2c;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1.5rem;
    font-family: 'Noto Sans KR', sans-serif;
    transition: all 0.2s ease;
    width: 100%;
}
.stButton > button:hover { background: #c9a84c; color: #1a1a1a; }

.case-box {
    background: #ffffff;
    border-left: 3px solid #c9a84c;
    padding: 1.2rem 1.5rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    color: #1a1a1a;
    line-height: 1.8;
}

.suspect-card {
    background: #ffffff;
    border: 1px solid #e0d8c8;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.suspect-card.active { border-color: #c9a84c; background: #fffbf0; }
.suspect-name { font-weight: 700; font-size: 1rem; margin-bottom: 0.2rem; }
.suspect-meta { font-size: 0.78rem; color: #888; margin-bottom: 0.3rem; }
.suspect-desc { font-size: 0.83rem; color: #555; line-height: 1.5; }

.clue-badge {
    display: inline-block;
    background: #fff8e7;
    border: 1px solid #c9a84c;
    color: #8a6a00;
    font-size: 0.8rem;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    margin: 0.2rem;
}

.chat-user {
    background: #e8f0fe;
    border-radius: 8px 8px 2px 8px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0 0.4rem 3rem;
    color: #1a1a1a;
    font-size: 0.88rem;
    line-height: 1.6;
}
.chat-suspect {
    background: #ffffff;
    border-left: 2px solid #c9a84c;
    border-radius: 2px 8px 8px 8px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 3rem 0.4rem 0;
    color: #1a1a1a;
    font-size: 0.88rem;
    line-height: 1.6;
}
.chat-name { font-size: 0.75rem; color: #c9a84c; font-weight: 700; margin-bottom: 0.3rem; }
.chat-hint { color: #aaa; font-size: 0.82rem; font-style: italic; padding: 2rem 0; text-align: center; }

.verdict-correct {
    background: #e8f5e9; border: 1px solid #4caf50;
    border-radius: 8px; padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;
}
.verdict-wrong {
    background: #ffebee; border: 1px solid #f44336;
    border-radius: 8px; padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;
}
.gold { color: #8a6a00; }
.divider { border: none; border-top: 1px solid #e0d8c8; margin: 1.2rem 0; }
.title-bar { border-bottom: 2px solid #e0d8c8; padding-bottom: 1rem; margin-bottom: 1.5rem; }
.section-label { color: #8a6a00; font-size: 0.72rem; letter-spacing: 2px; margin-bottom: 0.5rem; }

.stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid #e0d8c8 !important;
    color: #1a1a1a !important;
    border-radius: 4px !important;
}
.stTextInput input {
    background: #ffffff !important;
    border: 1px solid #e0d8c8 !important;
    color: #1a1a1a !important;
    border-radius: 4px !important;
}
</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {
        "phase": "start", "case": None, "selected_suspect": None,
        "chat_history": {}, "collected_clues": set(),
        "accusation": None, "result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def get_suspect(sid):
    return next((s for s in st.session_state.case["suspects"] if s["id"] == sid), None)


# ══════════════════════════════════════════════════════════════════════════════
#  화면 1: 시작
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.phase == "start":
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; letter-spacing:4px;'>🔍 AI 탐정</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; letter-spacing:2px; font-size:0.82rem; margin-bottom:2rem'>LLM 기반 인터랙티브 추리 게임</p>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div class='case-box' style='margin-bottom:1.2rem'>
            <b>게임 방법</b><br><br>
            1. AI가 새로운 사건을 생성합니다<br>
            2. 용의자를 선택해 자유롭게 심문하세요<br>
            3. 단서를 모아 진범을 추리하세요<br>
            4. 최종 범인을 지목하고 결과를 확인하세요
        </div>
        """, unsafe_allow_html=True)
        st.caption("🔒 입력하신 내용은 서버에 저장되지 않습니다. 본 서비스는 AI가 생성한 가상의 추리 게임입니다.")
        if st.button("🕵 새 사건 시작"):
            with st.spinner("사건을 생성하는 중..."):
                case = generate_case()
            if case:
                st.session_state.case = case
                st.session_state.phase = "interrogate"
                st.session_state.chat_history = {s["id"]: [] for s in case["suspects"]}
                st.session_state.collected_clues = set()
                st.rerun()
            else:
                st.error("사건 생성에 실패했습니다. API 키를 확인해주세요.")


# ══════════════════════════════════════════════════════════════════════════════
#  화면 2: 심문
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "interrogate":
    case = st.session_state.case

    st.markdown(f"""
    <div class='title-bar'>
        <div class='section-label'>CASE FILE</div>
        <div class='gold' style='font-family:Noto Serif KR,serif; font-size:1.6rem'>📁 {case['case_title']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='case-box'>
        <div class='section-label'>사건 개요</div>
        {case['case_overview']}<br><br>
        <span style='color:#888'>피해자</span>&nbsp;
        <b>{case['victim']['name']}</b>
        <span style='color:#888'> — {case['victim']['description']}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.collected_clues:
        clue_html = "".join([f"<span class='clue-badge'>🔍 {c}</span>" for c in st.session_state.collected_clues])
        st.markdown(f"<div style='margin-bottom:1rem'><div class='section-label'>수집된 단서</div>{clue_html}</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown("<div class='section-label'>용의자 목록</div>", unsafe_allow_html=True)
        for s in case["suspects"]:
            active = "active" if st.session_state.selected_suspect == s["id"] else ""
            st.markdown(f"""
            <div class='suspect-card {active}'>
                <div class='suspect-name'>{s['name']}</div>
                <div class='suspect-meta'>{s['job']} · {s['gender']}</div>
                <div class='suspect-desc'>{s['public_description']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("심문하기", key=f"sel_{s['id']}"):
                st.session_state.selected_suspect = s["id"]
                st.rerun()

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        if st.button("⚖ 범인 지목하기"):
            st.session_state.phase = "accuse"
            st.rerun()

    with right:
        sid = st.session_state.selected_suspect
        if sid is None:
            st.markdown("<div class='chat-hint'>← 왼쪽에서 용의자를 선택하세요</div>", unsafe_allow_html=True)
        else:
            suspect = get_suspect(sid)
            st.markdown(f"""
            <div style='margin-bottom:1rem'>
                <div class='section-label'>심문</div>
                <div style='font-family:Noto Serif KR,serif; font-size:1.3rem'>🎙 {suspect['name']}</div>
                <div style='font-size:0.78rem; color:#888; margin-top:0.2rem'>알리바이: {suspect['alibi']}</div>
            </div>
            """, unsafe_allow_html=True)

            history = st.session_state.chat_history[sid]
            if not history:
                st.markdown("<div class='chat-hint'>아래에 질문을 입력해 심문을 시작하세요</div>", unsafe_allow_html=True)
            else:
                chat_html = ""
                for msg in history:
                    if msg["role"] == "user":
                        chat_html += f"<div class='chat-user'>🕵 {msg['content']}</div>"
                    else:
                        chat_html += f"<div class='chat-suspect'><div class='chat-name'>{suspect['name']}</div>{msg['content']}</div>"
                st.markdown(f"<div style='max-height:400px; overflow-y:auto'>{chat_html}</div>", unsafe_allow_html=True)

            col_input, col_btn = st.columns([4, 1])
            with col_input:
                user_input = st.text_input(
                    "질문", key=f"input_{sid}",
                    label_visibility="collapsed",
                    placeholder=f"{suspect['name']}에게 질문하세요..."
                )
            with col_btn:
                send = st.button("전송", key=f"send_{sid}", use_container_width=True)

            if send and user_input:
                history.append({"role": "user", "content": user_input})
                with st.spinner("답변 생성 중..."):
                    reply, revealed_clue = get_suspect_response(suspect, case, history)
                history.append({"role": "assistant", "content": reply})
                if revealed_clue:
                    st.session_state.collected_clues.add(revealed_clue)
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  화면 3: 범인 지목
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "accuse":
    case = st.session_state.case

    st.markdown("""
    <div class='title-bar'>
        <div class='section-label'>FINAL DEDUCTION</div>
        <div class='gold' style='font-family:Noto Serif KR,serif; font-size:1.6rem'>⚖ 최종 추리</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.collected_clues:
        clue_html = "".join([f"<span class='clue-badge'>🔍 {c}</span>" for c in st.session_state.collected_clues])
        st.markdown(f"<div class='case-box'><div class='section-label'>수집한 단서</div>{clue_html}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='case-box' style='color:#aaa'>수집된 단서가 없습니다.</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='section-label'>범인을 지목하세요</div>", unsafe_allow_html=True)
        suspect_names = {s["id"]: s["name"] for s in case["suspects"]}
        choice = st.radio("", options=list(suspect_names.keys()),
                          format_func=lambda x: suspect_names[x], label_visibility="collapsed")
    with col2:
        st.markdown("<div class='section-label'>지목 이유</div>", unsafe_allow_html=True)
        reason = st.text_area("", placeholder="어떤 단서와 심문 내용을 근거로 판단했나요?",
                              height=130, label_visibility="collapsed")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 1])
    with c1:
        if st.button("✅ 범인 지목 확정"):
            if reason.strip():
                with st.spinner("판정 중..."):
                    result = judge_accusation(case, choice, reason, list(st.session_state.collected_clues))
                st.session_state.accusation = {"id": choice, "reason": reason}
                st.session_state.result = result
                st.session_state.phase = "result"
                st.rerun()
            else:
                st.warning("지목 이유를 입력해주세요.")
    with c2:
        if st.button("← 심문으로 돌아가기"):
            st.session_state.phase = "interrogate"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  화면 4: 결과
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "result":
    case = st.session_state.case
    truth = case["truth"]
    accusation = st.session_state.accusation
    result = st.session_state.result
    is_correct = accusation["id"] == truth["culprit_id"]

    st.markdown("""
    <div class='title-bar'>
        <div class='section-label'>CASE CLOSED</div>
        <div class='gold' style='font-family:Noto Serif KR,serif; font-size:1.6rem'>📖 사건의 진실</div>
    </div>
    """, unsafe_allow_html=True)

    if is_correct:
        st.markdown("""
        <div class='verdict-correct'>
            <div style='font-size:2.5rem'>🎉</div>
            <div style='font-family:Noto Serif KR,serif; font-size:1.5rem; color:#2e7d32; margin:0.5rem 0'>정답입니다!</div>
            <div style='color:#555; font-size:0.88rem'>탁월한 추리력으로 진범을 찾아냈습니다.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        accused_name = next(s["name"] for s in case["suspects"] if s["id"] == accusation["id"])
        st.markdown(f"""
        <div class='verdict-wrong'>
            <div style='font-size:2.5rem'>❌</div>
            <div style='font-family:Noto Serif KR,serif; font-size:1.5rem; color:#c62828; margin:0.5rem 0'>오답입니다</div>
            <div style='color:#555; font-size:0.88rem'><b>{accused_name}</b>은(는) 범인이 아닙니다.</div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f"""
        <div class='case-box'>
            <div class='section-label'>사건의 진실</div>
            <div style='margin-bottom:0.8rem'>
                <div style='color:#888; font-size:0.75rem'>진범</div>
                <div style='font-size:1.1rem; font-weight:700'>{truth['culprit_name']}</div>
            </div>
            <div style='margin-bottom:0.8rem'>
                <div style='color:#888; font-size:0.75rem'>동기</div>
                <div style='font-size:0.88rem'>{truth['motive']}</div>
            </div>
            <div style='margin-bottom:0.8rem'>
                <div style='color:#888; font-size:0.75rem'>전말</div>
                <div style='font-size:0.88rem'>{truth['full_story']}</div>
            </div>
            <div>
                <div style='color:#888; font-size:0.75rem'>결정적 증거</div>
                <div style='font-size:0.88rem; color:#8a6a00; font-weight:500'>{truth['decisive_evidence']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if result and result.get("feedback"):
            st.markdown(f"""
            <div class='case-box'>
                <div class='section-label'>탐정 평가</div>
                <div style='font-size:0.88rem; line-height:1.9; color:#555'>{result['feedback']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    _, cb, _ = st.columns([1, 1, 1])
    with cb:
        if st.button("🔄 새 게임 시작"):
            for key in ["phase", "case", "selected_suspect", "chat_history",
                        "collected_clues", "accusation", "result"]:
                del st.session_state[key]
            st.rerun()
