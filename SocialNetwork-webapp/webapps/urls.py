from django.urls import include, re_path
from socialnetwork import views

urlpatterns = [
    re_path(r'^$',              views.global_stream),
    re_path(r'^socialnetwork/', include('socialnetwork.urls')),
]