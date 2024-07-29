from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
import requests
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import (
    IsApproved,
    IsStudent,
    IsSupervisor,
    Isowner,
    IsPartner,
    IsPartnerOrSupervisor,
    IsStudentOrSupervisor,
)
from rest_framework import status
import json
from rest_framework import generics
from django.forms.models import model_to_dict
from datetime import date, datetime
from auths.models import User, UserDetails
from industry.models import PartnerDetails
from application.models import MatchedJobs
from django.conf import settings
from django.core.mail import send_mail


class ViewPersonlisedProjects(APIView):
    """Dashboard view of student and supervisor -- recommended projects

    Args:
        APIView (GET)

    Returns:
        list : object of type JobDescription
    """
    permission_classes = [IsApproved, IsAuthenticated, IsStudentOrSupervisor]

    def get(self, request, format=None):
        try:
            instance = MatchedJobs.objects.get(user_id=request.user.id)
        except MatchedJobs.DoesNotExist:
            instance = None
        if instance == None:
            return redirect("industry:display_jobs")
        ids = instance.job_id
        ids = ids.replace("[", "")
        ids = ids.replace("]", "")
        ids = ids.replace(" ", "")
        if ids == '':
            return redirect("industry:display-job")
        return redirect("industry:display-job-ids", job_ids=ids)


class IndustryPartnerDetails(APIView):
    """Browse partners -- supervisor access only

    Args:
        APIView (GET)

    Returns:
        list: object of type UserDetails
    """
    permission_classes = [IsApproved, IsAuthenticated, IsSupervisor]

    def get(self, request, format=None):
        new_list = []
        try:
            list_users = User.objects.filter(user_type=2, status=1).values_list(
                "id", flat=True
            )
            for user_id in list_users:
                personal_details = getPersonalDetails(user_id=user_id)
                company_name = PartnerDetails.objects.get(user_id=user_id).company
                response = makeResponse(personal_details, company_name, user_id)
                new_list.append(response)
            details = json.loads(json.dumps(new_list, indent=4, sort_keys=True))
            return Response(details, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendEmailUtil(APIView):
    """Send email to industry partners

    Args:
        APIView (POST)

    Returns:
        200: OK
        400: BAD REQUEST
    """
    permission_classes = [IsApproved, IsAuthenticated, IsSupervisor]

    def post(self, request, format=None):
        to_email = request.data.get("email")
        subject = request.data.get("subject")
        body = request.data.get("body")
        try:
            send_mail(
                subject,
                body,
                request.user.email,
                [to_email],
                fail_silently=False,
            )
            return Response({"message": "Email sent successfully"}, status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": str(e)}, status.HTTP_400_BAD_REQUEST)

#util functions
def getPersonalDetails(user_id):
    try:
        email = User.objects.get(id=user_id).email
        personal_detail = UserDetails.objects.get(user_id=user_id)
        return {
            "email": email,
            "first_name": personal_detail.first_name,
            "last_name": personal_detail.last_name,
        }
    except Exception as e:
        return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def makeResponse(personal_detail, company, user_id):
    return {
        "user": user_id,
        "email": personal_detail.get("email"),
        "first_name": personal_detail.get("first_name"),
        "last_name": personal_detail.get("last_name"),
        "company": company,
    }
