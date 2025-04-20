from django.urls import path
from . import views
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns=[
    path("",views.index,name="index"),
    path("login",views.login_view, name="login"),
    path("register",views.register, name="register"),
    path("recognize", views.recognize_and_mark, name="recognize"),
    path("history/", views.attendance_history, name="attendance_history"),
    path("logout", views.logout_view, name="logout"),
]