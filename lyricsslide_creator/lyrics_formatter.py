"""
가사 텍스트를 PPT 페이지에 맞게 분할하는 모듈
"""

from typing import List, Dict

class LyricsFormatter:
    """가사를 PPT 페이지에 맞게 포맷팅하는 클래스"""
    
    def __init__(self, max_lines_per_slide: int = 10, max_chars_per_line: int = 35):
        self.max_lines_per_slide = max_lines_per_slide
        self.max_chars_per_line = max_chars_per_line
    
    def split_lyrics_into_pages(self, lyrics: str) -> List[str]:
        """
        가사를 PPT 페이지별로 분할합니다.
        
        Args:
            lyrics: 전체 가사 텍스트
            
        Returns:
            페이지별로 분할된 가사 목록
        """
        # 가사를 줄 단위로 분리
        lines = lyrics.strip().split('\n')
        
        # 긴 줄 분리 (최대 글자수 제한)
        processed_lines = []
        for line in lines:
            if len(line) > self.max_chars_per_line:
                # 긴 줄은 여러 줄로 나누기
                chunks = [line[i:i+self.max_chars_per_line] 
                          for i in range(0, len(line), self.max_chars_per_line)]
                processed_lines.extend(chunks)
            else:
                processed_lines.append(line)
        
        # 페이지별로 분할
        pages = []
        current_page = []
        current_line_count = 0
        
        for line in processed_lines:
            # 빈 줄도 카운트에 포함
            if current_line_count >= self.max_lines_per_slide:
                # 현재 페이지가 가득 차면 새 페이지 시작
                pages.append('\n'.join(current_page))
                current_page = []
                current_line_count = 0
            
            # 현재 페이지에 줄 추가
            current_page.append(line)
            current_line_count += 1
            
            # 빈 줄 다음에는 페이지 나누기 고려
            if line.strip() == '' and current_line_count > self.max_lines_per_slide / 2:
                pages.append('\n'.join(current_page))
                current_page = []
                current_line_count = 0
        
        # 마지막 페이지 추가
        if current_page:
            pages.append('\n'.join(current_page))
        
        return pages
    
    def format_lyrics_for_display(self, lyrics_pages: List[str]) -> List[Dict]:
        """
        페이지로 나뉜 가사를 표시용으로 포맷팅합니다.
        
        Args:
            lyrics_pages: 페이지별로 분할된 가사 목록
            
        Returns:
            페이지 정보 목록 (각 페이지의 텍스트와 메타데이터 포함)
        """
        formatted_pages = []
        
        for i, page_text in enumerate(lyrics_pages):
            page_info = {
                'page_number': i + 1,
                'content': page_text,
                'word_count': len(page_text.split()),
                'line_count': len(page_text.split('\n'))
            }
            formatted_pages.append(page_info)
        
        return formatted_pages