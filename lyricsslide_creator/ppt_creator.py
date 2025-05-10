"""
가사로 PPT를 생성하는 모듈
"""

import os
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from typing import List, Dict

class LyricsPPTCreator:
    """가사 슬라이드 PPT를 생성하는 클래스"""
    
    def __init__(self, output_file: str = None):
        self.output_file = output_file
        # 새 프레젠테이션 생성 (16:9 비율 설정)
        self.prs = Presentation()
        
        # 16:9 비율로 슬라이드 크기 설정 (가로:세로 = 16:9)
        self.prs.slide_width = Inches(16)
        self.prs.slide_height = Inches(9)
        
        # 모든 텍스트 폰트 크기를 42pt로 통일
        self.title_font_size = Pt(42)
        self.body_font_size = Pt(42)
        self.font_name = "맑은 고딕"
        
    def create_title_slide(self, title: str, artist: str = None):
        """
        제목 슬라이드를 생성합니다. (검은색 배경, 중앙에 제목만)
        
        Args:
            title: 노래 제목
            artist: 아티스트 이름 (사용하지 않음)
        """
        # 빈 레이아웃 선택 (제목 없는 빈 슬라이드)
        slide_layout = self.prs.slide_layouts[5]
        slide = self.prs.slides.add_slide(slide_layout)
        
        # 배경을 검은색으로 설정
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색 (RGB: 0, 0, 0)
        
        # 텍스트 상자 추가 (중앙에 제목만)
        left = Inches(1)
        top = Inches(3)  # 중앙에 가깝게 위치
        width = Inches(14)
        height = Inches(3)
        
        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.word_wrap = True
        
        # 제목 텍스트 추가
        p = text_frame.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.CENTER
        
        # 제목 텍스트 서식 설정
        font = p.font
        font.name = self.font_name
        font.size = self.title_font_size
        font.bold = True
        font.color.rgb = RGBColor(255, 255, 255)  # 흰색
        
        return slide
        
    def create_slide(self, title=None, content=None):
        """
        슬라이드를 생성합니다.
        
        Args:
            title: 슬라이드 제목 (기본값: None)
            content: 슬라이드 내용 (기본값: None)
        """
        # 빈 슬라이드 추가
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # 빈 레이아웃
        
        # 배경을 검은색으로 설정
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
        
        # 텍스트 박스 위치 조정 - 상단 중앙으로 이동
        left = Inches(1.0)
        top = Inches(1.0)  # 상단으로 위치 이동
        width = Inches(14.0)
        height = Inches(7.0)
        
        # 텍스트 상자 추가
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP  # 상단 위치로 조정
        
        # 제목 텍스트 추가
        if title:
            p = tf.add_paragraph()
            p.text = title
            p.font.size = self.title_font_size
            p.font.name = self.font_name
            p.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
            p.font.bold = True
            p.alignment = PP_ALIGN.CENTER
            
        # 내용 텍스트 추가
        if content:
            if title:  # 제목이 있으면 공백 추가
                p = tf.add_paragraph()
                p.text = ""
            
            p = tf.add_paragraph()
            p.text = content
            p.font.size = self.body_font_size
            p.font.name = self.font_name
            p.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
            p.alignment = PP_ALIGN.CENTER
        
        return slide
    
    def add_song_to_presentation(self, song_info: Dict, lyrics_pages: List[str]):
        """
        하나의 노래 가사를 현재 프레젠테이션에 추가합니다.
        
        Args:
            song_info: 노래 정보 (제목, 아티스트, 앨범)
            lyrics_pages: 페이지별로 분할된 가사 목록
        """
        # 제목 슬라이드 추가
        title = song_info.get("title", "제목 없음")
        artist = song_info.get("artist", "아티스트 없음")
        self.create_title_slide(title, artist)
        
        # 가사 슬라이드 추가
        for lyrics_page in lyrics_pages:
            self.create_slide(content=lyrics_page)
            
    def save_presentation(self, output_file: str = None):
        """
        프레젠테이션을 저장합니다.
        
        Args:
            output_file: 저장할 파일 경로 (기본값: self.output_file)
            
        Returns:
            저장된 PPT 파일의 경로
        """
        # 출력 파일 경로 설정
        save_path = output_file if output_file else self.output_file
        
        # 출력 파일 경로가 없으면 기본 이름 사용
        if not save_path:
            save_path = "가사모음.pptx"
        
        # 절대 경로 생성
        output_path = os.path.abspath(save_path)
        
        # 프레젠테이션 저장
        self.prs.save(output_path)
        
        return output_path
        
    def create_presentation(self, song_info: Dict, lyrics_pages: List[str]) -> str:
        """
        가사 PPT 프레젠테이션을 생성합니다. (단일 노래용)
        
        Args:
            song_info: 노래 정보 (제목, 아티스트, 앨범)
            lyrics_pages: 페이지별로 분할된 가사 목록
            
        Returns:
            생성된 PPT 파일의 경로
        """
        # 노래 추가
        self.add_song_to_presentation(song_info, lyrics_pages)
        
        # 저장
        return self.save_presentation(self.output_file)