"""
URL configuration for pjt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from account.views import index  # 앱의 views.py에서 my_view 가져오기

urlpatterns = [
    path('admin/', admin.site.urls),

    # 메인 앱
    path('', index, name='index'),

    # 챗봇 앱
    path('chat/', include('chatbot.urls')),

    # 계정 관리 앱
    path('account/', include('account.urls')),
]

# 개발 환경에서 미디어 파일 서빙
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)