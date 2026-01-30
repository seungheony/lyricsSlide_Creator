# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

LyricsSlideCreator는 멜론(Melon.com)에서 노래를 검색하여 가사와 앨범아트를 가져오고, 템플릿 기반으로 PowerPoint 프레젠테이션을 생성하는 PyQt6 GUI 애플리케이션이다. UI 라벨과 코드 주석은 한국어로 작성되어 있다.

## 실행 방법

```bash
# 의존성 설치 (venv 사용 권장)
pip install -r requirements.txt

# 개발 모드 실행
python run.py
```

## 빌드

```bash
# Windows
build_windows.bat

# 수동 빌드 (모든 OS)
pyinstaller --noconfirm --clean --onefile --windowed \
  --name "LyricsSlideCreator" --add-data "template.pptx:." run.py
```

## 아키텍처

**진입점**: `run.py` — 전역 예외 핸들러 설정, `src/`를 `sys.path`에 추가, PyQt6 앱 실행. `src/main.py`는 PyInstaller용 진입점.

**UI 레이어** (`src/ui/`):
- `main_window.py` — QMainWindow에 두 페이지 QStackedWidget(검색 페이지 → 편집 페이지) 구성. 모든 네트워크 I/O는 QThread 서브클래스(`SearchThread`, `DetailThread`, `ImageLoaderThread`)로 비동기 처리. 스레드 객체는 `_threads` 리스트에 저장하여 GC 방지.
- `style.py` — QSS 스타일시트. 초록색(#00CD3C) 강조색, 한국어 폰트 지원(Apple SD Gothic Neo / Malgun Gothic).

**백엔드** (`src/utils/`):
- `melon_api.py` — `MelonScraper` 클래스가 멜론에서 노래 검색 결과와 가사/앨범아트를 스크래핑. BeautifulSoup + 정규식 사용. 멜론 HTML 구조 변경 시 깨질 수 있음.
- `ppt_engine.py` — `PPTBuilder` 클래스가 템플릿 PPTX를 로드하고, 슬라이드 구조를 딥카피하여 서식 유지, "가사" 플레이스홀더 텍스트를 교체, `BytesIO`로 메모리 내 슬라이드 생성.
- `helpers.py` — `resource_path()` 함수가 개발 환경과 PyInstaller(`sys._MEIPASS`) 환경 모두에서 파일 경로를 해석.

**주요 패턴**:
- `__init__.py` 파일 없음. `sys.path` 주입으로 모듈 탐색
- 프로젝트 루트의 `template.pptx`가 필수이며 실행 파일에 번들됨
- 메모리 내 PPT 생성(BytesIO), 임시 파일 미사용
- 자동화된 테스트 스위트 없음
