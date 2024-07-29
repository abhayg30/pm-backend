from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
import requests
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsApproved, IsStudent, IsSupervisor, Isowner, IsPartnerOrSupervisor, IsPartner
from rest_framework import status
from .serializers import CreateCommentLogSerializer, ViewCommentLogSerializer
import json
from .models import CommentLogDetails
from rest_framework import generics
from django.forms.models import model_to_dict
from datetime import date, datetime

# creates comment object on progress logs
class CreateCommentOnLog(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]
    def post(self, request, format = None):
        data = request.data
        if data['user'] != request.user.id:
            return Response({'errors': 'Unauthorised user'}, status=status.HTTP_401_UNAUTHORIZED)
        key_list = tuple(request.data.keys())
        serializer = CreateCommentLogSerializer(data = request.data, fields = key_list)
        if serializer.is_valid(raise_exception = True):
            project = serializer.save()
            return Response({'msg': 'Comment created successfully'}, status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)
    
# returns comments by a specific project ID         
class ViewCommentLogsByProjectID(APIView):
    permission_classes = [IsAuthenticated, IsPartnerOrSupervisor]
    def get(self, request, pk,format = None):
        try:
            all_project = CommentLogDetails.objects.filter(job_id = pk).order_by('-id')
            serialized_data = ViewCommentLogSerializer(all_project, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# returns comments by a specific progress log ID 
class ViewCommentLogsByProgressLogID(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,pk ,format = None):
        try:
            all_project = CommentLogDetails.objects.filter(progLogParent_id = pk).order_by('-id')
            serialized_data = ViewCommentLogSerializer(all_project, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# updates comments made by a specific owner 
class UpdateComment(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsSupervisor]
    queryset = CommentLogDetails.objects.all()
    def update(self, request, pk, *args, **kwargs):
        comment = get_object_or_404(CommentLogDetails, id = pk)
        if comment.user_id != request.user.id:
            return Response({'errors':'Not Authorized'}, status=status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        serializer = ViewCommentLogSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Comment updated successfully"}, status.HTTP_200_OK)

        else:
            return Response({"message": "failed", "details": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        
# deletes progress log objs made by a specific owner 
class DeleteComment(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsSupervisor]
    queryset = CommentLogDetails.objects.all()
    def destroy(self, request, pk, *args, **kwargs):
        user_id = get_object_or_404(CommentLogDetails, id = pk).user_id
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