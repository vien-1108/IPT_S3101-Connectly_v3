from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate
from .views import ProtectedView
from .views import AdminOnlyView
from .views import SafeUserLookupView
from .views import LikePostView, CommentOnPostView, CommentsForPostView
from .views import GoogleLogin
from .views import NewsFeedView

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('safe-user/', SafeUserLookupView.as_view()),
    path('', PostListCreate.as_view(), name='post-list-create'),
    path('<int:pk>/like/', LikePostView.as_view(), name='like-post'),
    path('<int:pk>/comment/', CommentOnPostView.as_view(), name='comment-post'),
    path('<int:pk>/comments/', CommentsForPostView.as_view(), name='post-comments'),
    path('auth/social/google/', GoogleLogin.as_view(), name='google-login'),
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
]
