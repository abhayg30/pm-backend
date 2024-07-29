from django.urls import path, include
from .views import (
    CreateRatingDetails, ViewRatingDetailsByRatedOn
)


urlpatterns = [
    #ratings
    path('create/rating/', CreateRatingDetails.as_view(), name = 'create-rating'),
    path('view/rating/<int:pk>', ViewRatingDetailsByRatedOn.as_view(), name = 'view-rating-personnel'),
]