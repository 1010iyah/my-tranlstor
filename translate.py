import streamlit as st
import openai
import base64

# 페이지 기본 설정
st.set_page_config(page_title="ONDA AI | 글로벌 감성 자막 번역기🎬", page_icon="🎬", layout="wide")

# 타이틀 및 브랜드 소개
st.title("ONDA AI | 글로벌 감성 자막 번역기🎬")
st.caption("🌐 **ONDA**: Open NJB Discover Across")
st.markdown("한국어와 영언의 인터넷 밈, 구어체를 최신 현지 감성으로 자연스럽고 위트있게 번역해 드립니다.")

# API Key 설정 (Secrets 사용 우선, 없을 경우 사이드바 입력 가능)
api_key = None
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    with st.sidebar:
        st.warning("⚠️ Secrets 설정이 되어있지 않아 직접 키 입력 모드로 작동합니다.")
        api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

if not api_key:
    st.info("서비스 준비 중이거나 API Key 설정이 필요합니다.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# ----------------- 프롬프트 정의 -----------------
# 1. 한국어 -> 영어 프롬프트
system_prompt_ko_to_en = """
You are a native slang expert and Gen-Z/Alpha internet culture translator.
Translate Korean subtitles into ultra-trendy American English suitable for YouTube, Twitch chat, and TikTok.

[Style Guidelines]:
1. Use casual internet slang, AAVE/hood slang (e.g., 'wsp gng', 'fr fr', 'no cap', 'trippin', 'ggs gng'), and Gen-Z/Aesthetic brainrot culture.
2. Make it funny, slightly exaggerated, or humorous rather than literal.
3. Keep the energy upbeat and natural for American internet creators.

[Mandatory Dictionary / Fixed Slang Rules]:
- '야르' -> 'yarrr'
- '영크크' -> 'Gen Z core' (or 'Young Creator Crew')
- '늙크크' -> 'UNC core'
- '줴줴이야' -> 'ggs gng'
- Translate other Korean memes, slang, and puns into their closest humorous American equivalent.
"""

# 2. 영어 -> 한국어 프롬프트
system_prompt_en_to_ko = """
You are a trendy Korean internet culture expert and subtitle translator.
Translate English subtitles/slang/tweets into modern Korean internet meme style (suitable for Korean YouTube, TikTok, and community posts).

[Style Guidelines]:
1. Use trendy Korean internet slang, natural spoken tone, and online community/YouTube subtitle vibes (e.g., '~했음 ㄷㄷ', '폼 미쳤다', '레전드', '개웃기네').
2. Avoid stiff, robot-like literal translations (e.g., do not translate 'What's up' as '무엇이 위인가요'). Translate intent into natural Korean humor/vibes.
3. Keep it witty, funny, and punchy.
"""

# 탭 구성 (텍스트 입력 / 이미지 업로드)
tab1, tab2 = st.tabs(["📝 텍스트/SRT 입력", "🖼️ 이미지 업로드"])

# ----------------- 탭 1: 텍스트 입력 -----------------
with tab1:
    st.write("### 자막 및 문장 입력")
    
    # 번역 방향 선택 버튼 (라디오 버튼)
    direction = st.radio(
        "번역 방향을 선택하세요:",
        ["🔥 한국어 ➡ 영어 (US Gen-Z/AAVE Vibe)", "🇰🇷 영어 ➡ 한국어 (한국 인터넷 밈/구어체)"],
        horizontal=True
    )
    
    # 적절한 시스템 프롬프트 선택
    current_prompt = system_prompt_ko_to_en if "한국어 ➡ 영어" in direction else system_prompt_en_to_ko

    col1, col2 = st.columns([5, 1])
    
    with col1:
        input_text = st.text_area(
            "자막 입력 칸",
            placeholder="번역할 한국어 또는 영어 문장을 입력하세요...",
            height=130,
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")
        st.write("")
        translate_btn = st.button("🔥번역", use_container_width=True)

    if translate_btn:
        if input_text.strip():
            with st.spinner("ONDA AI가 감성 넘치게 번역 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": current_prompt},
                            {"role": "user", "content": input_text}
                        ]
                    )
                    result = response.choices[0].message.content
                    st.success("번역 완료!")
                    st.text_area("🔥 번역 결과", value=result, height=180)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
        else:
            st.warning("문장을 입력해 주세요.")

# ----------------- 탭 2: 이미지 업로드 -----------------
with tab2:
    st.write("### 이미지 속 텍스트 번역")
    
    direction_img = st.radio(
        "이미지 번역 방향 선택:",
        ["🔥 한국어 ➡ 영어 (US Gen-Z/AAVE Vibe)", "🇰🇷 영어 ➡ 한국어 (한국 인터넷 밈/구어체)"],
        horizontal=True,
        key="img_radio"
    )
    current_img_prompt = system_prompt_ko_to_en if "한국어 ➡ 영어" in direction_img else system_prompt_en_to_ko

    uploaded_file = st.file_uploader("텍스트가 포함된 이미지를 올려주세요 (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="업로드한 이미지", use_container_width=True)
        
        img_btn = st.button("🖼️ 이미지 텍스트 번역하기")
        if img_btn:
            with st.spinner("이미지 속 텍스트를 읽고 번역하는 중..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    
                    prompt_instruction = "Extract text from this image and translate it to trendy American English according to guidelines." if "한국어 ➡ 영어" in direction_img else "Extract text from this image and translate it to trendy Korean internet slang according to guidelines."

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": current_img_prompt},
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_instruction},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        ]
                    )
                    result = response.choices[0].message.content
                    st.success("이미지 번역 완료!")
                    st.text_area("🔥 번역 결과", value=result, height=180)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")