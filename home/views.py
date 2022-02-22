from django.shortcuts import render, HttpResponse,redirect
from django.http.response import StreamingHttpResponse
from home.frameoperations import FrameOperations
from home.poseEstimator import PoseEstimator
from home.camera import VideoImgManager
from datetime import datetime
from django.contrib.auth import authenticate, login, logout	
from django.contrib.auth.models import User
from django.contrib import messages

from django.conf import settings
from django.core.mail import send_mail
import uuid
from .models import Profile

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

def Detection(request):
	if request.user.is_anonymous:
		return redirect(request,'/Login')
	return render(request,'Detection.html')



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
			

		#Create the User
		myuser = User.objects.create_user(username,email,pass1)
		# myuser.first_name = fname
		myuser.save()

		messages.success(request, 'Your account has been successfully created')

		ftoken = str(uuid.uuid4())

		profile = Profile.objects.create(user=user,forget_token=ftoken)

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

#Change Password
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

def frame_feed(request):
	return StreamingHttpResponse(gen(FrameOperations()),
					content_type='multipart/x-mixed-replace; boundary=frame')

def pose_feed(request):
	return StreamingHttpResponse(gen(PoseEstimator()),
					content_type='multipart/x-mixed-replace; boundary=frame')


def video_feed(request):
	return StreamingHttpResponse(gen(VideoImgManager()),
					content_type='multipart/x-mixed-replace; boundary=frame')
