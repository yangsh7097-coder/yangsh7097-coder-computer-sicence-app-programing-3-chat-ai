import google.generativeai as genai
import os

try:
    genai.configure(api_key="AIzaSyAdyMt-yq1c1Hr_FGSzup96fuW46SnPQpI")

    print("--- 사용 가능한 모델 목록 ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
    print("--------------------------")

except Exception as e:
    print(f"오류가 발생했습니다: {e}")
    print("API 키가 정확한지, 인터넷 연결이 정상적인지 확인해주세요.")
