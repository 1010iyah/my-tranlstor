import streamlit as st
from openai import OpenAI

# 1. 화면 제목 설정
st.set_page_config(page_title="유튜브 자막 번역기", page_icon="🎬")
st.title("🎬 유튜브 감성 자막 번역기")
st.write("한국어 밈과 구어체를 미국 유튜버 스타일 영어로 바꿔줍니다.")

# 2. 왼쪽 사이드바에서 API 키 입력받기
api_key = st.sidebar.text_input("OpenAI API Key 입력", type="password")

# 3. 자막 입력창
korean_text = st.text_area("한국어 자막 입력 (텍스트 또는 SRT)", height=150, 
                           placeholder="예: 억까 지리네 진짜... 오늘 착장 완전 레전드임 ㅋㅋㅋ")

# 4. AI 번역 규칙 (유튜브 스타일 지시문)
SYSTEM_PROMPT = """
You are an expert translator specializing in converting Korean YouTube subtitles into natural, trendy, and casual American English used by modern creators and SNS.
Translate Korean slangs, idioms, and YouTube culture naturally into American slang/casual speech.
Do not translate literally. Keep timestamps intact if SRT format is provided.
"""

# 5. 번역 버튼 동작
if st.button("🔥 유튜브 스타일로 번역하기"):
    if not api_key:
        st.error("왼쪽 사이드바에 OpenAI API 키를 입력해주세요!")
    elif not korean_text.strip():
        st.warning("번역할 글자를 입력해주세요!")
    else:
        try:
            client = OpenAI(api_key=api_key)
            with st.spinner("미국 유튜버 느낌으로 변환 중..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": korean_text}
                    ]
                )
                result = response.choices[0].message.content
                st.success("번역 완료!")
                st.text_area("번역된 영어 자막", value=result, height=150)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")