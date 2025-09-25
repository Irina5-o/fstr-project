from django.urls import path
from .views import SubmitData, PerevalRetrieveUpdateView

urlpatterns = [
    path('submitData/', SubmitData.as_view(), name='submit-data'),
    path('submitData/<int:pk>/', PerevalRetrieveUpdateView.as_view(), name='submit-data-detail'),
]