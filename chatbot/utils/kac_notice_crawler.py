import requests
import json
import logging

logger = logging.getLogger('chatbot')

class KACNoticeCrawler:
    def __init__(self):
        self.base_url = "https://www.airport.co.kr"
        self.api_url = "https://www.airport.co.kr/www/bbs/selectPageListBbs.do"
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def get_notices(self, category='notice', count=5):
        try:
            board_ids = {
                'notice': '1',
                'press': '41',
                'recruit': '603'
            }

            data = {
                'bbsId': board_ids.get(category, '1'),
                'pageUnit': str(count),
                'pageIndex': '1'
            }

            response = requests.post(self.api_url, headers=self.headers, data=data)
            
            logger.debug(f"API 요청 상태 코드: {response.status_code}")
            logger.debug(f"API 응답 내용: {response.text[:500]}")  # 응답 내용 일부 로그

            if response.status_code == 200:
                result = response.json()
                notices = []
                
                for item in result.get('resultList', []):
                    notice = {
                        'title': item.get('nttSj', ''),
                        'category': item.get('deptNm', ''),
                        'date': item.get('frstRegisterPnttm', '')[:10].replace('-', '.'),
                        'url': f"{self.base_url}/www/bbs/selectBbs.do?bbsId={data['bbsId']}&nttId={item.get('nttId', '')}"
                    }
                    notices.append(notice)
                
                return notices
            else:
                logger.error(f"API 요청 실패: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"데이터 가져오기 실패: {str(e)}")
            return []

    def get_all_categories(self):
        return {
            'notice': self.get_notices('notice'),
            'press': self.get_notices('press'),
            'recruit': self.get_notices('recruit')
        }