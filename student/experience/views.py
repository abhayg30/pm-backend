from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
import requests
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsApproved, IsStudent, IsSupervisor, Isowner, IsPartnerOrSupervisor, IsStudentOrSupervisor
from rest_framework import status
from .serializers import CreateExperienceSerializer, ViewExperienceSerializer
import json
from .models import ExperienceDetails
from rest_framework import generics
from django.forms.models import model_to_dict
from datetime import date, datetime

class CreatExperience(APIView):
    """Create new previous experiences -- functionality for both student and supervisor

    Args:
        APIView (POST): persist into DB

    Returns:
        201: sucessfully created, CREATED
        401: UNAUTHORIZED
        400: BAD REQUEST
    """
    permission_classes = [IsAuthenticated, Isowner, IsStudentOrSupervisor]
    def post(self, request, format = None):
        data = request.data
        if data['user'] != request.user.id:
            return Response({'errors': 'Unauthorised user'}, status=status.HTTP_401_UNAUTHORIZED)
        key_list = tuple(request.data.keys())
        serializer = CreateExperienceSerializer(data = request.data, fields = key_list)
        if serializer.is_valid(raise_exception = True):
            experience = serializer.save()
            return Response({'msg': 'Experience created successfully'}, status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)

class ViewExperiences(APIView):
    """View all experiences of an user -- student and supervisor can access

    Args:
        APIView (GET)

    Returns:
        list of object: model ExperienceDetails
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, format = None):
        try:
            all_experience = ExperienceDetails.objects.filter(user_id = request.user.id).order_by('-id')
            serialized_data = ViewExperienceSerializer(all_experience, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ViewSingleExperience(APIView):
    """View particular experience detail based id

    Args:
        APIView (GET)

    Returns:
        ExperienceDetails: object
    """
    permission_classes = [IsAuthenticated, Isowner, IsStudentOrSupervisor]
    def get(self, request, pk, format = None):

        experience = get_object_or_404(ExperienceDetails, id = pk, user_id = request.user.id)
        response_dict = model_to_dict(experience)
        response = json.loads(json.dumps(response_dict, indent=4, sort_keys=True, default=json_serial))
        return Response(response, status=status.HTTP_200_OK)  

class UpdateExperience(generics.UpdateAPIView):
    """Update Experience based on id

    Args:
        generics (PUT)

    Returns:
        401: UNAUTHORIZED
        200: OK
        400: BAD REQUEST
    """
    permission_classes = [IsAuthenticated, IsStudentOrSupervisor]
    queryset = ExperienceDetails.objects.all()
    def update(self, request, pk, *args, **kwargs):
        experience = get_object_or_404(ExperienceDetails, id = pk)
        if experience.user_id != request.user.id:
            return Response({'errors':'Not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        serializer = ViewExperienceSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Experience updated successfully"}, status.HTTP_200_OK)

        else:
            return Response({"message": "failed", "details": serializer.errors}, status.HTTP_400_BAD_REQUEST)

class DeleteExperience(generics.DestroyAPIView):
    """Delete a particular experience

    Args:
        generics (DESTROY or DELETE)

    Returns:
        401: UNAUTHORIZED
        204: NO CONTENT
        400: BAD REQUEST

    """
    permission_classes = [IsAuthenticated, IsStudentOrSupervisor]
    queryset = ExperienceDetails.objects.all()
    def destroy(self, request, pk, *args, **kwargs):
        user_id = get_object_or_404(ExperienceDetails, id = pk).user_id
        if request.user.id != user_id:
            return Response({'message':"Not authorized"}, status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        try:
            instance.delete()
            return Response({'message':"Successfully deleted"}, status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)

class DisplayUserExperience(APIView):
    """Display user's experience -- for partner or supervisor

    Args:
        APIView (GET)

    Returns:
        list: object of type ExperienceDetails
    """
    permission_classes = [IsAuthenticated, IsPartnerOrSupervisor]
    def get(self, request, format = None):
        user_id = request.data.get('user_id')
        try:
            all_education = ExperienceDetails.objects.filter(user_id = user_id).order_by('-id')
            serialized_data = ViewExperienceSerializer(all_education, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#util function for json serializing an object
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))