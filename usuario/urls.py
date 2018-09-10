from django.urls import path

from . import views

app_name = 'user'
urlpatterns = [
    path('register/',views.UserRegistry.as_view(),name='user_register'),
 	path('listuser/',views.list,name='list'),
 	path('api/',views.UserAPI.as_view(),name='api'),
 	path('view/',views.user,name='user'),
 	path('wait_confirmation/', views.view_waiting_page, name='waiting_page'),
    path('has_not_permits/', views.view_has_not_permits, name='has_not_permits'),
 	path('session/token/auth.json', views.user_session_token_authentication, name='user_session_token_authentication_json'),
    path('session/token/confirm/json', views.user_session_confirm_token, name='user_session_confirm_token_json'),
    
    
]
