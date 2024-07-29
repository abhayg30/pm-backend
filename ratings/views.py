from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
import requests
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsApproved, IsStudent, IsSupervisor, Isowner, IsPartnerOrSupervisor, IsPartner
from rest_framework import status
from .serializers import CreateRatingDetailsSerializer, ViewRatingDetailsSerializer
import json
from .models import RatingDetails
from rest_framework import generics
from django.forms.models import model_to_dict
from datetime import date, datetime


# Create your views here.
# creates a rating obj
class CreateRatingDetails(APIView):
    """Used to create ratings at end of a project

    Args:
        APIView (PUT)

    Returns:
        return 200, 400
    """
    permission_classes = [IsAuthenticated, IsPartnerOrSupervisor]
    def put(self, request, format = None):
        data = request.data
        if data['user'] != request.user.id:
            return Response({'errors': 'Unauthorised user'}, status=status.HTTP_401_UNAUTHORIZED)
        key_list = tuple(request.data.keys())
        serializer = CreateRatingDetailsSerializer(data = request.data, fields = key_list)
        if serializer.is_valid(raise_exception = True):
            project = serializer.save()
            return Response({'msg': 'Rating created successfully'}, status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)

# returns all ratings given to a user
class ViewRatingDetailsByRatedOn(APIView):
    """Used to get Ratings given to a student/supervisor

    Args:
        APIView (GET)

    Returns:
        return JSON, where ratings are filtered by rated ON. Ratings given to a student/supervisor
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk,format = None):
        try:
            all_project = RatingDetails.objects.filter(ratingOn_id = pk).order_by('-id')
            serialized_data = ViewRatingDetailsSerializer(all_project, many = True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)



def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))