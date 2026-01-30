import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

class MelonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.melon.com/index.htm'
        }

    def search_song(self, keyword):
        if not keyword: return []
        try:
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://www.melon.com/search/song/index.htm?q={encoded_keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code != 200: return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            rows = soup.select('table > tbody > tr')
            
            for row in rows:
                try:
                    song_link = row.select_one('a[href*="goSongDetail"]')
                    if not song_link: continue
                    
                    song_id_match = re.search(r"goSongDetail\('(\d+)'\)", song_link['href'])
                    song_id = song_id_match.group(1) if song_id_match else ""
                    title = song_link.get_text(strip=True).replace("상세정보 페이지 이동", "").strip()
                    
                    artist_div = row.select_one('#artistName')
                    artist = artist_div.get_text(strip=True) if artist_div else "아티스트 미상"
                    # 중복 아티스트명 제거 (예: "아티스트아티스트" -> "아티스트")
                    if artist and len(artist) > 0 and len(artist) % 2 == 0:
                        half = len(artist) // 2
                        if artist[:half] == artist[half:]:
                            artist = artist[:half]
                    
                    album_link = row.select_one('a[href*="goAlbumDetail"]')
                    album = album_link.get_text(strip=True) if album_link else "앨범 미상"

                    if song_id:
                        results.append({'song_id': song_id, 'title': title, 'artist': artist, 'album': album})
                except: continue
            return results[:10]
        except: return []

    def get_song_detail(self, song_id):
        if not song_id: return None
        try:
            url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            lyrics_div = soup.select_one('div.lyric')
            lyrics = ""
            if lyrics_div:
                for br in lyrics_div.find_all("br"): br.replace_with("\n")
                lyrics = lyrics_div.get_text().strip()
            
            img_tag = soup.select_one('.thumb img')
            image_url = img_tag['src'] if img_tag else ""
            
            return {'song_id': song_id, 'lyrics': lyrics, 'image_url': image_url}
        except: return None

    def get_album_image_url(self, song_id):
        """곡 상세 페이지에서 앨범아트 URL만 가져온다."""
        if not song_id: return ''
        try:
            url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tag = soup.select_one('.thumb img')
            return img_tag['src'] if img_tag else ''
        except:
            return ''
