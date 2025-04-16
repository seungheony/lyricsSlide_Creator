"""
가사로 PPT를 생성하는 모듈
"""

import os
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from typing import List, Dict, Tuple

class LyricsPPTCreator:
    """가사로 PPT를 생성하는 클래스"""
    
    def __init__(self, output_file: str = "lyrics_presentation.pptx"):
        self.output_file = output_file
        self.prs = Presentation()
        
        # 기본 PPT 설정
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(7.5)
        
        # 슬라이드 레이아웃 (첫 페이지, 가사 페이지)
        self.title_slide_layout = self.prs.slide_layouts[0]  # 제목 슬라이드
        self.content_slide_layout = self.prs.slide_layouts[5]  # 빈 슬라이드
    
    def create_title_slide(self, song_info: Dict) -> None:
        """
        제목 슬라이드를 생성합니다.
        
        Args:
            song_info: 노래 정보 (제목, 아티스트, 앨범)
        """
        slide = self.prs.slides.add_slide(self.title_slide_layout)
        
        # 제목 설정
        title = slide.shapes.title
        title.text = song_info.get('title', '제목 없음')
        title.text_frame.paragraphs[0].font.size = Pt(40)
        title.text_frame.paragraphs[0].font.bold = True
        
        # 부제목 설정 (아티스트 및 앨범)
        subtitle = slide.placeholders[1]
        subtitle.text = f"{song_info.get('artist', '아티스트 없음')} - {song_info.get('album', '앨범 없음')}"
        subtitle.text_frame.paragraphs[0].font.size = Pt(24)
    
    def create_lyrics_slide(self, lyrics_content: str) -> None:
        """
        가사 슬라이드를 생성합니다.
        
        Args:
            lyrics_content: 슬라이드에 표시할 가사 내용
        """
        slide = self.prs.slides.add_slide(self.content_slide_layout)
        
        # 가사 텍스트 상자 추가
        left = Inches(0.5)
        top = Inches(0.5)
        width = Inches(9)
        height = Inches(6.5)
        
        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.word_wrap = True
        
        # 가사 내용 설정
        p = text_frame.paragraphs[0]
        p.text = lyrics_content
        p.font.size = Pt(28)
        p.alignment = PP_ALIGN.CENTER
        
        # 줄 간격 설정
        p.line_spacing = 1.2
    
    def create_presentation(self, song_info: Dict, lyrics_pages: List[str]) -> str:
        """
        노래 정보와 가사로 프레젠테이션을 생성합니다.
        
        Args:
            song_info: 노래 정보 (제목, 아티스트, 앨범)
            lyrics_pages: 페이지별로 분할된 가사 목록
            
        Returns:
            생성된 PPT 파일 경로
        """
        # 제목 슬라이드 추가
        self.create_title_slide(song_info)
        
        # 가사 슬라이드 추가
        for page in lyrics_pages:
            self.create_lyrics_slide(page)
        
        # 파일 저장
        self.prs.save(self.output_file)
        return os.path.abspath(self.output_file)