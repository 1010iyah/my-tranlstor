import streamlit as st
import openai
import base64
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(
    page_title="ONDA AI | Global Meme Subtitles",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 커스텀 CSS 스타일링
custom_css = """
<style>
    /* 메인 배경 및 기본 폰트 설정 */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 상단 헤더 커스텀 */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 0.8rem;
    }
    .brand-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.1);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }

    /* 탭 스타일 개편 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(30, 41, 59, 0.5);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 16px;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
    }

    /* 버튼 모던 스타일링 */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
    }

    /* 텍스트 영역 스타일링 */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-size: 0.95rem !important;
        padding: 1rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* 안내 메시지 카드 */
    .usage-card {
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0.6rem 1rem;
        color: #cbd5e1;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 세션 상태에 번역 기록 시간 저장
if "usage_history" not in st.session_state:
    st.session_state.usage_history = []

def get_recent_usage_count():
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    st.session_state.usage_history = [t for t in st.session_state.usage_history if t > cutoff]
    return len(st.session_state.usage_history)

# 3. 히어로 헤더 영역
st.markdown("""
<div class="hero-container">
    <div class="brand-badge">ONDA AI</div>
    <div class="hero-title">Open NJB Discover Across</div>
    <div class="hero-subtitle">한국어 밈과 미국 현지 Gen-Z 감성을 자유롭게 넘나드는 AI 자막 번역기</div>
</div>
""", unsafe_allow_html=True)

# 사용량 정보
recent_count = get_recent_usage_count()
remaining_count = max(0, 20 - recent_count)
st.markdown(f"""
<div class="usage-card">
    ⚡ <b>오늘의 남은 무료 번역</b>: <span style="color:#38bdf8; font-weight:bold;">{remaining_count}회</span> / 20회 (24시간 기준 자동 갱신)
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
        height=120,
        label_visibility="collapsed"
    )
    
    translate_btn = st.button("🔥 감성 번역하기", use_container_width=True)

    if translate_btn:
        if recent_count >= 20:
            st.error("⚠️ 24시간 동안의 무료 번역 횟수(20회)를 모두 사용하셨습니다. 나중에 다시 시도해 주세요.")
        elif not input_text.strip():
            st.warning("문장을 입력해 주세요.")
        else:
            with st.spinner("ONDA AI가 트렌디한 감성으로 다듬는 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": current_prompt},
                            {"role": "user", "content": input_text}
                        ]
                    )
                    result = response.choices[0].message.content
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
            if recent_count >= 20:
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
                        st.session_state.usage_history.append(datetime.now())
                        
                        st.markdown("#### ✨ 번역 결과")
                        st.text_area("결과창 이미지", value=result, height=150, label_visibility="collapsed")
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")