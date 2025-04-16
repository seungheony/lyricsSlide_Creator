import sys
import subprocess
import os
import platform

def ensure_setuptools():
    """setuptools가 설치되어 있는지 확인하고, 없으면 설치합니다."""
    try:
        import setuptools
        return True
    except ImportError:
        print("setuptools가 설치되어 있지 않습니다. 설치를 시도합니다...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "setuptools"])
            import setuptools  # 다시 import 시도
            print("setuptools가 성공적으로 설치되었습니다.")
            return True
        except Exception as e:
            print(f"setuptools 설치 중 오류 발생: {e}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
                import setuptools  # 다시 import 시도
                print("setuptools가 성공적으로 설치되었습니다.")
                return True
            except Exception as e:
                print(f"setuptools 설치 중 오류 발생: {e}")
                print("수동으로 설치하세요: pip install setuptools")
                return False

# setuptools 설치 확인 및 필요시 설치
if not ensure_setuptools():
    sys.exit(1)

# 이제 setuptools import 가능
from setuptools import setup, find_packages

# requirements.txt 파일에서 의존성 읽기
def get_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('//')]
    
    # 기본 종속성
    install_requires = [
        "python-pptx",
        "Pillow",
        "pdf2image",
    ]
    
    # Windows 전용 종속성
    if platform.system() == 'Windows':
        install_requires.append("comtypes")
        
    return install_requires

# README.md 파일 확인
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()
    long_description_content_type = "text/markdown"
else:
    long_description = "PPT 파일을 변환하여 가사 슬라이드에 최적화된 프레젠테이션을 생성하는 도구"
    long_description_content_type = "text/plain"

setup(
    name="lyricsslide-creator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'lyricsslide-creator=lyricsslide_creator.main:cli_entry_point',
        ],
    },
    author="Kim Seung Heon",
    author_email="your.email@example.com",
    description="PPT 파일을 변환하여 가사 슬라이드에 최적화된 프레젠테이션을 생성하는 도구",
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    url="https://github.com/yourusername/lyricsSlide_Creator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    keywords=["lyrics", "presentation", "ppt", "powerpoint", "slide"],
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/lyricsSlide_Creator/issues",
        "Documentation": "https://github.com/yourusername/lyricsSlide_Creator#readme",
        "Source Code": "https://github.com/yourusername/lyricsSlide_Creator",
    },
)