from django.shortcuts import render, HttpResponse, redirect
from django.http.response import StreamingHttpResponse
from home.frameoperations import FrameOperations
from home.poseEstimator import PoseEstimator
from home.camera import VideoImgManager
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

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
    return render(request,'Detection.html')

def handleSignup(request):
    #Get the POST parameters
	if request.models == "POST":
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		cpassword = request.POST['cpassword']

		#check for errorneous inputs

			#Username must be under 10 character
		if len(username) > 10:
			messages.error(request, 'Username must be under 10 characters')
			return redirect('Homepage')

		#Username should be alphanumeric
		if not username.isalnum():
			messages.error(request, 'Username should only contain letters and numbers')
			return redirect('Homepage')
			
	 	#password should match
		 if password != cpassword:
    		messages.error(request, 'Passwords do not match')
			return redirect('Homepage')
			
		# Create the User
		myuser = User.objects.create_user(username,email,password)
		myuser.save()
		messages.success(request,'Your account has been successfully created')
		# return redirect('Homepage')
		return redirect('GenuValgum')

	else:
    	return HttpResponse('404 - Not found')

def handleLogin(request):
    	#Get the POST Parameters
	if request.method == "POST":
    	loginusername = request.POST['loginusername']
		loginpassword = request.POST['loginpassword']

		user =  authenticate(username=loginusername, password=loginpassword)

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
	messages.success(request, 'Sucessfully Logged Out')
	return redirect('Homepage')

	return HttpResponse('handleLogout')

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
