from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.db.models import Count
from .models import Video, Comment, Like, Subscription, Notification, User
from .forms import VideoForm, CommentForm, ProfileUpdateForm, RegisterForm
from .permissions import VideoAuthorRequiredMixin, CommentAuthorRequiredMixin
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

class HomeView(ListView):
    model = Video
    template_name = 'videos/home.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        return Video.objects.annotate(like_count=Count('likes')).order_by('-created_at')

class VideoDetailView(DetailView):
    model = Video
    template_name = 'videos/video_detail.html'
    context_object_name = 'video'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.object
        video.views += 1
        video.save()
        context['comment_form'] = CommentForm()
        context['comments'] = video.comments.all().order_by('-created_at')
        if self.request.user.is_authenticated:
            user_like = Like.objects.filter(video=video, user=self.request.user).first()
            context['user_like'] = user_like.value if user_like else 0
        return context

class VideoCreateView(LoginRequiredMixin, CreateView):
    model = Video
    form_class = VideoForm
    template_name = 'videos/video_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('video_detail', kwargs={'pk': self.object.pk}) 

class VideoUpdateView(LoginRequiredMixin, VideoAuthorRequiredMixin, UpdateView):
    model = Video
    form_class = VideoForm
    template_name = 'videos/video_form.html'

class VideoDeleteView(LoginRequiredMixin, VideoAuthorRequiredMixin, DeleteView):
    model = Video
    template_name = 'videos/video_confirm_delete.html'
    success_url = reverse_lazy('home')

class LikeToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        like, created = Like.objects.get_or_create(
            video=video,
            user=request.user,
            defaults={'value': 1} 
        )
        if not created:
            if like.value == 1: 
                like.delete()
            else:               
                like.value = 1
                like.save()

        return render(request, 'partials/like_buttons.html', {
            'video': video,
            'user_like': 1 if like.pk and like.value == 1 else 0,
            'likes_count': video.likes.filter(value=1).count(),
            'dislikes_count': video.likes.filter(value=-1).count(),
        })

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        video = get_object_or_404(Video, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.video = video
        form.save()
        comments = video.comments.all().order_by('-created_at')
        return render(self.request, 'partials/comments_list.html', {
            'comments': comments,
            'video': video,
        })

class CommentDeleteView(LoginRequiredMixin, CommentAuthorRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_pk'
    template_name = 'partials/comments_list.html' 

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        video = self.object.video
        self.object.delete()
        comments = video.comments.all().order_by('-created_at')
        return render(request, 'partials/comments_list.html', {
            'comments': comments,
            'video': video,
        })

class SubscriptionToggleView(LoginRequiredMixin, View):
    def post(self, request, username):
        channel = get_object_or_404(User, username=username)
        sub, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            channel=channel,
        )
        if not created:
            sub.delete()
        return render(request, 'partials/subscribe_button.html', {
            'channel': channel,
            'is_subscribed': request.user.subscribers.filter(channel=channel).exists(),
        })

class NotificationsView(LoginRequiredMixin, View):
    def get(self, request):
        qs = request.user.notifications.filter(is_read=False).order_by('-created_at')
        top_notifications = list(qs[:10])
        if top_notifications:
            Notification.objects.filter(id__in=[n.id for n in top_notifications]).update(is_read=True)
        return render(request, 'partials/notifications.html', {
            'notifications': top_notifications,
        })

class ChannelDetailView(DetailView):
    model = User
    template_name = 'users/channel.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'channel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = self.object.videos.all().order_by('-created_at')
        if self.request.user == self.object:
            context['deleted_videos'] = Video.all_objects.filter(
                author=self.object,
                status=False
            ).order_by('-created_at')
        else:
            context['deleted_videos'] = None
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'users/profile_form.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('channel', kwargs={'username': self.object.username})

class SearchView(ListView):
    template_name = 'videos/search.html'
    context_object_name = 'videos'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Video.objects.filter(title__icontains=query).order_by('-views')
        return Video.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class LiveSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        suggestions = Video.objects.filter(title__icontains=query)[:5]
        return render(request, 'partials/search_suggestions.html', {
            'suggestions': suggestions,
        })
    
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)
    
class SubscriptionFeedView(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'videos/subscription_feed.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        subscribed_channels = Subscription.objects.filter(
            subscriber=self.request.user
        ).values_list('channel_id', flat=True)
        return Video.objects.filter(author_id__in=subscribed_channels).order_by('-created_at')
    
@login_required
def soft_delete_video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if video.author != request.user:
        return redirect('home')
    video.soft_delete()
    messages.success(request, 'Видео перемещено в корзину.')
    return redirect('channel', username=request.user.username)

@login_required
def restore_video(request, pk):
    video = get_object_or_404(Video.all_objects, pk=pk)
    if video.author != request.user:
        messages.error(request, 'Вы не можете восстановить чужое видео.')
        return redirect('home')
    video.restore()
    messages.success(request, 'Видео восстановлено.')
    return redirect('video_detail', pk=video.pk)