from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from .models import User, Post, Like, Comment
from .serializers import UserSerializer, CommentSerializer, LikeSerializer, PostSerializer
from .factories import PostFactory
from .authentication import CsrfExemptTokenAuthentication
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter



class SafeUserLookupView(APIView):
    def get(self, request):
        user_id = request.GET.get("id")
        user = User.objects.filter(id=user_id).first()  # Safe query

        if user:
            return Response({"username": user.username})
        return Response({"error": "User not found"}, status=404)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]


    def get(self, request):
        return Response({"message": "Welcome, Admin!"})


class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        return Response({"message": "You are authenticated!"})


class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():       
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListCreate(APIView):
    authentication_classes = [CsrfExemptTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a post.")

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatePostView(APIView):
    def post(self, request):
        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {})
            )
            return Response({'message': 'Post created successfully!', 'post_id': post.id},
                            status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        if post.author != request.user:
            raise PermissionDenied("You are not allowed to access this post.")
        return Response({"content": post.content})
    

class LikePostView(APIView):
    authentication_classes = [CsrfExemptTokenAuthentication]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = Post.objects.filter(id=pk).first()
        if not post:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({'message': 'Post already liked'}, status=status.HTTP_200_OK)

        Like.objects.create(user=request.user, post=post)
        return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)


class CommentOnPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = Post.objects.filter(id=pk).first()
        if not post:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['post'] = pk
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentsForPostView(APIView):
    def get(self, request, pk):
        comments = Comment.objects.filter(post_id=pk).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    

class NewsFeedView(ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]