from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.FeedList.as_view()),
    path('<int:pk>/', views.FeedDetail.as_view()),
    path('<int:pk>/comment/', views.CommentView.as_view()),
    path('<int:pk>/comment/<int:comment_pk>/', views.CommentView.as_view()),
    path('<int:pk>/comment/<int:comment_pk>/like/', views.CommentLikeView.as_view()),
    path('<int:pk>/like/', views.FeedLikeView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
