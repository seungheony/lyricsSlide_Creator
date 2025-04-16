"""
멜론 사이트에서 가사를 검색하고 추출하는 모듈
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
from typing import List, Dict, Tuple, Optional

class MelonScraper:
    """멜론 사이트에서 가사 정보를 가져오는 클래스"""
    
    def __init__(self):
        self.search_url = "https://www.melon.com/search/song/index.htm"
        self.song_url = "https://www.melon.com/song/detail.htm"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    
    def search_songs(self, query: str) -> List[Dict]:
        """
        노래 제목으로 검색하여 결과 목록을 반환합니다.
        
        Args:
            query: 검색할 노래 제목
            
        Returns:
            검색 결과 목록 (제목, 아티스트, 앨범, 가사 첫줄, 노래 ID 포함)
        """
        params = {
            "q": query,
            "section": "song"
        }
        
        try:
            response = requests.get(self.search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # 인코딩 명시
            if sys.platform.startswith('win'):
                response.encoding = 'utf-8'
                
            soup = BeautifulSoup(response.text, 'html.parser')
            song_results = []
            
            # 검색 결과 목록 찾기
            song_list = soup.select('#frm_defaultList > div > table > tbody > tr')
            
            for song in song_list:
                try:
                    # 노래 ID 추출
                    song_id = song.select_one('td:nth-child(1) input')['value']
                    
                    # 제목 추출
                    title_elem = song.select_one('td:nth-child(3) a.fc_gray')
                    title = title_elem.text.strip() if title_elem else "제목 없음"
                    
                    # 아티스트 추출
                    artist_elem = song.select_one('td:nth-child(4) span a')
                    artist = artist_elem.text.strip() if artist_elem else "아티스트 없음"
                    
                    # 앨범 추출
                    album_elem = song.select_one('td:nth-child(5) a')
                    album = album_elem.text.strip() if album_elem else "앨범 없음"
                    
                    # 결과 추가
                    song_results.append({
                        'id': song_id,
                        'title': title,
                        'artist': artist,
                        'album': album,
                        'preview': "가사 미리보기..."  # 상세 페이지에서 가져올 예정
                    })
                    
                except (AttributeError, KeyError) as e:
                    print(f"노래 정보 추출 중 오류: {e}")
                    continue
            
            # 추가 정보 가져오기 (가사 첫 줄)
            for song in song_results:
                try:
                    # 가사 첫 줄 가져오기
                    preview = self.get_lyrics_preview(song['id'])
                    if preview:
                        song['preview'] = preview
                except Exception as e:
                    print(f"가사 미리보기 가져오기 오류: {e}")
            
            return song_results
            
        except requests.RequestException as e:
            print(f"검색 요청 중 오류 발생: {e}")
            return []
    
    def get_lyrics_preview(self, song_id: str) -> str:
        """
        노래 ID로 가사 첫 줄을 가져옵니다.
        
        Args:
            song_id: 노래 ID
            
        Returns:
            가사 첫 줄 (없으면 빈 문자열)
        """
        params = {
            "songId": song_id
        }
        
        try:
            # 너무 빠른 요청은 차단될 수 있으므로 약간의 지연 추가
            time.sleep(0.5)
            
            response = requests.get(self.song_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # 인코딩 명시
            if sys.platform.startswith('win'):
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 가사 미리보기 찾기 (첫 줄만)
            lyrics_div = soup.select_one('div.lyric')
            if lyrics_div:
                # HTML 태그 제거하고 첫 줄만 반환
                lyrics_text = lyrics_div.get_text(strip=True)
                first_line = lyrics_text.split('\n')[0] if '\n' in lyrics_text else lyrics_text[:30]
                return first_line + "..."
            
            return "가사 없음"
            
        except requests.RequestException as e:
            print(f"가사 미리보기 요청 중 오류 발생: {e}")
            return "가사 로딩 실패"
    
    def get_full_lyrics(self, song_id: str) -> Tuple[Dict, str]:
        """
        노래 ID로 전체 가사와 노래 정보를 가져옵니다.
        
        Args:
            song_id: 노래 ID
            
        Returns:
            (노래 정보 딕셔너리, 전체 가사)
        """
        params = {
            "songId": song_id
        }
        
        try:
            response = requests.get(self.song_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # 인코딩 명시
            if sys.platform.startswith('win'):
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 노래 정보 추출
            title = soup.select_one('div.song_name').text.replace('곡명', '').strip()
            artist = soup.select_one('div.artist').text.strip()
            album = soup.select_one('div.meta > dl > dd:nth-child(2)').text.strip()
            
            # 가사 전체 추출
            lyrics_div = soup.select_one('div.lyric')
            if not lyrics_div:
                return {'title': title, 'artist': artist, 'album': album}, "가사를 찾을 수 없습니다."
                
            # HTML 태그 처리 및 줄바꿈 유지
            lyrics_text = lyrics_div.get_text('\n', strip=True)
            
            # 불필요한 공백 제거
            lyrics_text = re.sub(r'\n\s+', '\n', lyrics_text)
            lyrics_text = re.sub(r'\n{3,}', '\n\n', lyrics_text)
            
            return {'title': title, 'artist': artist, 'album': album}, lyrics_text
            
        except requests.RequestException as e:
            print(f"전체 가사 요청 중 오류 발생: {e}")
            return {}, "가사를 가져오는 중 오류가 발생했습니다."