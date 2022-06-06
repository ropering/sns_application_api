from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from account import views

urlpatterns = [
    path('signup/', views.UserCreate.as_view()),  # 회원 가입
    path('profile/', views.Profile.as_view()),  # 프로필 조회
    path('api-auth/', include('rest_framework.urls')),  # 로그인
    path('api-token-auth/', obtain_auth_token),  # 토큰 발급, 조회
]