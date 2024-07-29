from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from .permissions import IsPartner, Isowner, IsApproved
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import PartnerDetails, JobDescription
from datetime import datetime, timedelta
from django.db.models import DateTimeField, ExpressionWrapper, F
from .serializers import (
    CreatePartnerSerializer,
    CreateJobSerializer,
    JobDescriptionSerializer,
    ViewAllJobsSerializer,
    ViewAllJobsListSerializer,
)
import json
from rest_framework import generics
from django.core.exceptions import PermissionDenied
from application.models import AppliedToJob
from django.db import models
from django.db.models import Field
from django.core.serializers import serialize
import ast


class CreatePartner(APIView):
    """Add company of the partner

    Args:
        APIView (POST)

    Returns:
        401 UNAUTHORIZED
        201 CREATED
    """
    permission_classes = [IsAuthenticated, IsPartner]

    def post(self, request, format=None):
        data = request.data
        if data["user"] != request.user.id:
            return Response(
                {"errors": "Unauthorised user"}, status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = CreatePartnerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            partner_details = serializer.save()
            return Response({"msg": "created successfully"}, status.HTTP_201_CREATED)


class CreateJob(APIView):
    """Create a Project posting

    Args:
        APIView (POST): fill out a form and then persist into DB

    Returns:
       401 UNAUTHORIZED
       404 NOT FOUND PARTNER
       400 BAD REQUEST
       201 PROJECT POSTING CREATED
    """
    permission_classes = [IsAuthenticated, IsPartner, IsApproved]

    def post(self, request, format=None):
        data = request.data
        if data["job_posted_by"] != request.user.id:
            return Response(
                {"errors": "Unauthorised user"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            partner = PartnerDetails.objects.get(user_id=request.user.id)
        except:
            return Response({"errors": "Partner not found"}, status.HTTP_404_NOT_FOUND)
        try:
            company_name = partner.company
            if data["company"] != company_name:
                raise PermissionDenied()
        except:
            return Response(
                {
                    "errors": "Company name needs to be same as the company name of the partner"
                },
                status.HTTP_401_UNAUTHORIZED,
            )
        data["closes_at"] = data["closes_at"] * 86400
        serializer = CreateJobSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            job_description = serializer.save()
            return Response(
                {"msg": "Job created successfully"}, status.HTTP_201_CREATED
            )
        return Response({"errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)


# Own created projects
class ViewAllJobs(APIView):
    """View projects posted by an industry partner -- dashboard view of a partner

    Args:
        APIView (GET)

    Returns:
        list of objects of type JobDescription
    """
    permission_classes = [IsAuthenticated, IsPartner, IsApproved]

    def get(self, request, format=None):
        try:
            all_jobs = JobDescription.objects.filter(
                job_posted_by_id=request.user.id
            ).order_by("-created_at")
            serialized_data = ViewAllJobsSerializer(all_jobs, many=True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateJobDescription(generics.UpdateAPIView):
    """Edit project description -- owner rights

    Args:
        generics (UPDATE or PUT): Update project description

    Returns:
        HTTP 200 OK after successful update or else 400 BAD REQUEST
        HTTP 401 if user or partner unauthorized to perform this action
    """
    permission_classes = [IsAuthenticated, IsPartner, IsApproved]
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    lookup_field = "pk"

    def update(self, request, pk, *args, **kwargs):
        user = get_object_or_404(JobDescription, id=pk)
        user_id = user.job_posted_by_id
        if request.user.id != user_id:
            return Response({"message": "Not authorized"}, status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Job description updated successfully"}, status.HTTP_200_OK
            )

        else:
            return Response({"message": "failed", "details": serializer.errors},status=status.HTTP_400_BAD_REQUEST)


class DeleteJobPosting(generics.DestroyAPIView):
    """Delete project posting -- owner rights

    Args:
        generics (DELETE or DESTROY)

    Returns:
        HTTP 204 NO CONTENT after successful delete or else 400 BAD REQUEST
        HTTP 401 if user or partner unauthorized to perform this action
    """
    permission_classes = [IsAuthenticated, IsPartner, IsApproved]
    queryset = JobDescription.objects.all()

    def destroy(self, request, pk, *args, **kwargs):
        user_id = get_object_or_404(JobDescription, id=pk).job_posted_by_id
        if request.user.id != user_id:
            return Response({"message": "Not authorized"}, status.HTTP_401_UNAUTHORIZED)
        instance = self.get_object()
        try:
            instance.delete()
            return Response(
                {"message": "Successfully deleted"}, status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response({"error": str(e)}, status.HTTP_400_BAD_REQUEST)


# TODO List of students applied -- students function first


class DisplayJobs(APIView):
    """Display all projects

    Args:
        APIView (GET)

    Returns:
        list of object of type JobDescription
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            all_jobs = JobDescription.objects.filter(job_status=0).order_by(
                "-created_at"
            )
            serialized_data = ViewAllJobsSerializer(all_jobs, many=True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DisplayJobsBasedOnIds(APIView):
    """Display all projects based on IDs

    Args:
        APIView (GET)

    Returns:
        list of object of type JobDescription
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, job_ids, format=None):
        fl = 0
        job_ids = job_ids.split(",")
        if job_ids[-1] == "#":
            job_ids = [int(id) for id in job_ids[:-1]]
            fl = 1
        else:
            job_ids = [int(id) for id in job_ids]
        try:
            all_jobs = JobDescription.objects.in_bulk(job_ids)
            jobs_in_order = [all_jobs[x] for x in job_ids]
            new_list = []
            for entry in jobs_in_order:
                if fl != 1 and int(entry.job_status) != 0:
                    continue
                serialized_data = ViewAllJobsSerializer(entry)
                new_list.append(serialized_data.data)
            details = json.loads(json.dumps(new_list, indent=4, sort_keys=True))
            return Response(details, status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DisplaySingleJob(APIView):
    """Display a single project

    Args:
        APIView (GET)

    Returns:
        single object of type JobDescription based on the paramter 'pk'
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            job = get_object_or_404(JobDescription, id=pk)
            serialized_data = ViewAllJobsSerializer(job)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SearchJob(APIView):
    """Project searchfunctionality based on category

    Args:
        APIView (GET)

    Returns:
       list of object of type JobDescription
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, query, format=None):
        try:
            jobs = JobDescription.objects.all()
            filtered_jobs = jobs.filter(category__icontains=query)
            serialized_data = ViewAllJobsSerializer(filtered_jobs, many=True)
            return Response(serialized_data.data, status.HTTP_200_OK)
        except:
            return Response(
                {"errors": "Something went wrong, please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangeStatus(APIView):
    """Update status of a particular project based on the id

    Args:
        APIView (PUT)

    Returns:
        HTTP Status Code 200: Successful update
        HTTP Status Code 400: BAD REQUEST
    """
    permission_classes = [IsAuthenticated, IsApproved, IsPartner]

    def put(self, request, job_id, format=None):
        user_id = request.user.id
        try:
            job = JobDescription.objects.get(job_posted_by_id=user_id, id=job_id)
            job.job_status = request.data.get("status")
            job.save()
            return Response(
                {"message": "Job status updated successfully"},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {"errors": "Something went wrong, please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )
