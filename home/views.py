from django.shortcuts import render, HttpResponse,redirect
from django.http.response import StreamingHttpResponse

from home.camera import VideoImgManager
from home.body_detect import VideoImgManagers
from datetime import datetime
from django.contrib.auth import authenticate, login, logout	
from django.contrib.auth.models import User
from django.contrib import messages
from .models import liveResult
from .models import imageResult
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
import uuid
from .models import Profile

import cv2 as cv

# Create your views here.

def Homepage(request):
    return render(request,'Homepage.html')

def GenuValgum(request):
    return render(request,'GenuValgum.html')

def GenuVarum(request):
    return render(request,'GenuVarum.html')

def TreatmentValgum(request):
    return render(request,'TreatmentValgum.html')

def TreatmentVarum(request):
    return render(request,'TreatmentVarum.html')

def Detection_Live(request):
	return render(request,'Detection_Live.html')

# def Detection_img(request):
#     return render(request,'Detection_img.html')

def handleSignup(request):
	# Get the POST parameters
	if request.method == "POST":
		username = request.POST['username']
		email = request.POST['email']
		pass1 = request.POST['pass1']
		pass2 = request.POST['pass2']
	
		#Check for errorneous inputs

		#Username must be under 10 character
		if len(username) > 10:
			messages.error(request, 'Username must be under 10 character')
			return redirect('Homepage')
		
		#Username should be alphanumeric
		if not username.isalnum():
			messages.error(request, 'Username should only contain letters and numbers')
			return redirect('Homepage')
			
		#password should match
		if pass1 != pass2:
			messages.error(request, 'Passwords do not match')
			return redirect('Homepage')
			
		# data=User.objects.all()
		# z=0
		# for i in data:
    	# 	if i.email==email:
    	# 		z=1
		# 		break
		# if z==1:
    	# 	return render(request,"Homepage.html",{"Variable":"Email id already exists"})

		# #Create the User
		myuser = User.objects.create_user(username,email,pass1)
		# myuser.first_name = fname
		

		myuser.save()
		
		# ftoken = str(uuid.uuid4())
		
		# profile = Profile.objects.create(user=user,forget_token=ftoken)
		
		messages.success(request, 'Your account has been successfully created')

		
		

		# return redirect('Homepage')
		return redirect('GenuValgum')

	else:
		return HttpResponse('404 - Not found')


			
def handleLogin(request):
		# Get the POST parameters
	if request.method == "POST":
		loginusername = request.POST['loginusername']
		loginpassword = request.POST['loginpassword']
		
		user = authenticate(username=loginusername, password=loginpassword)
		

		if user is not None:
			login(request, user)
			messages.success(request, "Successfully Logged In")
			return redirect('Homepage')

	else:
		messages.error(request, "Invalid credentials, Please try again")
		print(messages.error(request, "Invalid credentials, Please try again"))
		return redirect('GenuVarum')

	# return HttpResponse('handleLogin')
	return render(request, 'GenuValgum.html')

def handleLogout(request):
	logout(request)
	messages.success(request, "Successfully Logged Out")
	return redirect('Homepage')

	return HttpResponse('handleLogout') 

	# return redirect('Homepage') 

	# logout(request)
	# return HttpResponseRedirect('Homepage')

# def UserProfile(request):
#     return render(request,'UserProfile.html')


#Forget password
def fpass(request):
    if request.method == 'POST':
        username = request.POST['username']
        user = User.objects.get(username=username)
        # print(user.check_password("admin"))
        profile = Profile.objects.get(user=user)
        user_email = user.email
        print(user_email)
        ftoken = profile.forget_token
        mail_message = f'Hey Your Reset Password Link is http://127.0.0.1:8000/changepass/{ftoken}/'
        send_mail('Password Reset Request',mail_message,settings.EMAIL_HOST_USER,[user_email],fail_silently=False)
        messages.success(request,'MAIL SEND')
    return render(request,'forgetpassword.html')

# #Change Password
def changepassword(request,id):
    if request.method == 'POST':
        password = request.POST['password']
        profile = Profile.objects.get(forget_token=id).user
        user = User.objects.get(username=profile)
        user.set_password(password)
        user.save()
        messages.success(request,'Password Changed Please Login! ')
        return redirect('Homepage')
    return render(request,'changepassword.html')

def gen(camera):
	while True:
		frame = camera.estimate_vid()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
	return StreamingHttpResponse(gen(VideoImgManager()),
					content_type='multipart/x-mixed-replace; boundary=frame')



def image_det(body_detect):
	while True:
		frame = body_detect.estimate_vid()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		if cv.waitKey(5000) :break
			

def image_feed(request):
	return StreamingHttpResponse(image_det(VideoImgManagers()),
					content_type='multipart/x-mixed-replace; boundary=frame')

					
# def live_Res(request):
#     if request.method == 'POST':
#     	username = request.POST.get('username')
# 	   	LiveRes1 = request.POST.get('LiveRes1')
# 	   	LiveRes2 = request.POST.get('LiveRes2')
# 	   	live_Res = liveResult(user=username,LiveRes1=LiveRes1,LiveRes2=LiveRes2,date=datetime.today())
# 	   	live_Res.save()
    
#     return render(request, 'Detection_Live.html')  

def Detection_img(request):
	if request.method == "POST":
		username = request.POST['username']
		imgRes1 = request.POST['imgRes1']
		imgRes2 = request.POST['imgRes2']
		print(imgRes1,imgRes2)
		
		img_Result = imageResult(user=username,imgRes1=imgRes1,imgRes2=imgRes2,date=datetime.today())
		img_Result.save()
		messages.success(request,'Stored successfully') 
	
	return render(request, 'Detection_img.html') 
 

def Hospitals(request):
	return render(request,'Hospitals.html')