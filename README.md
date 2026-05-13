# 🕵️‍♀️ 6학년 데이터 탐정 AI 챗봇

본 프로젝트는 초등학교 6학년 정보-사회 융합 수업을 돕기 위해 제작된 AI 보조 교사 애플리케이션입니다.

## 🚀 주요 기능
- **개념 학습**: 디지털과 아날로그 데이터의 차이점 안내
- **알고리즘 검증**: 학생들이 만든 트리 알고리즘의 분류 기준(질문)에 대한 피드백 제공
- **사회 융합**: 데이터가 우리 사회(기업, 정부)에서 어떻게 유용하게 쓰이는지 탐구
- **학습 기록**: AI와의 대화 내용을 텍스트 파일로 저장 기능

## 🛠 설치 및 실행 방법
1. Python 설치
2. 필수 라이브러리 설치: `pip install -r requirements.txt`
3. `.streamlit/secrets.toml` 파일에 Google Gemini API 키 설정
4. 실행: `streamlit run ai_making_with_streamlit.py`

## 📂 파일 구조
- `ai_making_with_streamlit.py`: 메인 애플리케이션 코드
- `style.css`: 웹 UI 스타일 시트
- `lesson_plan.pdf`: 수업 지도안 (다운로드용)