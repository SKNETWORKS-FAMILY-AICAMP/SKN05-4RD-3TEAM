from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.contrib.auth.models import User
from .models import Profile
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm



def index(request):
    if request.user.is_authenticated:
        return redirect('chat')
    return redirect('account:login')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('chat')
        else:
            return render(request, 'account/login.html', {'error': '아이디 또는 비밀번호가 올바르지 않습니다.'})
    
    return render(request, 'account/login.html')

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
                return render(request, 'account/register.html', {'error': '비밀번호가 일치하지 않습니다.'})

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
                return redirect('account:login')

        except IntegrityError as e:
            messages.error(request, '이미 등록된 사용자입니다.')
            return render(request, 'account/register.html', {'error': '이미 등록된 사용자입니다.'})
        except Exception as e:
            messages.error(request, f'회원가입 중 오류가 발생했습니다: {str(e)}')
            return render(request, 'account/register.html', {'error': f'회원가입 중 오류가 발생했습니다: {str(e)}'})

    return render(request, 'account/register.html')

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
            return redirect('account:my_page')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'account/mypage.html', context)

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
                return redirect('account/my_page')
            
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
            
    return redirect('account:my_page')

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
                return redirect('account/login')
                
        except Exception as e:
            messages.error(request, f'회원 탈퇴 중 오류가 발생했습니다: {str(e)}')
            return redirect('account:my_page')
    return redirect('account:my_page')

def logout_view(request):
    logout(request)
    return redirect('account:login')

@login_required(login_url='account/login')
def mypage_view(request):
    context = {
        'user': request.user,
    }
    return render(request, 'account/mypage.html', context)