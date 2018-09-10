from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import logout_then_login, login, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.contrib.auth.decorators import login_required
from usuario.views import CustomLoginView
from usuario.views import customlogout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pet/', include('refuge.urls')),
    path('user/', include('usuario.urls')),
    path('reset/password_reset', password_reset, {'template_name': 'recover_password/password_reset_form.html',
                                                  'email_template_name': 'recover_password/password_reset_email.html'}, name='password_reset'),

    path('reset/password_reset_done', password_reset_done,
         {'template_name': 'recover_password/password_reset_done.html'}, name='password_reset_done'),

    path('reset/<uidb64>/<token>/ ', password_reset_confirm, {
         'template_name': 'recover_password/password_reset_confirm.html'}, name='password_reset_confirm'),
    path('reset/password_reset_complete', password_reset_complete,
         {'template_name': 'recover_password/password_reset_complete.html'}, name='password_reset_complete'),

    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', customlogout, name='logout'),


]
