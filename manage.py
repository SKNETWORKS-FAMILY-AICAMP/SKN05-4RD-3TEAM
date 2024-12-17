#!/usr/bin/env python
"""
Django의 명령행 유틸리티
서버 실행, 마이그레이션 등 Django 프로젝트 관리를 위한 커맨드라인 도구
"""
import os
import sys

def main():
    """
    메인 함수
    Django 설정을 로드하고 명령행 인자를 처리
    """
    # Django 설정 모듈 지정
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot.settings')
    try:
        # Django 관리 명령어 실행 모듈 임포트
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # 명령행 인자를 처리하여 해당하는 Django 명령 실행
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()