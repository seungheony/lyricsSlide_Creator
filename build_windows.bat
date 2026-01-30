@echo off
echo [1/3] 가상환경 생성 중...
python -m venv venv
call venv\Scripts\activate

echo [2/3] 필수 라이브러리 설치 중...
pip install -r requirements.txt

echo [3/3] 실행 파일(.exe) 생성 중...
pyinstaller --noconfirm --clean --onefile --windowed --name "LyricsSlideCreator" --add-data "template.pptx;." run.py

echo.
echo ==========================================
echo 빌드 완료! dist 폴더를 확인하세요.
echo ==========================================
pause