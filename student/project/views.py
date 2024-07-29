from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
import requests
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsApproved, IsStudent, IsSupervisor, Isowner, IsPartnerOrSupervisor, IsStudentOrSupervisor
from rest_framework import status
from .serializers import CreateProjectSerializer, ViewProjectSerializer
import json
from .models import ProjectDetails
from rest_framework import generics
from django.forms.models import model_to_dict
from datetime import date, datetime


# Create your views here.

class CreateProject(APIView):
    """Create new previous projects -- functionality for both student and supervisor

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
        serializer = CreateProjectSerializer(data = request.data, fields = key_list)
        if serializer.is_valid(raise_exception = True):
            project = serializer.save()
            return Response({'msg': 'Project created successfully'}, status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)

class ViewProjects(APIView):
    """View all previous projects of an user -- student and supervisor can access

    Args:
        APIView (GET)

    Returns:
        list of object: model ProjectDetails
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, format = None):
        try:
            all_project = ProjectDetails.objects.filter(user_id = request.user.id).order_by('-id')
            serialized_data = ViewProjectSerializer(all_project, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ViewSingleProject(APIView):
    """View particular previous project detail based id

    Args:
        APIView (GET)

    Returns:
        ProjectDetails: object
    """
    permission_classes = [IsAuthenticated, Isowner, IsStudentOrSupervisor]
    def get(self, request, pk, format = None):
        project = get_object_or_404(ProjectDetails, id = pk, user_id = request.user.id)
        response_dict = model_to_dict(project)
        response = json.loads(json.dumps(response_dict, indent=4, sort_keys=True, default=json_serial))
        return Response(response, status=status.HTTP_200_OK)  

class UpdateProject(generics.UpdateAPIView):
    """Update previous project based on id

    Args:
        generics (PUT)

    Returns:
        401: UNAUTHORIZED
        200: OK
        400: BAD REQUEST
    """
    permission_classes = [IsAuthenticated, IsStudentOrSupervisor]
    queryset = ProjectDetails.objects.all()
    def update(self, request, pk, *args, **kwargs):
        project = get_object_or_404(ProjectDetails, id = pk)
        if project.user_id != request.user.id:
            return Response({'errors':'Not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        serializer = ViewProjectSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Project updated successfully"}, status.HTTP_200_OK)

        else:
            return Response({"message": "failed", "details": serializer.errors}, status.HTTP_400_BAD_REQUEST)

class DeleteProject(generics.DestroyAPIView):
    """Delete a particular previous project

    Args:
        generics (DESTROY or DELETE)

    Returns:
        401: UNAUTHORIZED
        204: NO CONTENT
        400: BAD REQUEST

    """
    permission_classes = [IsAuthenticated, IsStudentOrSupervisor]
    queryset = ProjectDetails.objects.all()
    def destroy(self, request, pk, *args, **kwargs):
        user_id = get_object_or_404(ProjectDetails, id = pk).user_id
        if request.user.id != user_id:
            return Response({'message':"Not authorized"}, status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        try:
            instance.delete()
            return Response({'message':"Successfully deleted"}, status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)

class DisplayUserProject(APIView):
    """Display user's previous projects -- for partner or supervisor

    Args:
        APIView (GET)

    Returns:
        list: object of type ProjectDetails
    """
    permission_classes = [IsAuthenticated, IsPartnerOrSupervisor]
    def get(self, request, format = None):
        user_id = request.data.get('user_id')
        try:
            all_project = ProjectDetails.objects.filter(user_id = user_id).order_by('-id')
            serialized_data = ViewProjectSerializer(all_project, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))