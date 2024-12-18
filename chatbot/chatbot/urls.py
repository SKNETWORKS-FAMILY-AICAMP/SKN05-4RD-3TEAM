"""
URL 설정 파일
웹 요청 URL과 이를 처리할 뷰 함수를 연결
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # 관리자
    path('admin/', admin.site.urls),
    
    # 메인 페이지
    path('', views.index, name='index'),
    
    # 채팅 관련
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('chatbot/', views.chatbot_api, name='chatbot_api'),
    
    # 인증 관련
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # 마이페이지 관련
    path('mypage/', views.my_page_view, name='my_page'),  # 하나의 경로로 통일
    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # FAQ
    path('faq/', views.faq_view, name='faq'),
    
    # API 엔드포인트
    path('api/news/', views.get_news, name='get_news'),
    path('api/google-news/', views.get_google_news, name='get_google_news'),# URL 패턴 통일
    path('api/weather/', views.get_weather, name='get_weather'),          # URL 패턴 통일
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)