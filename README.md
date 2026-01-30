# Lyrics Slide Creator

Lyrics Slide Creator는 Melon.com에서 노래 가사를 검색하고, 편집하여 PowerPoint 프레젠테이션 슬라이드로 자동 생성해주는 Python 기반의 GUI 애플리케이션입니다. 교회, 학교, 행사 등에서 노래 가사를 효과적으로 전달해야 할 때 유용하게 활용할 수 있습니다.

## 주요 기능

*   **Melon.com 노래 검색**: 노래 제목 또는 가수 이름으로 Melon.com에서 노래를 검색하고 관련 정보를 가져옵니다.
*   **가사 및 앨범 아트 추출**: 선택한 노래의 가사와 앨범 아트를 자동으로 가져옵니다.
*   **가사 편집 및 분할**: 가져온 가사를 편리하게 편집할 수 있으며, 슬라이드별로 가사를 분할하는 기능을 제공합니다.
*   **PowerPoint 슬라이드 생성**: 사용자 정의 가능한 템플릿(`.pptx` 파일)을 기반으로, 편집된 가사를 적용한 PowerPoint 슬라이드를 생성합니다.
*   **Windows 실행 파일**: PyInstaller를 통해 Windows용 독립 실행형 `.exe` 파일로 빌드하여 편리하게 배포 및 실행할 수 있습니다.

## 기술 스택

*   **Python**: 핵심 프로그래밍 언어
*   **PyQt6**: 그래픽 사용자 인터페이스 (GUI)
*   **requests, beautifulsoup4**: 웹 스크래핑 (Melon.com)
*   **python-pptx**: PowerPoint 파일 생성 및 조작
*   **Pillow**: 이미지 처리
*   **PyInstaller**: 애플리케이션 패키징

## 설치 및 실행

### 1. 종속성 설치

프로젝트를 실행하려면 Python 3.x가 설치되어 있어야 합니다. 먼저 가상 환경을 설정하고 필요한 라이브러리를 설치합니다.

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 필수 라이브러리 설치
pip install -r requirements.txt
```

### 2. 애플리케이션 실행 (개발 모드)

가상 환경 활성화 후, 다음 명령어를 사용하여 개발 모드로 애플리케이션을 실행할 수 있습니다.

```bash
python run.py
```

### 3. Windows 실행 파일 빌드

PyInstaller를 사용하여 Windows용 독립 실행형 `.exe` 파일을 생성하려면 `build_windows.bat` 스크립트를 실행합니다.

```bash
build_windows.bat
```

빌드가 완료되면 `dist` 폴더 내에서 `LyricsSlideCreator.exe` 파일을 찾을 수 있습니다.

## 사용 방법

1.  **노래 검색**: 애플리케이션 실행 후 검색창에 노래 제목이나 가수를 입력하고 `검색` 버튼을 클릭합니다.
2.  **노래 선택**: 검색 결과 목록에서 원하는 노래를 클릭하여 가사 및 앨범 아트를 불러옵니다.
3.  **가사 편집**: 불러온 가사를 필요에 따라 편집합니다. 하단의 버튼을 통해 가사를 슬라이드별로 분할할 수 있습니다.
4.  **템플릿 선택**: `템플릿 변경` 버튼을 클릭하여 PowerPoint 템플릿(`.pptx` 파일)을 선택합니다. (기본 템플릿이 제공됩니다.)
5.  **PPT 생성**: `PPT 생성` 버튼을 클릭하여 최종 PowerPoint 파일을 저장합니다.

## 개발 컨벤션

*   **GUI**: PyQt6를 활용한 직관적인 사용자 인터페이스.
*   **비동기 처리**: 네트워크 요청과 같은 시간이 오래 걸리는 작업은 `QThread`를 사용하여 UI의 응답성을 유지합니다.
*   **리소스 관리**: PyInstaller 번들링 환경에서도 리소스 파일(예: `template.pptx`)을 올바르게 참조할 수 있도록 `resource_path` 유틸리티 함수를 사용합니다.
*   **스타일**: QSS를 통해 일관되고 현대적인 UI 스타일을 적용합니다.
