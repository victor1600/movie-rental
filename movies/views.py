from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from django.http import Http404
from rest_framework.response import Response
from rest_framework import status, mixins, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Movie, LikeHistory, Rent, Sell, MovieChangesLog
from .serializers import MovieSerializer, LikeHistorySerializer, RentSerializer, SellSerializer, \
    MovieChangesLogSerializer


class MovieViewSet(ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    filterset_fields = ['availability']
    search_fields = ['title']
    # TODO: Review if code isnt broken.
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'likes']

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Movie.objects.filter(availability=True)
        return Movie.objects.all()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action not in ['list', 'retrieve']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


class SetAvailability(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk, format=None):
        if not request.data.get('availability'):
            raise ValidationError({'availability': ['You have to set a valid availability value']})
        try:
            user = Movie.objects.get(pk=pk)
        except Movie.DoesNotExist:
            raise Http404
        serializer = MovieSerializer(user, data={'availability': request.data.get('availability')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeMovieView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            movie = Movie.objects.get(pk=pk, availability=True)
            user = self.request.user
        except Movie.DoesNotExist:
            raise Http404

        try:
            like_history = LikeHistory.objects.get(movie=movie, user=user)
        except LikeHistory.DoesNotExist:
            like_history = LikeHistory(movie=movie, user=user)
            serializer = LikeHistorySerializer(like_history, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                movie.likes += 1
                movie.save()
        return Response(status=status.HTTP_200_OK)


class DislikeMovieView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            movie = Movie.objects.get(pk=pk, availability=True)
            user = self.request.user
        except Movie.DoesNotExist:
            raise Http404

        try:
            like_history = LikeHistory.objects.get(movie=movie, user=user)
            like_history.delete()
            movie.likes -= 1
            movie.save()
        except LikeHistory.DoesNotExist:
            pass
        return Response(status=status.HTTP_200_OK)


class ReturnView(mixins.UpdateModelMixin, APIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            rent = Rent.objects.get(pk=pk, returned=False)
        except Rent.DoesNotExist:
            raise Http404
        serializer = RentSerializer(rent, data={'returned': True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Updating movie stock
            movie = rent.movie
            quantity = rent.quantity
            movie.alter_stock(quantity)
            movie.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RentListView(generics.ListAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = (IsAuthenticated,)


class RentView(mixins.UpdateModelMixin, APIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            movie = Movie.objects.get(pk=pk, availability=True)
            quantity = request.data.get('quantity')
            if not quantity:
                raise ValidationError({'quantity': ['You have to set a valid quantity value']})
            if not movie.check_movie_stock(quantity):
                raise ValidationError({'quantity': ['There are not enough movie copies to rent.']})
            quantity = int(quantity)
            user = self.request.user
        except Movie.DoesNotExist:
            raise Http404
        rent = Rent(movie=movie, user=user)
        serializer = RentSerializer(rent, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Updating movie stock
            movie.alter_stock(-quantity)
            movie.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellView(mixins.UpdateModelMixin, APIView):
    queryset = Sell.objects.all()
    serializer_class = SellSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            movie = Movie.objects.get(pk=pk, availability=True)
            quantity = request.data.get('quantity')
            if not quantity:
                raise ValidationError({'quantity': ['You have to set a valid quantity value']})
            if not movie.check_movie_stock(quantity):
                raise ValidationError({'quantity': ['There are not enough movie copies to sell.']})
            quantity = int(quantity)
            user = self.request.user
        except Movie.DoesNotExist:
            raise Http404
        sell = Sell(movie=movie, user=user)
        serializer = SellSerializer(sell, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Updating movie stock
            movie.alter_stock(-quantity)
            movie.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellListView(generics.ListAPIView):
    queryset = Sell.objects.all()
    serializer_class = SellSerializer
    permission_classes = (IsAuthenticated,)


class MovieChangesLogView(generics.ListAPIView):
    queryset = MovieChangesLog.objects.all()
    serializer_class = MovieChangesLogSerializer
    permission_classes = (IsAdminUser,)
