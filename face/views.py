from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import base64
import cv2
import face_recognition
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
User = get_user_model()


from .models import *

def index(request):
    return render(request, "face/index.html")


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        
        # Debugging information
        print(f"Attempting login with username: {username} and password: {password}")
        
        user = authenticate(request, username=username, password=password)
        
        # Debugging information
        print(f"Authenticated user: {user}")

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "face/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "face/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

from .models import UserPhoto  # import the model

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        photo = request.FILES.get("photo")  # get the uploaded photo

        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()

            if photo:
                if not photo.name.lower().endswith(".jpg"):
                    return render(request, "face/register.html", {
                        "message": "Only JPG format is allowed for the photo."
                    })
                # Save photo
                UserPhoto.objects.create(user=user, photo=photo)

        except IntegrityError:
            return render(request, "face/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "face/register.html")



import base64
import cv2
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import base64
import json
import numpy as np
import cv2
import face_recognition
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def recognize(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            image_data = data.get('image')

            if not image_data:
                return JsonResponse({"result": "No image data received."}, status=400)

            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            captured_encoding = face_recognition.face_encodings(rgb_img)

            if not captured_encoding:
                return JsonResponse({"result": "No face found in captured image."}, status=400)

            # Load known image
            known_path = os.path.join('path_to_your_known_image', 'known_face.jpg')  # Adjust path
            known_img = cv2.imread(known_path)

            if known_img is None:
                return JsonResponse({"result": "Known image not found."}, status=500)

            rgb_known = cv2.cvtColor(known_img, cv2.COLOR_BGR2RGB)
            known_encoding = face_recognition.face_encodings(rgb_known)

            if not known_encoding:
                return JsonResponse({"result": "No face found in known image."}, status=400)

            result = face_recognition.compare_faces([known_encoding[0]], captured_encoding[0])

            if result[0]:
                return JsonResponse({"result": "Image matched ✅"})
            else:
                return JsonResponse({"result": "Image does not match ❌"})

        except Exception as e:
            return JsonResponse({"result": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"result": "Invalid request method."}, status=400)


import base64
import cv2
import numpy as np
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import UserPhoto, Subject, Student

@csrf_exempt
def recognize_and_mark(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        image_data = data.get('image')
        username = request.user.username
        subject_topic = data.get('subject')  # You must send this from frontend

        if not image_data:
            return JsonResponse({'status': 'fail', 'message': 'No image data'})

        # Decode base64 to OpenCV image
        image_data = image_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        captured_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Get registered photo
        try:
            user_photo_path = request.user.userphoto.photo.path
            reg_img = cv2.imread(user_photo_path)
        except:
            return JsonResponse({'status': 'fail', 'message': 'No registered photo found'})

        # Face recognition comparison
        try:
            enc1 = face_recognition.face_encodings(cv2.cvtColor(reg_img, cv2.COLOR_BGR2RGB))[0]
            enc2 = face_recognition.face_encodings(cv2.cvtColor(captured_img, cv2.COLOR_BGR2RGB))[0]
        except IndexError:
            return JsonResponse({'status': 'fail', 'message': 'Face not detected in one of the images'})

        match = face_recognition.compare_faces([enc1], enc2)[0]

        if match:
            subject, _ = Subject.objects.get_or_create(topic=subject_topic, date=timezone.now())
            Student.objects.create(username=request.user, detail=subject)
            return JsonResponse({'status': 'success', 'message': 'Attendance marked'})
        else:
            return JsonResponse({'status': 'fail', 'message': 'Face does not match'})

    return JsonResponse({'status': 'fail', 'message': 'Invalid request'})

from django.contrib.auth.decorators import login_required

@login_required
def attendance_history(request):
    records = Student.objects.filter(username=request.user).select_related('detail').order_by('-detail__date')
    return render(request, "face/attendance_history.html", {"records": records})

