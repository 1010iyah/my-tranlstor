import streamlit as st
import openai
import base64

# 페이지 기본 설정
st.set_page_config(page_title="한글->영어 유튜브 감성 번역기🎬", page_icon="🎬", layout="wide")

# 타이틀 및 안내 문구
st.title("한글->영어 유튜브 감성 번역기🎬")
st.caption("한국어 밈과 구어체를 미국 유튜브 스타일 영어로 바꿔줍니다.")

# 사이드바 API 키 입력
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

if not api_key:
    st.info("왼쪽 사이드바에 OpenAI API Key를 먼저 입력해 주세요.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# 밈 파inet-tuning 및 스타일 정의 프롬프트
system_prompt = """
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

# 탭 구성 (텍스트 입력 / 이미지 업로드)
tab1, tab2 = st.tabs(["📝 텍스트/SRT 입력", "🖼️ 이미지 업로드"])

# ----------------- 탭 1: 텍스트 입력 -----------------
with tab1:
    st.write("### 한국어 자막 입력 (텍스트 또는 SRT)")
    
    # 입력창과 버튼을 옆으로 배치 (채팅 스타일)
    col1, col2 = st.columns([5, 1])
    
    with col1:
        korean_text = st.text_area(
            "한국어 자막 입력 (텍스트 또는 SRT)",
            placeholder="번역할 내용을 입력하세요...",
            height=130,
            label_visibility="collapsed"
        )
    
    with col2:
        # 버튼 유격을 맞추기 위해 약간의 여백 추가
        st.write("")
        st.write("")
        translate_btn = st.button("🔥번역", use_container_width=True)

    if translate_btn:
        if korean_text.strip():
            with st.spinner("유튜브 감성으로 번역 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": korean_text}
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
    st.write("### 이미지 속 한글 자막 번역")
    uploaded_file = st.file_uploader("한국어 텍스트가 포함된 이미지를 올려주세요 (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="업로드한 이미지", use_container_width=True)
        
        img_btn = st.button("🖼️ 이미지 텍스트 번역하기")
        if img_btn:
            with st.spinner("이미지 속 텍스트를 읽고 미국 감성으로 번역하는 중..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Extract all Korean text from this image and translate it into trendy American English for YouTube subtitles according to the guidelines."},
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