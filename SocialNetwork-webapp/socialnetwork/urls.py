from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    re_path(r'^$',                 views.global_stream,     name='home'),
    re_path(r'^admin$', admin.site.urls),
    re_path(r'^myProfile$',        views.myProfile,         name='myProfile'),
    re_path(r'^someone_profile$',  views.someone_profile,   name='someone_profile'),
    re_path(r'^add_post$',         views.add_post,          name='add_post'),
    re_path(r'^global_stream$',    views.global_stream,     name='global_stream'),
    re_path(r'^register$',         views.register,          name='register'),
    re_path(r'^add_comment$',      views.add_comment,       name='add_comment'),
    re_path(r'^relate$', views.relate, name='relate'),
    re_path(r'^hug$', views.hug, name='hug'),
    re_path(r'^start_chat$', views.start_chat, name='start_chat'),
    re_path(r'^chat$', views.chat, name='chat'),
    re_path(r'^someone_not_exist$',views.someone_not_exist, name='someone_not_exist'),

    re_path(r'^get_list_json$',    views.get_list_json,     name='get_list_json'),
    # Route for built-in authentication with our own custom login page
    re_path(r'^login$',    LoginView.as_view(), {'template_name':'socialnetwork/login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    re_path(r'^logout$',   LogoutView.as_view(),                                  name='logout'),
]