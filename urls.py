from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chatbot import views  # views import 추가

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', views.chat_api, name='chat_api'), # type: ignore
    path('', include('chatbot.urls')),  # chatbot 앱의 URLs만 include
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)