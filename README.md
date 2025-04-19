# lyricsSlide Creator 사용 설명서

PPT 파일을 변환하여 가사 슬라이드에 최적화된 프레젠테이션을 생성하는 도구입니다.

## 설치 방법

### 배포 버전 설치
1. 최신 릴리스에서 운영체제에 맞는 배포 파일을 다운로드하세요
   - Windows: `LyricsSlide_Creator_Setup.exe`
   - macOS: `LyricsSlide_Creator.dmg`

### 개발 버전 설치
```bash
git clone https://github.com/yourusername/lyricsSlide_Creator.git
cd lyricsSlide_Creator
pip install -e .
```

## 필수 외부 프로그램

1. **LibreOffice** (필수): PPT → PDF 변환에 사용
   - [다운로드 링크](https://www.libreoffice.org/download/)
   - Windows: 설치 후 기본 경로에 설치됨
   - macOS: LibreOffice.app에 설치

2. **Poppler** (필수): PDF → 이미지 변환에 사용
   - Windows: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) 다운로드 후 `C:\poppler`에 압축 해제 (참조 링크: https://blog.naver.com/chandong83/222262274082)
   - macOS: `brew install poppler`
   - Linux: `apt-get install poppler-utils`

## 주요 기능

### 1. 멜론 검색 가사 PPT 제작
- 멜론에서 노래 검색 후 가사를 추출하여 PPT 생성
- 여러 곡을 한 번에 검색하여 하나의 PPT로 생성 가능
- 가사 페이지 분할 방식 선택 가능 (2줄씩 자동 분할, 수동 분할)

### 2. 악보 포함 가사 PPT 제작
- 기존 PPT 파일을 변환하여 가사 슬라이드에 최적화된 형식으로 변환
- 악보 이미지가 검은 배경에 흰색 선으로 반전되어 표시
- 여러 PPT 파일을 하나로 병합 가능

## 폴더 구조

- **input_ppts**: 변환할 PPT 파일을 넣는 폴더
- **output_ppts**: 생성된 모든 PPT 파일이 저장되는 폴더

## 사용 방법

### 기본 사용법

1. 프로그램 실행
   - Windows: 설치된 바로가기 아이콘 또는 `lyrics_slide.exe` 실행
   - macOS: `LyricsSlide.app` 또는 터미널에서 `lyrics_slide` 실행
   - 개발 버전: `python run.py` 또는 `lyricsslide-creator` 명령어 실행

2. 메인 메뉴에서 원하는 기능 선택
   ```
   === lyricsSlide Creator ===
   1. 가사 PPT 제작 (멜론 검색)
   2. 악보 포함 가사 PPT 제작
   0. 종료
   ```

### 멜론 검색 가사 PPT 제작 (1번 기능)

1. 노래 제목 입력 (여러 곡은 쉼표로 구분)
   ```
   노래 제목을 입력하세요 (여러 곡을 검색하려면 쉼표로 구분):
   > 아무노래, 마음을 드려요
   ```

2. 검색 결과에서 원하는 곡 선택
   ```
   '아무노래'에 대한 검색 결과 (3개):
   1. 아무노래 - 지코 [ZZZ]
      아무 노래나 일단 틀어...
   2. 아무노래 - VANNER(배너) [컬러스 오브 바네르]
      I don't wanna smile...
   3. 아무노래나 - Ezi [아무노래나]
      오늘도 아침에 눈을 떠...
   
   사용할 노래 번호를 선택하세요 (0: 건너뛰기):
   > 1
   ```

3. 가사 확인 후 PPT 생성 여부 결정
   ```
   === 가사 미리보기 ===
   아무 노래나 일단 틀어
   너의 생각을 들려줘...
   
   이 노래의 가사로 PPT를 만드시겠습니까? (확인: 엔터, 이전으로: b):
   > [엔터]
   ```

4. 가사 페이지 분할 방식 선택
   ```
   분할 방식을 선택하세요:
   1. 자동 분할 (2줄씩)
   2. 자동 분할 후 특정 페이지 선택
   3. 수동 분할 (직접 줄 번호 지정)
   > 1
   ```

5. 생성된 PPT 파일은 output_ppts 폴더에 저장됨

### 악보 포함 가사 PPT 제작 (2번 기능)

1. input_ppts 폴더에 변환할 PPT 파일 넣기
   - 악보 PPT 파일 형식: .ppt 또는 .pptx

2. 변환 확인
   ```
   'input_ppts' 폴더에서 3개의 PPT 파일을 찾았습니다.
   모든 파일을 변환하려면 엔터키를 누르세요. (취소: n):
   > [엔터]
   ```

3. 각 파일이 변환되고 자동으로 병합됨
   ```
   '곡명1.ppt' 변환 중...
   변환 완료
   
   '곡명2.ppt' 변환 중...
   변환 완료
   
   3개의 파일을 하나의 PPT로 병합하는 중...
   병합된 프레젠테이션 저장 완료: output_ppts/병합된_가사_20250419_120030.pptx
   ```

4. 변환된 PPT 파일은 output_ppts 폴더에 저장됨

## 명령줄 옵션 (고급 사용법)

```bash
lyricsslide-creator [options]
```

- `-d, --directory`: 변환할 PPT 파일들이 있는 디렉토리 경로
- `-o, --output`: 생성될 프레젠테이션 파일 이름
- `-i, --images-dir`: 변환된 이미지 저장 디렉토리
- `--keep-images`: 임시 이미지 파일 유지
- `--dependency-check`: 종속성 확인 후 종료
- `--version`: 버전 정보 표시

## 자동 실행 스크립트

- Windows: run.bat 실행
- macOS: run.command 실행
- 기타 환경: `python run.py` 실행

## 문제 해결

### LibreOffice 관련 오류
- 오류: `LibreOffice가 설치되어 있지 않습니다`
- 해결: LibreOffice를 설치하고 시스템 재시작 후 다시 시도

### Poppler 관련 오류
- 오류: `Unable to get page count. Is poppler installed and in PATH?`
- 해결: Poppler를 설치하고 PATH 환경 변수에 추가

### 한글 파일명 오류
- 오류: 한글 파일명이 깨져서 처리 실패
- 해결: 영문 파일명 사용 또는 최신 버전으로 업데이트

## 개발 정보

- 버전: 0.1.0
- 필요 Python 버전: 3.7 이상
- 라이선스: MIT License

## 패키징

프로젝트를 실행 파일로 패키징하려면:
```bash
python package_app.py
```

## 라이선스

MIT License

Copyright (c) 2025 Kim Seung Heon