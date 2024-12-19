from django.shortcuts import render
from .vector_db import get_vector_db, get_template
from django.views.decorators.http import require_http_methods
import json
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from django.http import JsonResponse
import requests
import feedparser
from datetime import datetime
from .kac_crawler import KACCrawler



# Create your views here.
vector_retriever = None

def initialize_vector_db():
    """벡터 DB 초기화 함수"""
    global vector_retriever
    if vector_retriever is None:
        try:
            print("벡터 DB 초기화 시작...")
            vector_retriever = get_vector_db()
            print("벡터 DB 초기화 완료")
        except Exception as e:
            print(f"벡터 DB 초기화 실패: {str(e)}")
            raise

@require_http_methods(["GET", "POST"])
def chat_view(request):
    if request.method == "GET":
        return render(request, 'chatbot/chat.html')
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # 벡터 DB 검색
            retriever = get_vector_db()
            template = get_template()
            prompt = ChatPromptTemplate.from_template(template)
            
            # ChatOpenAI 모델 설정 - fine-tuned 모델 사용
            model = ChatOpenAI(
                model_name="ft:gpt-4o-mini-2024-07-18:personal::AXmDF5MY",  # fine-tuned 모델 ID
                temperature=0.7,
                max_tokens=1000,
                openai_api_key=os.getenv('OPENAI_API_KEY')
            )

            # 문서 포맷팅
            def format_docs(docs):
                return '\n\n'.join([d.page_content for d in docs])

            # 체인 구성
            chain = {
                'context': retriever | format_docs,
                'question': RunnablePassthrough()
            } | prompt | model | StrOutputParser()

            # 응답 생성
            response = chain.invoke(user_message)

            return JsonResponse({
                'status': 'success',
                'response': response
            })

        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            print(f"\n=== 새로운 질문 접수 ===\n질문: {user_message}")
            
            # 검색 함수 가져오기
            search_func = get_vector_db()
            
            # 문서 검색
            print("\n=== 문서 검색 시작 ===")
            relevant_docs = search_func(user_message)
            print(f"검색된 문서 수: {len(relevant_docs)}")
            
            def format_docs(docs):
                if not docs:
                    print("경고: 검색된 문서가 없습니다!")
                    return "관련 문서를 찾을 수 없습니다."
                    
                formatted = '\n\n'.join([d.page_content for d in docs])
                print(f"\n=== 검색된 문서 내용 ===\n{formatted[:500]}...\n")
                return formatted
            
            template = get_template()
            prompt = ChatPromptTemplate.from_template(template)
            model = ChatOpenAI(temperature=0.7, max_tokens=1000)
            
            chain = {
                'context': lambda x: format_docs(relevant_docs),
                'question': RunnablePassthrough()
            } | prompt | model | StrOutputParser()
            
            response = chain.invoke(user_message)
            print(f"\n=== 생성된 답변 ===\n{response}\n")
            
            return JsonResponse({
                'status': 'success',
                'response': response
            })
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            import traceback
            print("상세 오류:", traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'error': str(e),
                'response': '죄송합니다. 오류가 발생했습니다.'
            })
    
    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)


@require_http_methods(["GET"])
def get_google_news(request):
    try:
        print("=== Google News API 호출 시작 ===")  # 로그 추가
        rss_url = "https://news.google.com/rss/search?q=한국공항공사&hl=ko&gl=KR&ceid=KR:ko"
        
        print("RSS URL:", rss_url)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # requests로 먼저 데이터 가져오기
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # feedparser로 파싱
        feed = feedparser.parse(response.content)
        
        news_items = []
        for entry in feed.entries[:3]:  # 최근 5개 뉴스
            try:
                pub_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'pubDate': pub_date.strftime('%Y.%m.%d')
                })
            except Exception as e:
                print(f"뉴스 항목 처리 중 오류: {str(e)}")
                continue
        
        print(f"크롤링된 뉴스 개수: {len(news_items)}")
        return JsonResponse({'success': True, 'news': news_items})
            
    except Exception as e:
        print(f"뉴스 크롤링 실패: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_news(request):
    try:
        crawler = KACCrawler()
        count = int(request.GET.get('count', 3))
        
        # press 카테고리의 뉴스를 가져옴
        news = crawler.get_notices('press', page=1, count=count)
        
        # 디버깅을 위한 로그
        print("Crawler response:", news)
        
        if not news:  # 뉴스가 비어있는 경우
            print("No news fetched from crawler")
            return JsonResponse([], safe=False)
            
        return JsonResponse(news, safe=False)
    except Exception as e:
        print(f"뉴스 가져오기 실패: {str(e)}")
        import traceback
        print(traceback.format_exc())  # 상세한 에러 로그
        return JsonResponse({
            'error': str(e)
        }, status=500)