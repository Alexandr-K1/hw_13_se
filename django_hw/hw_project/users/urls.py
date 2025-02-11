from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

from . import views
from .forms import LoginForm

app_name = 'users'

urlpatterns = [
    path('signup/', views.RegisterView.as_view(), name = 'signup'),
    path('login/', LoginView.as_view(template_name='users/login.html', form_class=LoginForm, redirect_authenticated_user=True),
         name = 'login'),
    path('logout/', LogoutView.as_view(next_page='quotes:home'), name = 'logout'),
    path('profile/', views.profile, name = 'profile'),
    path('reset_password/', views.ResetPasswordView.as_view(), name = 'password_reset'),
    path('reset_password/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name = 'password_reset_done'),
    path('reset_password/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password/complete/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name = 'password_reset_complete'),
]