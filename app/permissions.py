from django.contrib.auth.mixins import UserPassesTestMixin

class VideoAuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        video = self.get_object()
        return self.request.user == video.author

class CommentAuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user