# 내장 라이브러리
import datetime

# django
from django.core.paginator import Paginator
from django.utils import timezone

# 사용자 정의 모듈
from account.models import User
from .models import Feed, Comment
from .serializers import FeedSerializer, CommentSerializer

# rest_framework 관련
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# Feed 의 목록을 보여주는 역할
class FeedList(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        feeds = Feed.objects.all().order_by('-created_at')
        sort = request.GET.get('sort', '')  # sort 값이 넘어오는 것이 없더라도 없는 값으로 처리하기 위함 (None 방지)
        days = request.GET.get('days', '')
        page = request.GET.get('page', '')
        categories = ['like']

        def previous_time(day):
            return timezone.now() - datetime.timedelta(days=day)

        # 좋아요 순 정렬 and 작성 날짜 순 필터링
        if sort in categories and days.isdigit():
            days = int(days)
            if days > 0:
                feeds = feeds.filter(created_at__gte=previous_time(days)).order_by('-like_count')
        # 좋아요 순 정렬
        elif sort in categories:
            feeds = feeds.order_by('-like_count')
        # 작성 날짜 순 필터링
        elif days.isdigit():
            days = int(days)
            if days > 0:
                feeds = feeds.filter(created_at__gte=previous_time(days))

        # 30개씩 pagination
        paginator = Paginator(feeds, 30)
        feeds = paginator.get_page(page)

        # 여러 개의 객체를 serialization하기 위해 many=True로 설정
        serializer = FeedSerializer(feeds, many=True)
        return Response(serializer.data)

    # 새로운 Feed 글을 작성할 때
    def post(self, request):
        feed = Feed()
        feed.title = request.POST['title']
        feed.content = request.POST['content']
        feed.user = request.user
        feed.save()

        # serializer = FeedSerializer(data=request.data)
        # if serializer.is_valid():  # 유효성 검사
        #     serializer.save()  # 저장
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=feed)


class FeedDetail(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 단일 피드 조회
    def get(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        serializer = FeedSerializer(feed)
        return Response(serializer.data)

    # 단일 피드 수정
    def put(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        serializer = FeedSerializer(feed, data=request.data)
        if serializer.is_valid():
            if request.user == feed.user:
                serializer.save()
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 단일 피드 삭제
    def delete(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        if request.user == feed.user:
            feed.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 게시물에 해당하는 전체 댓글 조회
    def get(self, request, pk):
        comment = Comment.objects.filter(feed=pk)  # 복수 개 가능
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data)

    # 게시물에 해당하는 댓글 생성
    def post(self, request, pk):
        comment = Comment()
        comment.comment = request.POST['comment']
        comment.feed = Feed(id=pk)
        comment.user = request.user
        comment.save()

        # serializer = CommentSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # 게시물에 해당하는 단일 댓글 수정
    def put(self, request, pk, comment_pk):
        comment = get_object_or_404(Comment, feed=pk, pk=comment_pk)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            if request.user == comment.user:
                serializer.save()
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 게시물, 댓글에 해당하는 댓글 삭제
    def delete(self, request, pk, comment_pk):
        comment = get_object_or_404(Comment, feed=pk, pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
            return Response(status=200, data=comment.user)
        return Response(status=400, data=comment.user)


class FeedLikeView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        # 현재 피드
        feed = get_object_or_404(Feed, pk=pk)
        # 현재 유저
        profile = User.objects.get(nickname=request.user)
        # 해당 게시글 좋아요 유무 파악
        check_like_post = profile.like_posts.filter(id=pk)

        if check_like_post.exists():
            profile.like_posts.remove(feed)  # 현재 유저의 좋아요한 피드 목록에 현재 피드 추가
            feed.like_count -= 1  # 현재 피드의 좋아요 개수 하향
            feed.save()
            return Response('remove')
        else:
            profile.like_posts.add(feed)  # 현재 유저의 좋아요한 피드 목록에 현재 피드 추가
            feed.like_count += 1  # 현재 피드의 좋아요 개수 상향
            feed.save()
            return Response('add')


class CommentLikeView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, pk, comment_pk):
        # 현재 댓글
        comment = get_object_or_404(Comment, pk=comment_pk)
        # 현재 유저
        profile = User.objects.get(nickname=request.user)
        # 해당 댓글 좋아요 유무 파악
        check_like_comment = profile.like_comments.filter(id=comment_pk)

        if check_like_comment.exists():
            profile.like_comments.remove(comment)
            comment.like_count -= 1
            comment.save()
            return Response('remove')
        else:
            profile.like_comments.add(comment)
            comment.like_count += 1
            comment.save()
            return Response('add')