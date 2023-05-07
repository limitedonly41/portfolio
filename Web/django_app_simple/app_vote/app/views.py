
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import keras

from django.views import generic
from .models import Choice, Question
from .forms import PredictForm

import tensorflow as tf
# import scipy.misc as sm

from skimage.transform import resize

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .apps import DigitrecappConfig
from rest_framework.decorators import api_view

import cv2
from PIL import Image, ImageGrab, ImageDraw
import os
import time
import requests
import json
import io
import numpy as np
from urllib.request import urlopen
import imageio
from PIL import Image
import requests
from io import BytesIO
import skimage




@api_view(["POST"])  # recieve the request
def getimagefromrequest(request):
    # if request.method == 'POST':
    # print('POST',request.data.get('image'))
    # body = json.loads(request.body)
    image = request.FILES.get("file")
    print("image:", type(image))
    print("image:", type(image.file))
    # print("image:", type(image.read()))

    image_bytes = image.read()
    # final_image = np
    # print('hello')
    digit, acc = classify_handwriting(image_bytes)
    print(str(digit))
    return JsonResponse({"digit": str(digit), "acc": str(acc)})
 
 
def classify_handwriting(image):
    # print('image type:',type(image))
    # img = np.array(image)
    img = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
    # print('decoded', img)
    print()
    
    # converting to grayscale
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        img2 = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # print('\n'*3)
    # print(gray.shape)
    # print('\n'*3)
    # apply otsu thresholding
    ret, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV, cv2.THRESH_OTSU)
    # find the contours
    contours = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    for cnt in contours:
        # get bounding box and exact region of interest
        x, y, w, h = cv2.boundingRect(cnt)
        # create rectangle
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)
        top = int(0.05 * th.shape[0])
        bottom = top
        left = int(0.05 * th.shape[1])
        right = left
        th_up = cv2.copyMakeBorder(th, top, bottom, left, right, cv2.BORDER_REPLICATE)
        # Extract the image's region of interest
        roi = th[y - top : y + h + bottom, x - left : x + w + right]
        digit, acc = predict_digit(roi)
        return digit, acc


def predict_digit(img):

    print('\n'*3)
    print(img.shape)
    print('\n'*3)
    # resize image to 28x28 pixels
    img = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)
    # cv2.imshow("img", img)
    img = img.reshape(28, 28, 1)
    # normalizing the image to support our model input
    img = img / 255.0
    #   img=img.convert('L')
    #   img=np.array(img)
    #   print(img)
    # reshaping to support our model and normalizing
    #   img=img.reshape(1,28,28,1)
    #   img=img/255.0
    #   print(img.size)
    #   temp=np.array(img)
    #   flat=temp.ravel()
    #   print(flat.size)
    # predicting the class
    res = DigitrecappConfig.digitmodel.predict([img])[0]
    print('\n'*3)
    print(img.shape)
    print(DigitrecappConfig.digitmodel.predict([img]))
    return np.argmax(res), max(res)




def predict_form(request):
    form = PredictForm(request.POST or None)
    result = None
    if form.is_valid():
        url = form.cleaned_data['url']
                            


        # url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTEcUX7z4NKVR2xR8ndWZXf0ajJIzX7enrF9tvIBoQRH85TRfnl&s'


        image = skimage.io.imread( url )
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = resize(image, (28, 28))

        image = np.expand_dims(image, axis=0)



        result = predict_image(image)
        print('\n'*3)
        print(result)
        print('\n'*3)
        form.save()
                
	# return HttpResponseRedirect(reverse('predict_form', kwargs={'form':form, 'prediction':result}))

    return render(request, 'predict.html', {'form':form, 'prediction':result})


def predict_image(img):
    classes = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]

    model = tf.keras.models.load_model('app/models/fashion_best.h5')


    probability_model = tf.keras.Sequential([model, 
                                            tf.keras.layers.Softmax()])
    prediction = probability_model.predict(img)



    return classes[np.argmax(prediction[0])]








class IndexView(generic.ListView):
    template_name = 'index.html'
    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:3]
    

class DetailView(generic.DetailView):
    model = Question
    template_name = 'detail.html'

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'result.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'detail.html', {
            'question': question,
            'error_message': "Вы не выбрали ответ.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('results', args=(question.id,)))