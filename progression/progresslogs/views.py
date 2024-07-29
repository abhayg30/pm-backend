from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
import requests
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsApproved, IsStudent, IsSupervisor, Isowner, IsPartnerOrSupervisor, IsPartner
from rest_framework import status
from .serializers import CreateProgressLogSerializer, ViewProgressLogSerializer
import json
from .models import ProgressLogDetails
from rest_framework import generics
from django.forms.models import model_to_dict
from datetime import date, datetime

# creates a progress log obj
class CreateProgressLog(APIView):
    """Used to get progress logs for a project

    Args:
        APIView (POST)

    Returns:
        return 200, 400
    """
    permission_classes = [IsAuthenticated, IsStudent]
    def post(self, request, format = None):
        data = request.data
        if data['user'] != request.user.id:
            return Response({'errors': 'Unauthorised user'}, status=status.HTTP_401_UNAUTHORIZED)
        key_list = tuple(request.data.keys())
        serializer = CreateProgressLogSerializer(data = request.data, fields = key_list)
        if serializer.is_valid(raise_exception = True):
            project = serializer.save()
            return Response({'msg': 'Log created successfully'}, status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)

# returns progress log objs made by a specific student
class ViewProgressLogsByStudentId(APIView):
    """Used to get progress logs by a student

    Args:
        APIView (GET)

    Returns:
        return JSON, where each object is a progress log filtered by studentID
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            all_project = ProgressLogDetails.objects.filter(user_id = pk).order_by('-id')
            serialized_data = ViewProgressLogSerializer(all_project, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# returns progress log objs made by a specific project        
class ViewProgressLogsByProjectID(APIView):
    """Used to get progress logs for a project

    Args:
        APIView (GET)

    Returns:
        return JSON, where each object is a progress log filtered by project ID
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            all_project = ProgressLogDetails.objects.filter(job_id = pk).order_by('-id')
            serialized_data = ViewProgressLogSerializer(all_project, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# updates progress log objs made by a specific owner    
class UpdateProgressLog(generics.UpdateAPIView):
    """Used to update progress logs by a student

    Args:
        APIView (PUT)

    Returns:
        updates logs. returns 200, 400
    """
    permission_classes = [IsAuthenticated, IsStudent]
    queryset = ProgressLogDetails.objects.all()
    def update(self, request, pk, *args, **kwargs):
        progresslog = get_object_or_404(ProgressLogDetails, id = pk)
        if progresslog.user_id != request.user.id:
            return Response({'errors':'Not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        serializer = ViewProgressLogSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Progress Log updated successfully"}, status.HTTP_200_OK)

        else:
            return Response({"message": "failed", "details": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        
# deletes progress log objs made by a specific owner 
class DeleteProgressLog(generics.DestroyAPIView):
    """Used to delete progress logs by a student

    Args:
        APIView (DELETE)

    Returns:
        delete status, 401, 200,400
    """
    permission_classes = [IsAuthenticated, IsStudent]
    queryset = ProgressLogDetails.objects.all()
    def destroy(self, request, pk, *args, **kwargs):
        user_id = get_object_or_404(ProgressLogDetails, id = pk).user_id
        if request.user.id != user_id:
            return Response({'message':"Not authorized"}, status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        try:
            instance.delete()
            return Response({'message':"Successfully deleted"}, status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)
        

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))