import streamlit as st
import openai
import base64
from datetime import datetime, timedelta

# 1. 페이지 기본 설정 (Centered 800px 모드)
st.set_page_config(
    page_title="ONDA AI | Global Meme Subtitles",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 관리자 비밀번호 설정
MASTER_KEY = "ondaNJB1543"

# 사이드바 하단에 비밀 관리자 입력창 배치
with st.sidebar:
    st.write("---")
    admin_input = st.text_input("System Key", type="password", help="관리자 전용")

# 관리자 여부 판별
is_admin = (admin_input == MASTER_KEY)

# 2. 시안 C (Minimal Dark Stack) 커스텀 CSS
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* 배경 및 기본 폰트 */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* 헤더 카드 */
    .hero-container {
        text-align: center;
        padding: 2rem 1.2rem;
        background: #111827;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .brand-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.1);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 400;
    }

    /* 사용량 카드 */
    .usage-card {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 0.6rem 1rem;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 1.2rem;
        text-align: center;
    }

    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #111827;
        padding: 5px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 18px;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: #2563eb !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    .stButton > button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px) !important;
    }

    /* 텍스트 상자 스타일 */
    .stTextArea textarea {
        background-color: #111827 !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        font-size: 0.95rem !important;
        padding: 0.9rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }

    /* 라디오 버튼 텍스트 */
    .stRadio label {
        color: #cbd5e1 !important;
        font-weight: 500;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 세션 상태 초기화
if "usage_history" not in st.session_state:
    st.session_state.usage_history = []

def get_recent_usage_count():
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    st.session_state.usage_history = [t for t in st.session_state.usage_history if t > cutoff]
    return len(st.session_state.usage_history)

# 3. 헤더
st.markdown("""
<div class="hero-container">
    <div class="brand-badge">ONDA AI</div>
    <div class="hero-title">Open NJB Discover Across</div>
    <div class="hero-subtitle">한국어 밈과 미국 현지 Gen-Z 감성을 넘나드는 AI 자막 번역기</div>
</div>
""", unsafe_allow_html=True)

# 잔여 횟수 카드
recent_count = get_recent_usage_count()
remaining_count = "♾️" if is_admin else max(0, 20 - recent_count)

st.markdown(f"""
<div class="usage-card">
    ⚡ <b>오늘의 남은 무료 번역</b>: <span style="color:#38bdf8; font-weight:bold;">{remaining_count}회</span> / 20회 (24시간 기준)
</div>
""", unsafe_allow_html=True)

# API Key 설정
api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    with st.sidebar:
        api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

if not api_key:
    st.info("서비스 준비 중이거나 API Key 설정이 필요합니다.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# ----------------- 프롬프트 정의 -----------------
system_prompt_ko_to_en = """
You are a native slang expert and Gen-Z/Alpha internet culture translator.
Translate Korean subtitles into ultra-trendy American English suitable for YouTube, Twitch chat, and TikTok.

[Mandatory Dictionary]:
- '야르' -> 'yarrr'
- '영크크' -> 'Gen Z core'
- '늙크크' -> 'UNC core'
- '줴줴이야' -> 'ggs gng'
"""

system_prompt_en_to_ko = """
You are a trendy Korean internet culture expert and subtitle translator.
Translate English subtitles/slang/tweets into modern Korean internet meme style.
"""

# 4. 메인 탭 인터페이스
tab1, tab2 = st.tabs(["📝 텍스트 입력", "🖼️ 이미지/캡처 번역"])

with tab1:
    direction = st.radio(
        "번역 방향",
        ["🔥 한국어 ➡ 영어 (US Gen-Z/AAVE Vibe)", "🇰🇷 영어 ➡ 한국어 (한국 인터넷 밈/구어체)"],
        horizontal=True,
        label_visibility="collapsed"
    )
    current_prompt = system_prompt_ko_to_en if "한국어 ➡ 영어" in direction else system_prompt_en_to_ko

    input_text = st.text_area(
        "텍스트 입력",
        placeholder="번역하고 싶은 자막이나 밈 문장을 입력하세요...",
        height=130,
        label_visibility="collapsed"
    )
    
    translate_btn = st.button("🔥 번역하기", use_container_width=True)

    if translate_btn:
        if not is_admin and recent_count >= 20:
            st.error("⚠️ 24시간 동안의 무료 번역 횟수(20회)를 모두 사용하셨습니다.")
        elif not input_text.strip():
            st.warning("문장을 입력해 주세요.")
        else:
            with st.spinner("ONDA AI가 번역 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": current_prompt},
                            {"role": "user", "content": input_text}
                        ]
                    )
                    result = response.choices[0].message.content
                    
                    if not is_admin:
                        st.session_state.usage_history.append(datetime.now())
                    
                    st.markdown("#### ✨ 번역 결과")
                    st.text_area("결과창", value=result, height=150, label_visibility="collapsed")
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

with tab2:
    direction_img = st.radio(
        "이미지 번역 방향",
        ["🔥 한국어 ➡ 영어 (US Gen-Z/AAVE Vibe)", "🇰🇷 영어 ➡ 한국어 (한국 인터넷 밈/구어체)"],
        horizontal=True,
        key="img_radio",
        label_visibility="collapsed"
    )
    current_img_prompt = system_prompt_ko_to_en if "한국어 ➡ 영어" in direction_img else system_prompt_en_to_ko

    uploaded_file = st.file_uploader("이미지를 업로드하세요 (PNG, JPG)", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        st.image(uploaded_file, use_container_width=True)
        img_btn = st.button("🖼️ 이미지속 텍스트 번역", use_container_width=True)
        
        if img_btn:
            if not is_admin and recent_count >= 20:
                st.error("⚠️ 24시간 동안의 무료 번역 횟수(20회)를 모두 사용하셨습니다.")
            else:
                with st.spinner("이미지 텍스트 읽는 중..."):
                    try:
                        bytes_data = uploaded_file.getvalue()
                        base64_image = base64.b64encode(bytes_data).decode('utf-8')

                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": current_img_prompt},
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": "Extract text and translate according to guidelines."},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                    ]
                                }
                            ]
                        )
                        result = response.choices[0].message.content
                        
                        if not is_admin:
                            st.session_state.usage_history.append(datetime.now())
                        
                        st.markdown("#### ✨ 번역 결과")
                        st.text_area("결과창 이미지", value=result, height=150, label_visibility="collapsed")
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")