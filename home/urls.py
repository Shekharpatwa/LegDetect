from django.contrib import admin
from django.urls import path
from home import views
from .import views

urlpatterns = [
    path('', views.Homepage, name='Homepage'),
    path('Homepage.html',views.Homepage,name='Homepage'),
    path('frame_feed', views.frame_feed, name='frame_feed'),
    path('pose_feed', views.pose_feed, name='pose_feed'),
    path('video_feed', views.video_feed, name='video_feed'),

    #Disease urls
    path('GenuValgum', views.GenuValgum, name='GenuValgum'),
    path('GenuVarum', views.GenuVarum, name='Genu Varum'),

    #Treatment urls
    path('TreatmentValgum', views.TreatmentValgum, name='TreatmentValgum'),
    path('TreatmentVarum', views.TreatmentVarum, name='TreatmentVarum'),

    #Detection url
    path('Detection', views.Detection, name='Detection'),

    #Sgnup, Login, Logout urls
    path('signup',views.handleSignup, name='handleSignup'),
    path('login',views.handleLogin, name='handleLogin'),
    path('logout',views.handleLogout, name='handleLogout'),

    # Forget and change password urls 
    path('changepass/<str:id>/',views.changepassword,name="changepassword"),
    path('forgetpassword/',views.fpass,name='fpass')
]


