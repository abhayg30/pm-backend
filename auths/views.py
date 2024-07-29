from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from django.http.response import JsonResponse
from django.core import serializers
from rest_framework.views import APIView
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserChangePasswordSerializer,
    SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer,
    UserLogoutSerializer,
    UpdateProfileSerializer,
)
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import json
from .permissions import Isowner, IsApproved
from datetime import datetime
from .models import User, UserDetails

# User Registration view
class UserRegistrationView(APIView):
    """Registration for user

    Args:
        APIView (POST): Persist details entered by the user in DB
    """
    def post(self, req, format=None):
        serializer = UserRegistrationSerializer(data=req.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            try:
                userDetailFunction(req)
            except Exception as e:
                return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            token = get_tokens_for_user(user)
            return Response(
                {"token": token, "msg": "Registration Successful"},
                status.HTTP_201_CREATED,
            )
        return Response({"errors": str(serializer.errors)}, status.HTTP_400_BAD_REQUEST)


# User Login Functionality
class UserLoginView(APIView):
    """Secure login functionality for user

    Args:
        APIView (POST)
    """
    def post(self, req, format=None):
        serializer = UserLoginSerializer(data=req.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                response = Response()
                response.data = {
                    "refresh": token.get("refresh"),
                    "access": token.get("access"),
                }
                return Response(
                    {"token": token, "msg": "login successful"}, status.HTTP_200_OK
                )
            else:
                return Response(
                    {"errors": "Email or Password is not valid"},
                    status.HTTP_404_NOT_FOUND,
                )


# User profile View
class UserProfileView(APIView):
    """Gives the details about the user -- for profile page

    Args:
        APIView (GET): fetch details of the user from DB

    Returns:
        json of user's data
    """
    permission_classes = [IsAuthenticated, IsApproved]

    def get(self, req, format=None):
        try:
            user_details = UserDetails.objects.get(user_id=req.user.id)
            response_data = UserProfileSerializer(user_details)
            new_data = response_data.data
            new_data["user_type"] = req.user.user_type
            return Response(new_data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": str(e)}, status.HTTP_400_BAD_REQUEST)

# Logout User
class UserLogoutView(APIView):
    """Secure logout for the user

    Args:
        APIView (POST): blacklisting the token

    Returns:
        HTTP CODE 204
    """
    permission_classes = [IsAuthenticated, IsApproved]

    def post(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

# Update user profile
class UpdateProfile(generics.UpdateAPIView):
    """Update user profile -- can be done by the owner

    Args:
        generics (UPDATE or PUT): change information about the user

    Returns:
       success and error messages with 200 OK and 400 BAD REQUEST HTTP Codes respectively
    """
    permission_classes = [IsAuthenticated, Isowner, IsApproved]
    serializer_class = UpdateProfileSerializer

    def update(self, request, *args, **kwargs):
        user_id = request.user.id
        user_detail = get_object_or_404(UserDetails, user_id=user_id)
        serializer = self.get_serializer(user_detail, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User details updated successfully"}, status.HTTP_200_OK
            )

        else:
            return Response(
                {"message": "failed", "details": serializer.errors},
                status.HTTP_400_BAD_REQUEST,
            )

# Util function to store in UserDetails Table
def userDetailFunction(req):
    user = User.objects.filter(email=req.data.get("email")).first()
    user_id = user.id
    userDetails = UserDetails()
    userDetails.user_id = user_id
    userDetails.city = req.data.get("city")
    userDetails.working_rights = req.data.get("working_rights")
    userDetails.gender = req.data.get("gender")
    userDetails.zip_code = int(req.data.get("zip_code"))
    userDetails.first_name = req.data.get("first_name")
    userDetails.last_name = req.data.get("last_name")
    date = datetime.strptime(str(req.data.get("date_of_birth")), "%Y-%m-%d")
    userDetails.date_of_birth = date
    userDetails.save()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh["email"] = user.email
    refresh["status"] = user.status
    refresh["user_type"] = user.user_type
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }