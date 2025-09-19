from django.urls import path
from .views import SubmitData

urlpatterns = [
    path('submitData/', SubmitData.as_view(), name='submit-data'),
]
