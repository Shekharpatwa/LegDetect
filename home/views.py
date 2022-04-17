from django.shortcuts import render, HttpResponse,redirect
from django.http.response import StreamingHttpResponse

from home.camera import VideoImgManager
from home.body_detect import VideoImgManagers
from datetime import datetime
from django.contrib.auth import authenticate, login, logout	
from django.contrib.auth.models import User
from django.contrib import messages
from .models import LiveRes
from .models import ImageRes
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
import uuid
from .models import Prof

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

def page1(request):
    return render(request,'page1.html')

def page2(request):
    return render(request,'page2.html')

def page3(request):
    return render(request,'page3.html')

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
			print(messages.error(request, 'Username must be under 10 character'))
			return redirect('Homepage')
		
		#Username should be alphanumeric
		if not username.isalnum():
			messages.error(request, 'Username should only contain letters and numbers')
			print(messages.error(request, 'Username should only contain letters and numbers'))
			return redirect('Homepage')

		if len(pass1) <8:
			messages.error(request, 'Password must be greater than 8 or equal to 8 charaters')
			print(messages.error(request, 'Password must be greater than 8 or equal to 8 charaters'))
			return redirect('Homepage')

		if len(pass1) >15:
			messages.error(request, 'Password must not be greater 15 characters')
			print(messages.error(request, 'Password must not be greater 15 characters'))
			return redirect('Homepage')

	
		# #password should match
		if pass1 != pass2:
			messages.error(request, 'Passwords do not match')
			print(messages.error(request, 'Passwords do not match'))
			return redirect('Homepage')
			
		

		data=User.objects.all()
		y=0
		for j in data:
			if j.username==username:
				y=1
				break
		if y==1:
			messages.error(request,"Username already exists")
			print(messages.error(request,"Username already exists"))
			return redirect("Homepage.html")

		data=User.objects.all()
		z=0
		for i in data:
			if i.email==email:
				z=1
				break
		if z==1:
			messages.error(request,"Email already exists")
			print(messages.error(request,"Email already exists"))
			return redirect("Homepage.html")


		# #Create the User
		myuser = User.objects.create_user(username,email,pass1)
		# myuser.first_name = fname
		

		myuser.save()

		
		messages.success(request, 'Your account has been successfully created')
		print(messages.success(request, 'Your account has been successfully created'))

		return redirect('Homepage')

	else:	
		return HttpResponse('404 - Not found')


			
def handleLogin(request):
		# Get the POST parameters
	if request.method == "POST":
		loginusername = request.POST['loginusername']
		loginpassword = request.POST['loginpassword']
		

		
		user = authenticate(username=loginusername, password=loginpassword)
		
		ftoken = str(uuid.uuid4())
		
		profile = Prof.objects.create(user=user,forget_token=ftoken)

		if user is not None:
			login(request, user)
			messages.success(request, "Successfully Logged In")
			print(messages.success(request, "Successfully Logged In"))
			return redirect('Homepage')

		else:
			messages.error(request, "Invalid credentials, Please try again")
			print(messages.error(request, "Invalid credentials, Please try again"))
			return redirect('Homepage')

	# return HttpResponse('handleLogin')
	return render(request, 'GenuValgum.html')

def handleLogout(request):
	logout(request)
	messages.success(request, "Successfully Logged Out")
	print(messages.success(request, "Successfully Logged Out"))
	return redirect('Homepage')

	return HttpResponse('handleLogout') 



def UserProfile1(request):
	allresult = ImageRes.objects.all().filter(name = request.user)
	
	context = {'UserProfile1': allresult}
	
	return render(request,'UserProfile1.html',context)

def UserProfile2(request):
    allresult = LiveRes.objects.all().filter(name = request.user)
    context = {'UserProfile2': allresult}
    return render(request,'UserProfile2.html',context)

#Forget password
def fpass(request):
    if request.method == 'POST':
        username = request.POST['username']
        user = User.objects.get(username=username)
        # print(user.check_password("admin"))
        profile = Prof.objects.get(user=user)
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
        profile = Prof.objects.get(forget_token=id).user
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



def Detection_img(request):
	if request.method == "POST":
		name = request.POST['name']
		Langle = request.POST['Langle']
		Rangle = request.POST['Rangle']
		Result = ImageRes(name=name,ImgLeftAngle=Langle,ImgRightAngle=Rangle,date=datetime.today())
		Result.save()
		messages.success(request,'Stored successfully') 
	return render(request, 'Detection_img.html') 
 
def Detection_Live(request):
    if request.method == "POST":
    	name = request.POST['name']
    	Langle = request.POST['Langle']
    	Rangle = request.POST['Rangle']

    	Result = LiveRes(name=name,LiveLeftAngle=Langle,LiveRightAngle=Rangle,date=datetime.today())
    	Result.save()
    	messages.success(request,'Stored successfully') 
    	print(messages.success(request,'Stored successfully')) 

    return render(request,'Detection_Live.html')


def Hospitals(request):
	return render(request,'Hospitals.html')

def chartProfile1(request):
	allresult = ImageRes.objects.all().filter(name = request.user)
	context = {'chartProfile1': allresult}
	return render(request,'chartProfile1.html',context)

def chartProfile2(request):
    allresult = LiveRes.objects.all().filter(name = request.user)
    context = {'chartProfile2': allresult}
    return render(request,'chartProfile2.html',context)


