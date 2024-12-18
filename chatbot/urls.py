from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # 메인 페이지
    path('', views.index, name='index'),

##채팅 관련
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),

#인증 관련
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

#마이페이지 관련
    path('mypage/', views.my_page_view, name='my_page'),
    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('logout/', views.logout_view, name='logout'),

#API 엔드포인트
    path('api/google-news/', views.get_google_news, name='get_google_news'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)