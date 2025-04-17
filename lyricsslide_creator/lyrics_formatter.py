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
    
    def split_lyrics_with_user_input(self, lyrics: str) -> List[str]:
        """
        사용자 입력에 따라 가사를 PPT 페이지별로 분할합니다.
        
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
        print("\n=== 가사 페이지 분할 ===")
        print("다음 가사를 페이지별로 나눕니다. 각 줄 번호를 확인하세요.")
        
        # 모든 줄 표시
        for i, line in enumerate(processed_lines):
            print(f"{i+1:3d}: {line}")
        
        pages = []
        current_line_index = 0
        
        while current_line_index < len(processed_lines):
            print(f"\n현재 {current_line_index+1}번 줄부터 시작합니다.")
            print("이 페이지에 포함할 마지막 줄 번호를 입력하세요 (자동으로 나누려면 A 입력):")
            
            user_input = input("> ").strip()
            
            # 자동 모드
            if user_input.upper() == 'A':
                # 자동으로 페이지 나누기 계산
                max_lines = min(current_line_index + self.max_lines_per_slide, len(processed_lines))
                end_line_index = max_lines
            else:
                try:
                    # 사용자가 입력한 줄 번호 (1부터 시작)
                    end_line_index = int(user_input)
                    
                    # 유효성 검사
                    if end_line_index < current_line_index + 1:
                        print("현재 줄보다 앞선 줄 번호는 입력할 수 없습니다.")
                        continue
                    if end_line_index > len(processed_lines):
                        print(f"유효한 줄 번호를 입력하세요 (최대: {len(processed_lines)}).")
                        continue
                        
                    # 인덱스는 0부터 시작하므로 1 감소
                    end_line_index = end_line_index
                except ValueError:
                    print("유효한 숫자나 'A'를 입력하세요.")
                    continue
            
            # 현재 페이지 생성
            current_page_lines = processed_lines[current_line_index:end_line_index]
            current_page = '\n'.join(current_page_lines)
            pages.append(current_page)
            
            # 미리보기 표시
            print("\n--- 이 페이지 미리보기 ---")
            print(current_page)
            print("-------------------------")
            
            # 다음 페이지 준비
            current_line_index = end_line_index
            
            if current_line_index >= len(processed_lines):
                print("\n모든 가사가 페이지로 분할되었습니다.")
                break
        
        print(f"\n총 {len(pages)}개의 페이지로 분할되었습니다.")
        return pages
    
    def split_lyrics_with_interactive_selection(self, lyrics: str) -> List[str]:
        """
        가사를 줄 단위로 조정하여 특정 줄을 독립 페이지로 설정할 수 있는 기능
        
        Args:
            lyrics: 전체 가사 텍스트
            
        Returns:
            사용자 조정이 반영된 페이지별 가사 목록
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
        
        # 초기 상태: 2줄씩 자동 분할된 페이지 보여주기
        auto_pages = []
        page_to_line_mapping = {}  # 페이지 번호와 줄 번호 매핑을 저장
        
        for i in range(0, len(processed_lines), 2):
            page_idx = len(auto_pages)  # 현재 페이지 인덱스
            line_indices = []  # 현재 페이지에 포함된 줄 번호들
            
            if i + 1 < len(processed_lines):
                auto_pages.append(f"{processed_lines[i]}\n{processed_lines[i+1]}")
                line_indices = [i+1, i+2]  # 1부터 시작하는 줄 번호
            else:
                auto_pages.append(processed_lines[i])
                line_indices = [i+1]
            
            page_to_line_mapping[page_idx+1] = line_indices  # 페이지 번호는 1부터 시작
        
        # 페이지별 분할 위치를 저장할 리스트
        # True는 해당 줄을 독립 페이지로 설정함을 의미
        line_breaks = [False] * len(processed_lines)
        
        # 선택한 첫 번째 줄 번호 저장 (기본값: 모든 줄 표시)
        first_selected_line = 1  # 처음에는 1번줄부터 표시
        
        # 선택 기록 저장 (이전으로 돌아갈 때 사용)
        selection_history = []
        
        while True:
            print("\n=== 페이지 조정 ===")
            # 각 페이지의 줄 번호 정보와 함께 가사 미리보기도 표시
            print("페이지 목록 및 포함된 줄:")
            
            # 현재 페이지 구성으로 미리보기 생성
            current_pages = self._create_pages_from_line_breaks(processed_lines, line_breaks)
            
            # 현재 페이지 매핑 계산
            current_page_mapping = {}
            line_idx = 0
            for page_idx, page in enumerate(current_pages):
                lines_in_page = page.count('\n') + 1
                line_nums = list(range(line_idx + 1, line_idx + lines_in_page + 1))
                current_page_mapping[page_idx + 1] = line_nums
                line_idx += lines_in_page
            
            # 각 페이지와 가사 내용 표시 (선택한 줄 이상만 표시)
            for page_num, line_nums in current_page_mapping.items():
                # 페이지의 줄 중 하나라도 선택한 첫 번째 줄보다 크거나 같으면 표시
                if any(line_num >= first_selected_line for line_num in line_nums):
                    print(f"\n[{page_num} 페이지]")
                    
                    # 해당 페이지의 가사 줄 추출
                    page_content = current_pages[page_num-1].split('\n')
                    
                    # 각 줄에 줄 번호 붙여서 표시 (선택한 줄 이상만)
                    for i, (line_num, content) in enumerate(zip(line_nums, page_content)):
                        if line_num >= first_selected_line:
                            print(f"{line_num}: {content}")
                            
            print("\n독립 페이지로 설정할 줄 번호를 입력하세요 (1-{})".format(len(processed_lines)))
            print("완료: 엔터, 취소: c, 이전으로: b")  # q 제거, c만 남김
            
            selection = input("> ").strip().lower()
            
            if selection == '':  # 엔터만 누르면 완료
                break
            elif selection == 'c':  # c 입력 시 취소 (q/c 대신 c만)
                print("기본 분할을 유지합니다.")
                return auto_pages
            elif selection == 'b':  # 이전으로 돌아가기
                if selection_history:
                    # 이전에 설정한 마지막 줄 되돌리기
                    last_line = selection_history.pop()
                    line_breaks[last_line - 1] = False
                    
                    # 이전 선택한 줄로 first_selected_line 업데이트
                    if selection_history:
                        first_selected_line = selection_history[-1]
                    else:
                        first_selected_line = 1  # 모든 선택을 취소하면 다시 처음부터 표시
                        
                    print(f"이전 단계로 돌아갔습니다. 줄 {last_line}의 독립 페이지 설정이 취소되었습니다.")
                    continue
                else:
                    print("더 이상 이전 단계가 없습니다.")
                    continue
            
            try:
                line_num = int(selection)
                if 1 <= line_num <= len(processed_lines):
                    # 이미 설정된 줄인지 확인
                    if line_breaks[line_num - 1]:
                        print(f"줄 {line_num}은(는) 이미 독립 페이지로 설정되어 있습니다.")
                        continue
                    
                    # 선택한 줄을 독립 페이지로 설정 (인덱스는 0부터 시작)
                    line_breaks[line_num - 1] = True
                    print(f"줄 {line_num}이(가) 독립 페이지로 설정되었습니다.")
                    
                    # 선택 기록에 추가
                    selection_history.append(line_num)
                    
                    # 다음에는 선택한 줄부터 표시
                    first_selected_line = line_num
                else:
                    print(f"유효한 줄 번호를 입력하세요 (1-{len(processed_lines)}).")
            except ValueError:
                print("유효한 줄 번호나 명령어(엔터, q, c, b)를 입력하세요.")
        
        # 최종 페이지 생성
        result_pages = self._create_pages_from_line_breaks(processed_lines, line_breaks)
        print(f"\n총 {len(result_pages)}개의 페이지가 생성되었습니다.")
        return result_pages

    def _create_pages_from_line_breaks(self, lines: List[str], line_breaks: List[bool]) -> List[str]:
        """
        줄 단위 분할 정보를 기반으로 페이지 목록 생성
        
        Args:
            lines: 모든 가사 줄 목록
            line_breaks: 각 줄이 독립 페이지인지를 나타내는 불리언 목록
            
        Returns:
            생성된 페이지 목록
        """
        result_pages = []
        current_page = []
        
        for i, line in enumerate(lines):
            if line_breaks[i]:
                # 현재까지 모은 줄이 있으면 페이지로 추가
                if current_page:
                    result_pages.append('\n'.join(current_page))
                    current_page = []
                
                # 독립 페이지로 설정된 줄
                result_pages.append(line)
            else:
                current_page.append(line)
                
                # 2줄마다 페이지 나누기 (독립 페이지가 아닌 경우)
                if len(current_page) == 2:
                    result_pages.append('\n'.join(current_page))
                    current_page = []
        
        # 남은 줄이 있으면 마지막 페이지로 추가
        if current_page:
            result_pages.append('\n'.join(current_page))
        
        return result_pages
    
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