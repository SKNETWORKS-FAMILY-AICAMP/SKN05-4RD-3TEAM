from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # 메인 페이지
    path('', views.index, name='index'),
    
    # 채팅 관련
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    
    # 인증 관련
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # 마이페이지 관련
    path('mypage/', views.my_page_view, name='my_page'),
    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # API 엔드포인트
    path('api/notices/', views.get_kac_notices, name='get_kac_notices'),
    path('api/google-news/', views.get_google_news, name='get_google_news'),  # URL 수정
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)