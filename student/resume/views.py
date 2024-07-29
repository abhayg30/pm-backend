from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
import requests
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsApproved, IsStudent, IsSupervisor, Isowner, IsPartnerOrSupervisor, IsStudentOrSupervisor
from rest_framework import status
import json
from .models import UploadResume, ResumeData
from industry.models import JobDescription
from rest_framework import generics
from django.forms.models import model_to_dict
from datetime import date, datetime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import ResumeData
from powerpuff import settings
import boto3
s3 = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)

class UploadResumeView(APIView):
    """Upload resume -- pdf file accepted -- access for student and supervisor only

    Args:
        APIView (PUT): One user can have one resume at a time

    Returns:
        201: CREATED
        400: BAD REQUEST
        url: S3 url of the resume
    """
    permission_classes = [IsAuthenticated, IsStudentOrSupervisor, IsApproved]
    def put(self, request, format=None):
        print(request.FILES)
        try:
            upload = UploadResume.objects.get(user_id = request.user.id)
        except UploadResume.DoesNotExist:
            upload = None
        if upload == None:
            resume = request.FILES.get('pdf_file')
            # file_name = resume.name
            try:
                upload = UploadResume(resume = resume)
                upload.user_id = request.user.id
                upload.save()
                s3_url = upload.resume.url
                name = upload.resume
                resume_instance = resumeDetails(request=request, s3_url=s3_url, new_user=True)
                new_url = generateLongExpirationURL(name)
                resume_instance.url = new_url
                resume_instance.save()
                return Response({'message': 'File uploaded to S3', 'url': new_url}, status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)
        elif upload != None:
            resume = request.FILES['pdf_file']
            try:
                upload.resume = resume
                upload.save()
                s3_url = upload.resume.url
                resume_instance = resumeDetails(request=request, s3_url=s3_url, new_user=False)
                name = upload.resume
                new_url = generateLongExpirationURL(name)
                resume_instance.url = new_url
                resume_instance.save()
                return Response({'message': 'File uploaded to S3', 'url': new_url}, status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)

class ViewResume(APIView):
    """View resume

    Args:
        APIView (GET): fetch from DB and S3

    Returns:
        url: url of uploaded resume
        200: OK
        400: BAD REQUEST
    """
    permission_classes = [IsAuthenticated, IsApproved]
    def get(self, request, format = None):
        user_id = request.user.id 
        try:
            resume_instance = UploadResume.objects.get(user_id = user_id)
        except UploadResume.DoesNotExist:
            resume_instance = None
        if resume_instance == None:
            return Response({'message': 'You have not uploaded your resume yet'}, status=status.HTTP_204_NO_CONTENT)
        resume_id = resume_instance.id 
        try:
            resume_detail = ResumeData.objects.get(resume_id = resume_id)
        except ResumeData.DoesNotExist:
            resume_detail = None
        if resume_detail == None:
            return Response({'message': 'Unable to fetch your resume'}, status=status.HTTP_204_NO_CONTENT)
        url = resume_detail.url
        return Response({'resume': url}, status=status.HTTP_200_OK)

#Util functions
def resumeDetails(request, s3_url, new_user):
    user_id = request.user.id
    resume = get_object_or_404(UploadResume, user_id = user_id)
    if new_user == True:
        resume_instance = ResumeData()
        resume_instance.resume_id = resume.id
    elif new_user == False:
        resume_instance = ResumeData.objects.get(resume_id = resume.id)
    resume_instance.url = s3_url
    return resume_instance

#generating long expiration url
def generateLongExpirationURL(key):
    object_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': str(key)},
        ExpiresIn=604800
    )
    return object_url
