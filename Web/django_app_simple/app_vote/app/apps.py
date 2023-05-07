from django.apps import AppConfig
from django.apps import AppConfig
from keras.models import load_model
from django.conf import settings
import pickle
import os


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

class DigitrecappConfig(AppConfig):
    name = 'app'
    # loading model
    model_path = os.path.join(settings.MODELS, 'my_model.h5')
    digitmodel = load_model(model_path)


