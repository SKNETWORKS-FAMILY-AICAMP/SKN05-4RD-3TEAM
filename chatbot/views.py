import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import json
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from .vector_db import get_vector_db, get_template
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from PIL import Image
from django.db import transaction
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.views.decorators.csrf import csrf_exempt
from .utils.kac_crawler import KACCrawler
import logging
from .utils.kac_notice_crawler import KACNoticeCrawler
from django.views.decorators.http import require_http_methods
import feedparser
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import urllib.parse
import feedparser
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# OpenAI API 키 로드
openai_api_key = os.getenv('OPENAI_API_KEY')

# 전역 변수로 모델과 벡터 DB 초기화
chat_model = ChatOpenAI(
    model_name="ft:gpt-4o-mini-2024-07-18:personal::AXmDF5MY",
    temperature=0.7,
    max_tokens=1000,
    openai_api_key=openai_api_key
)

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

def index(request):
    if request.user.is_authenticated:
        return redirect('chat')
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('chat')
        else:
            return render(request, 'login.html', {'error': '아이디 또는 비밀번호가 올바르지 않습니다.'})
    
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        try:
            # POST 데이터 확인을 위한 로그 추가
            print("POST 데이터:", request.POST)
            
            employee_id = request.POST.get('employee_id')
            name = request.POST.get('name')
            department = request.POST.get('department')
            
            # 각 필드 값 확인을 위한 로그
            print("사번:", employee_id)
            print("이름:", name)
            print("부서:", department)
            
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            if password != password_confirm:
                return render(request, 'register.html', {'error': '비밀번호가 일치하지 않습니다.'})

            with transaction.atomic():
                user = User.objects.create_user(
                    username=employee_id,
                    password=password
                )
                user.first_name = name
                user.save()

                # 프로필 생성 로그 추가
                print("프로필 생성 시작 - 부서:", department)
                
                Profile.objects.filter(user=user).delete()
                profile = Profile.objects.create(
                    user=user,
                    department=department
                )
                
                # 생성된 프로필 확인 로그
                print("생성된 프로필 부서:", profile.department)

                messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
                return redirect('login')

        except IntegrityError as e:
            messages.error(request, '이미 등록된 사용자입니다.')
            return render(request, 'register.html', {'error': '이미 등록된 사용자입니다.'})
        except Exception as e:
            messages.error(request, f'회원가입 중 오류가 발생했습니다: {str(e)}')
            return render(request, 'register.html', {'error': f'회원가입 중 오류가 발생했습니다: {str(e)}'})

    return render(request, 'register.html')

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

@login_required
def my_page_view(request):
    # 프로필이 없으면 생성
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '프로필이 업데이트되었습니다.')
            return redirect('my_page')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'mypage.html', context)

@login_required
def faq_view(request):
    return render(request, 'faq.html')

@login_required
def update_profile_image(request):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        try:
            # 이미지 파일 가져오기
            image_file = request.FILES['profile_image']
            
            # 이미지 확장자 검사
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if image_file.content_type not in allowed_types:
                messages.error(request, '지원하지 않는 이미지 형식입니다. (JPEG, PNG, GIF만 가능)')
                return redirect('my_page')
            
            # 기존 프로필 이미지 삭제 (기본 이미지가 아닌 경우)
            profile = request.user.profile
            if profile.profile_image and 'default.png' not in profile.profile_image.name:
                if os.path.isfile(profile.profile_image.path):
                    os.remove(profile.profile_image.path)
            
            # 새 이미지 저장
            profile.profile_image = image_file
            profile.save()
            
            messages.success(request, '프로필 이미지가 업데이트되었습니다.')
            
        except Exception as e:
            messages.error(request, f'이미지 업로드 중 오류가 발생했습니다: {str(e)}')
            
    return redirect('my_page')

@login_required
@transaction.atomic  # 트랜잭션 처리 추가
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        try:
            with transaction.atomic():
                # 프로필 이미지가 있다면 삭제
                if hasattr(user, 'profile') and user.profile.profile_image:
                    if user.profile.profile_image.name != 'profile_images/default.png':
                        user.profile.profile_image.delete()  # 실제 이미지 파일 삭제
                
                # 채팅 기록 삭제 (ChatHistory 모델이 있는 경우)
                if hasattr(user, 'chathistory_set'):
                    user.chathistory_set.all().delete()
                
                # 프로필 삭제
                if hasattr(user, 'profile'):
                    user.profile.delete()
                
                # 사용자 계정 삭제
                user.delete()  # User 모델 삭제 (CASCADE로 연결된 모든 데이터 삭제)
                
                # 로그아웃
                logout(request)
                messages.success(request, '회원 탈퇴가 완료되었습니다.')
                return redirect('login')
                
        except Exception as e:
            messages.error(request, f'회원 탈퇴 중 오류가 발생했습니다: {str(e)}')
            return redirect('my_page')
    return redirect('my_page')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def mypage_view(request):
    context = {
        'user': request.user,
    }
    return render(request, 'mypage.html', context)

@require_http_methods(["GET"])
def get_kac_notices(request):
    try:
        crawler = KACNoticeCrawler()
        category = request.GET.get('category', 'notice').split(':')[0]  # notice:1 같은 형식 처리
        count = int(request.GET.get('count', 5))
        
        notices = crawler.get_notices(category, count)
        return JsonResponse({'success': True, 'notices': notices})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def get_all_notices(request):
    crawler = KACCrawler()
    all_notices = crawler.get_all_categories()
    return JsonResponse(all_notices)

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
        for entry in feed.entries[:5]:  # 최근 5개 뉴스
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

