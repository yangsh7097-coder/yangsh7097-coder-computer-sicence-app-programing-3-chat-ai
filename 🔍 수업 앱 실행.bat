@echo off
chcp 65001 > nul
title 인구 집중 데이터 탐정 - 5학년 사회 수업

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   🔍 인구 집중 데이터 탐정 앱 실행 중...  ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  잠시 기다리면 브라우저가 자동으로 열립니다!
echo  앱을 종료하려면 이 창을 닫으세요.
echo.

"C:\Users\AORUS\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run "%~dp0ai_making_with_streamlit.py" --server.port 8501

pause
