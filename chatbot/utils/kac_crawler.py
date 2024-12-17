import requests
import json
from datetime import datetime

class KACCrawler:
    def __init__(self):
        self.base_url = "https://www.airport.co.kr"
        self.api_url = "https://www.airport.co.kr/www/cms/getContents.do"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.airport.co.kr',
            'Referer': 'https://www.airport.co.kr/www/cms/menu/1419.do',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session = requests.Session()

    def get_notices(self, category='notice', page=1, count=5):
        try:
            # 카테고리별 설정
            category_params = {
                'notice': {'id': 'C1419', 'seq': '1', 'subSeq': '1'},
                'press': {'id': 'C1419', 'seq': '1', 'subSeq': '2'},
                'recruit': {'id': 'C1419', 'seq': '1', 'subSeq': '3'}
            }
            
            params = category_params.get(category, category_params['notice'])
            
            data = {
                'configId': params['id'],
                'configSeq': params['seq'],
                'subSeq': params['subSeq'],
                'pageIndex': str(page),
                'pageUnit': str(count),
                'searchCondition': '',
                'searchKeyword': ''
            }

            response = self.session.post(
                self.api_url,
                headers=self.headers,
                data=data,
                verify=False
            )

            if response.status_code != 200:
                print(f"API 요청 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return []

            try:
                result = response.json()
                notices = []
                
                # 응답 구조 확인을 위한 디버깅
                print("API 응답:", json.dumps(result, indent=2, ensure_ascii=False))
                
                for item in result.get('resultList', []):
                    notice = {
                        'category': item.get('deptNm', ''),
                        'date': item.get('frstRegisterPnttm', '')[:10].replace('-', '.'),
                        'title': item.get('nttSj', ''),
                        'link': f"{self.base_url}/www/bbs/selectBbs.do?configId={params['id']}&nttId={item.get('nttId', '')}"
                    }
                    notices.append(notice)
                
                return notices

            except json.JSONDecodeError as e:
                print(f"JSON 파싱 실패: {str(e)}")
                print(f"응답 내용: {response.text}")
                return []

        except Exception as e:
            print(f"크롤링 중 오류 발생: {str(e)}")
            return []

    def get_all_categories(self):
        result = {
            'notice': self.get_notices('notice'),
            'press': self.get_notices('press'),
            'recruit': self.get_notices('recruit')
        }
        return result

# 테스트 코드
if __name__ == "__main__":
    crawler = KACCrawler()
    notices = crawler.get_notices('notice')
    print("\n크롤링 결과:")
    for notice in notices:
        print(f"\n제목: {notice['title']}")
        print(f"날짜: {notice['date']}")
        print(f"카테고리: {notice['category']}")
        print(f"링크: {notice['link']}") 