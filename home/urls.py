from django.contrib import admin
from django.urls import path
from home import views
from .import views

# from django.views.generic.base import RedirectView
# from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    path('', views.Homepage, name='Homepage'),
    path('Homepage.html',views.Homepage,name='Homepage'),
    # path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.jpg'))),
    path('video_feed', views.video_feed, name='video_feed'),
    path('image_feed', views.image_feed, name='image_feed'),

    path('Hospitals',views.Hospitals, name='Hospitals'),

    #Disease urls
    path('GenuValgum', views.GenuValgum, name='GenuValgum'),
    path('GenuVarum', views.GenuVarum, name='Genu Varum'),

    #Treatment urls
    path('TreatmentValgum', views.TreatmentValgum, name='TreatmentValgum'),
    path('TreatmentVarum', views.TreatmentVarum, name='TreatmentVarum'),

    #Detection url
    path('Detection_Live', views.Detection_Live, name='Detection_Live'),
    path('Detection_img', views.Detection_img, name='Detection_img'),


    #Sgnup, Login, Logout urls
    path('signup',views.handleSignup, name='handleSignup'),
    path('login',views.handleLogin, name='handleLogin'),
    path('logout',views.handleLogout, name='handleLogout'),

    # # #User Profile url
    # path('UserProfile',views.UserProfile,name='UserProfile'),

    #Storing user deformity result
    # path('live_Res',views.live_Res, name='live_Res'),
    # path('img_Res',views.img_Res, name='img_Res'),

    # Forget and change password urls 
    path('changepass/<str:id>/',views.changepassword,name="changepassword"),
    path('forgetpassword/',views.fpass,name='fpass')
]


