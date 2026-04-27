from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Главная
    path('', views.HomeView.as_view(), name='home'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Видео CRUD
    path('video/<int:pk>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('video/create/', views.VideoCreateView.as_view(), name='video_create'),
    path('video/<int:pk>/edit/', views.VideoUpdateView.as_view(), name='video_edit'),
    path('video/<int:pk>/delete/', views.VideoDeleteView.as_view(), name='video_delete'),

    # Взаимодействия
    path('video/<int:pk>/like/', views.LikeToggleView.as_view(), name='like_toggle'),
    path('video/<int:pk>/comment/', views.CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:comment_pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('subscribe/<str:username>/', views.SubscriptionToggleView.as_view(), name='toggle_subscription'),

    # Уведомления
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),

    # Профили
    path('channel/<str:username>/', views.ChannelDetailView.as_view(), name='channel'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),

    # Поиск и лента
    path('search/', views.SearchView.as_view(), name='search'),
    path('live-search/', views.LiveSearchView.as_view(), name='live_search'),
    path('subscriptions/', views.SubscriptionFeedView.as_view(), name='subscription_feed'),
]