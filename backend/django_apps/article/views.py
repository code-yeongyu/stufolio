"""
Views 파일은 Article 앱의 실제로 "보이는" 부분을 담당하는 파일입니다.
따라서, 다음과 같은 내용들이 포함되어있습니다:
이미지, 하트, 게시글 업로드 및 조회, 작성자별 게시글 조회
"""

import json
from urllib.parse import unquote

from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from django_apps.article.models import Article, Image
from django_apps.article.serializers import ArticleSerializer, ImageSerializer
from stufolio import settings


class ArticleList(generics.ListAPIView, APIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    # 게시글 리스트 반환 제너릭 설정

    def _is_image_available(self, pk):
        try:
            Image.objects.get(id=pk)
            return True
        except Image.DoesNotExist:
            return False

    def post(self, request):  # 작성자 이름 자동추가 기능을 위해 post용 뷰 분리
        if request.user.is_authenticated:  # 사용자가 인증 되었을경우
            serializer = ArticleSerializer(data=request.data)
            for temp in json.loads(
                    request.data.get('images_id')):  # 이미지의 id값들이 유효한지 체크
                if not self._is_image_available(temp):  # 잘못된 id값을 받았을 경우
                    return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            if serializer.is_valid():
                serializer.save(writer=request.user)  # 작성자 요청자로 설정
                return JsonResponse(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)  # 폼에 오류가 있을 경우
        return Response(status=status.HTTP_401_UNAUTHORIZED)  #인증되지 않았을 경우


class ArticleDetail(generics.RetrieveUpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    # 게시글 받아오는 기능 제너릭 설정


@api_view(['POST'])
def create_image(request):
    if request.user.is_authenticated:
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "id": serializer.data['id']
                }, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_articles_page(request, pk):
    articles = Article.objects.all().order_by('-created_at')
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data[int(pk) * 10 - 10:int(pk) * 10])


@api_view(['GET'])
def image(request, pk):  # 이미지 반환
    test_file = open(
        settings.BASE_DIR + "/" + str(
            get_object_or_404(Image, pk=pk).image.url), 'rb')
    return HttpResponse(
        content=test_file,
        content_type="image/jpeg",
        status=status.HTTP_200_OK)


@api_view(['GET'])
def image_thumbnail(request, pk):  # 이미지 반환

    test_file = open(
        unquote(settings.BASE_DIR + "/" +
                str(get_object_or_404(Image, pk=pk).thumbnail.url)), 'rb')
    return HttpResponse(
        content=test_file,
        content_type="image/jpeg",
        status=status.HTTP_200_OK)


@api_view(['POST'])
def article_heart(request, pk):  # 게시글에 하트 추가
    if request.user.is_authenticated:
        article = get_object_or_404(Article, pk=pk)
        article_heart, article_heart_created = article.heart_set.get_or_create(
            user=request.user)
        if article_heart_created:
            return JsonResponse({
                'like_count': article.count_hearts,
                'isCreated': True,
                'username': request.user.username
            })
        article_heart.delete()
        return JsonResponse({
            'like_count': article.count_hearts,
            'isCreated': False,
            'username': request.user.username
        })
    return Response(status=status.HTTP_401_UNAUTHORIZED)
    # 하트가 눌린 게시글의 경우 하트 제거, 하트가 눌리지 않은 게시글의 경우 하트 생성


@api_view(['GET'])
def article_profile(request, string):  #유저가 작성한 게시글을 반환
    try:
        u = User.objects.get(username=string)
        articles = Article.objects.filter(writer=u)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        raise Http404


@api_view(['GET'])
def article_profile_page(request, string, pk):  #유저가 작성한 게시글을 반환
    try:
        u = User.objects.get(username=string)
        articles = Article.objects.filter(writer=u)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data[int(pk) * 10 - 10:int(pk) * 10])
    except Article.DoesNotExist:
        raise Http404
