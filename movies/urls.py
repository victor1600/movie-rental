from django.urls import path
from movies import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'', views.MovieViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/availability', views.SetAvailability.as_view()),
    path('<int:pk>/like', views.LikeMovieView.as_view()),
    path('<int:pk>/dislike', views.DislikeMovieView.as_view()),
    path('rent', views.RentListView.as_view()),
    path('<int:pk>/rent', views.RentView.as_view()),
    path('return/<int:pk>', views.ReturnView.as_view()),
    path('<int:pk>/sell', views.SellView.as_view()),
    path('sell', views.SellListView.as_view()),
    path('logs', views.MovieChangesLogView.as_view()),
]
