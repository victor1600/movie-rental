from django.contrib.auth.models import User

# Create your views here.
from django.http import Http404

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class UserCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class SetAdminState(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk, format=None):
        if not request.data.get('is_staff'):
            raise ValidationError({'is_staff': ['You have to set a valid is_staff value']})
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
        serializer = UserSerializer(user, data={'is_staff': request.data.get('is_staff')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh = request.data["refresh"]
            token = RefreshToken(refresh)
            token.blacklist()

            return Response("Successful Logout. Token was blacklisted and cant be refreshed anymore",
                            status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            # TODO: Add serializer validation for refresh parameter.
            return Response("Couldn't logout.", status=status.HTTP_400_BAD_REQUEST)
