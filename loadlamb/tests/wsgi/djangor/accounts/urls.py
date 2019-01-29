from django.contrib.auth.views import LoginView
from django.urls import path
from .views import UserDetailView


urlpatterns = [
    path('profile/', UserDetailView.as_view(), name='user-details'),
    path('login/', LoginView.as_view(success_url='/'), name='login'),
]