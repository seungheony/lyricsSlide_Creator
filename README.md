# lyricsSlide Creator

PPT 파일을 변환하여 가사 슬라이드에 최적화된 프레젠테이션을 생성하는 도구입니다.

## 설치

```bash
pip install lyricsslide-creator
```

## 사용 요구사항

1. **Python 3.7 이상**
2. **LibreOffice** (PPT -> PDF 변환용): [다운로드 링크](https://www.libreoffice.org/download/download/)
3. **Poppler**
   - Windows: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)
   - macOS: `brew install poppler`
   - Linux: `apt-get install poppler-utils` 또는 `yum install poppler-utils`

## 기본 사용법

```bash
lyricsslide-creator
```

프롬프트가 나타나면 변환할 PPT 파일들이 있는 디렉토리 경로를 입력합니다.

## 고급 사용법

```bash
lyricsslide-creator -d "변환할_PPT_폴더" -o "결과파일.pptx" --keep-images
```

### 명령줄 옵션

- `-d, --directory`: 변환할 PPT 파일들이 있는 디렉토리 경로
- `-o, --output`: 생성될 프레젠테이션 파일 이름 (기본값: merged_presentation.pptx)
- `-i, --images-dir`: 변환된 이미지가 저장될 디렉토리 (기본값: converted_images)
- `--keep-images`: 처리 후 변환된 이미지 파일 유지
- `--dependency-check`: 필요한 종속성을 확인하고 종료
- `--version`: 버전 정보 표시

## 종속성 확인

패키지 실행 전 필요한 종속성을 확인하려면:

```bash
lyricsslide-creator --dependency-check
```

## 라이선스

MIT License