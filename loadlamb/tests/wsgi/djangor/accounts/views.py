from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import DetailView


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'registration/user-detail.html'

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(pk=self.request.user.pk)
        except self.model.DoesNotExist:
            raise Http404

