from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from django.core import serializers
from .permissions import (
    IsPartner,
    Isowner,
    IsApproved,
    IsPartnerOrSupervisor,
    IsStudentOrSupervisor,
    IsStudent,
    IsSupervisor,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ApplyForProjectSerializer, ViewAllJobsSerializer
import json
from rest_framework import generics
from django.core.exceptions import PermissionDenied
from .models import AppliedToJob
from industry.models import JobDescription
from auths.models import UserDetails, User
from student.education.models import Education
from student.experience.models import ExperienceDetails
from student.project.models import ProjectDetails
from student.resume.models import ResumeData, UploadResume
from student.education.serializers import ViewEducationSerializer
from student.project.serializers import ViewProjectSerializer
from student.experience.serializers import ViewExperienceSerializer
import boto3
from django.core.mail import send_mail
from django.conf import settings

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


class ApplyForProject(APIView):
    """ Apply for a project

    Args:
        APIView (PUT)

    Returns:
        403: METHOD NOT ALLOWED TO USER
        401: BAD REQUEST
        200: OK APPLIED
    """
    permission_classes = [IsAuthenticated, IsStudentOrSupervisor]

    def put(self, request, job_id, user_id, format=None):
        """_summary_

        Args:
            request
            job_id (int): job id
            user_id (int): user id
            format (_type_, optional): Defaults to None.
        """
        if user_id != request.user.id:
            return Response(
                {"errors": "You are not authorised to perform this function"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            detail = AppliedToJob.objects.filter(user_id=user_id, has_accepted=1)
        except AppliedToJob.DoesNotExist:
            detail = None
        print(len(detail))
        if detail != None and len(detail) != 0:
            print("here")
            return Response(
                {"errors": "You are already enrolled in a project"},
                status.HTTP_403_FORBIDDEN,
            )
        else:
            try:
                detail = AppliedToJob.objects.get(user_id=user_id, job_id=job_id)
            except AppliedToJob.DoesNotExist:
                detail = None
            if detail != None:
                if detail.status == "Rejected":
                    return Response(
                        {"errors": "Unfortunately, you cannot apply to this job"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if detail.status == "Under review" or detail.has_applied == 1:
                    return Response(
                        {
                            "errors": "You have already applied for this project. Hang tight!!"
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
            context = {
                "user": user_id,
                "job": job_id,
                "status": request.data.get("status"),
                "has_applied": True,
                "has_accepted": False,
            }
            serializer = ApplyForProjectSerializer(data=context, fields=context.keys())
            if serializer.is_valid(raise_exception=True):
                application = serializer.save()
                return Response(
                    {"messsage": "You have successfully applied to the job"},
                    status.HTTP_201_CREATED,
                )
            return Response({"errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)


class SendEmailUtil(APIView):
    """Send Email to particular email

    Args:
        APIView (POST): _description_

    Returns:
        200: OK EMAIL SENT
        400: BAD REQUEST
    """
    permission_classes = [IsApproved, IsAuthenticated]

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


class ApprovedJobs(APIView):
    """List of approved projects for an user

    Args:
        APIView (GET): Redirects to different API under "industry"

    Returns:
        204: NO CONTENT
        200: OK
        400: BAD REQUEST

    """
    permission_classes = [IsApproved, IsAuthenticated, IsStudentOrSupervisor]

    def get(self, request, format=None):
        try:
            jobs_approved = AppliedToJob.objects.filter(
                user_id=request.user.id, status="Approved"
            ).values_list("job_id", flat=True)
        except AppliedToJob.DoesNotExist:
            jobs_approved = []
        if jobs_approved == []:
            return Response(
                {"message: No approved projects"}, status=status.HTTP_204_NO_CONTENT
            )
        jobs_approved = [str(x) for x in jobs_approved]
        ids = ",".join(jobs_approved)
        print(ids)
        return redirect("industry:display-job-ids", job_ids=ids)


class HasAccepted(APIView):
    """Tells us whther user has accepted any project or not

    Args:
        APIView (GET)

    Returns:
        status: project has been accepted (1) or not (0)
        200: OK
        403: FORBIDDEN
    """
    permission_classes = [IsAuthenticated, IsApproved, IsStudentOrSupervisor]

    def get(self, request, format=None):
        try:
            instance = AppliedToJob.objects.get(
                user_id=request.user.id, has_accepted=True
            )
        except AppliedToJob.DoesNotExist:
            instance = None
        if instance != None:
            return Response(
                {"errors": "You cannot offer more than one offer", "status": 1},
                status.HTTP_403_FORBIDDEN,
            )
        else:
            return Response({"status": 0}, status.HTTP_200_OK)


class AcceptOffer(APIView):
    """Student or supervisor can accept offer

    Args:
        APIView (PUT)
    """
    permission_classes = [IsAuthenticated, IsApproved, IsStudentOrSupervisor]

    def put(self, request, job_id, format=None):
        """
        Args:
            request
            job_id (int): job id

        Returns:
            HTTP 403, 200, 400
        """
        try:
            job_approvals = AppliedToJob.objects.get(
                user_id=request.user.id, status="Approved", has_accepted=1
            )
        except:
            job_approvals = None
        if job_approvals != None:
            return Response(
                {"errors": "You cannot offer more than one offer at the same time"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            instance = AppliedToJob.objects.get(
                job_id=job_id, user_id=request.user.id, status="Approved"
            )
        except AppliedToJob.DoesNotExist:
            instance = None
        if instance == None:
            return Response({"errors": "No such application exist"})
        try:
            instance.has_accepted = True
            instance.save()
            return Response(
                {"message": "You have successfully accepted the offer"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"errors": "Something went wrong, please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AppliedApplication(APIView):
    permission_classes = [IsAuthenticated, IsApproved, IsStudentOrSupervisor]

    def get(self, request, format=None):
        """Applied Applications

        Args:
            request

        Returns:
            list: projects
        """
        user_id = request.user.id
        try:
            instance = AppliedToJob.objects.filter(user_id=user_id).values_list(
                "job_id", flat=True
            )
        except AppliedToJob.DoesNotExist:
            instance = None
        if instance == None:
            return Response(
                {"message": "You have not applied to any project"},
                status=status.HTTP_204_NO_CONTENT,
            )
        try:
            job_applied_to = JobDescription.objects.filter(id__in=instance)
            serialized_data = ViewAllJobsSerializer(job_applied_to, many=True)
            print(serialized_data.data)
            return Response(
                {"projects": serialized_data.data}, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {"errors": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


class EnroledProject(APIView):
    permission_classes = [IsAuthenticated, IsApproved, IsStudentOrSupervisor]

    def get(self, request, format=None):
        """Project currently worked on by student or supervisor

        Args:
            request

        Returns:
            single object: JobDescription model
        """
        user_id = request.user.id
        print(user_id)
        try:
            job_id = AppliedToJob.objects.get(user_id=user_id, has_accepted=1).job_id
            job_id = str(job_id) + ",#"
            return redirect("industry:display-job-ids", job_ids=job_id)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WithdrawApplication(APIView):
    """Withdraw application

    Args:
        APIView (DELETE)

    Returns:
        HTTP CODE 205, 403, 400
    """
    permission_classes = [IsAuthenticated, IsStudentOrSupervisor]

    def delete(self, request, job_id, user_id, format=None):
        if request.user.id != user_id:
            return Response(
                {"errors": "You are not allowed to perform this function"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            application = AppliedToJob.objects.get(user_id=user_id, job_id=job_id)
        except AppliedToJob.DoesNotExist:
            application = None
        if application == None:
            return Response(
                {"errors": "No such application found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if application.status == "Rejected":
            return Response(
                {"errors": "You are not allowed to perform this function"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            application.delete()
            return Response(
                {"message": "Application successfully withdrawn"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {"errors": "Something went wrong! Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReviewInformation(APIView):
    """REview information before submitting

    Args:
        APIView (GET)

    Returns:
       json with user's details
    """
    permission_classes = [IsApproved, IsAuthenticated, IsStudentOrSupervisor]

    def get(self, request, format=None):
        user_id = request.user.id
        try:
            personal_detail = getPersonalDetails(user_id)
            education_detail = getEducation(user_id)
            project_detail = getProject(user_id)
            experience_detail = getExperience(user_id)
            url = getResume(user_id)
            value = makeResponse2(
                user_id,
                personal_detail,
                education_detail,
                project_detail,
                experience_detail,
                url,
            )
            details = json.loads(json.dumps(value, indent=4, sort_keys=True))
            return Response(details, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"errors": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class StudentSupervisorApplicants(APIView):
    """Applicants viewd by industry partner for a particular project

    Args:
        APIView (GET)

    Returns:
       list of json, each json contains the information about an user
    """
    permission_classes = [IsAuthenticated, IsPartner, IsApproved]

    def get(self, request, job_id, format=None):
        try:
            job_posted_by = JobDescription.objects.get(id=job_id).job_posted_by_id
        except Exception as e:
            return Response(
                {"errors": "No such project found"}, status=status.HTTP_404_NOT_FOUND
            )
        if job_posted_by != request.user.id:
            return Response(
                {"errors": "Not authorised to perform this action"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            applicants = AppliedToJob.objects.filter(job_id=job_id).values_list(
                "user_id", flat=True
            )
            applicants_info = []
            for user_id in applicants:
                personal_detail = getPersonalDetails(user_id)
                education_detail = getEducation(user_id)
                project_detail = getProject(user_id)
                experience_detail = getExperience(user_id)
                url = getResume(user_id)
                applicationStatus = getApplicationStatus(job_id, user_id)
                applicants_info.append(
                    makeResponse(
                        user_id,
                        personal_detail,
                        education_detail,
                        project_detail,
                        experience_detail,
                        url,
                        applicationStatus,
                    )
                )
            details = json.loads(json.dumps(applicants_info, indent=4, sort_keys=True))
            return Response(details, status=status.HTTP_200_OK)
        except:
            return Response(
                {"errors": "Something went wrong please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class getApprovedPersonnelData(APIView):
    """Used in ratings and access conditions

    Args:
        APIView (GET)

    Returns:
        list of JSON, each object contains approved personnel information
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id, format=None):
        try:
            applicants = (
                AppliedToJob.objects.filter(job_id=job_id)
                .filter(status="Approved")
                .values_list("user_id", flat=True)
            )
            applicants_info = []
            for user_id in applicants:
                personal_detail = getPersonalDetails(user_id)
                education_detail = getEducation(user_id)
                project_detail = getProject(user_id)
                experience_detail = getExperience(user_id)
                applicationStatus = getApplicationStatus(job_id, user_id)
                url = getResume(user_id)
                applicants_info.append(
                    makeResponse(
                        user_id,
                        personal_detail,
                        education_detail,
                        project_detail,
                        experience_detail,
                        url,
                        applicationStatus,
                    )
                )
            details = json.loads(json.dumps(applicants_info, indent=4, sort_keys=True))
            return Response(details, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"errors": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ApproveOrRejectStudent(APIView):
    """Industry partner could approve or reject applicant

    Args:
        APIView (PUT): change status of the application

    Returns:
        HTTP CODE 200, 401, 404, 400
    """
    permission_classes = [IsAuthenticated, IsApproved, IsPartner]

    def put(self, request, job_id, format=None):
        try:
            job_posted_by = JobDescription.objects.get(id=job_id).job_posted_by_id
        except Exception as e:
            return Response(
                {"errors": "No such project found"}, status=status.HTTP_404_NOT_FOUND
            )
        if job_posted_by != request.user.id:
            return Response(
                {"errors": "Not authorised to perform this action"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        student_id = request.data.get("user")
        status_val = request.data.get("status")
        try:
            application = AppliedToJob.objects.get(user_id=student_id, job_id=job_id)
        except AppliedToJob.DoesNotExist:
            application = None
        if application == None:
            return Response(
                {"errors": "No such application found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if application.status == "Rejected":
            return Response(
                {"errors": "You already rejected the applicant"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if application.status == "Approved":
            return Response(
                {"errors": "You already approved the applicant"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            application.status = status_val
            application.save()
            return Response(
                {"message": "Application status updated successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HasApplied(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    def get(self, request, job_id, format=None):
        print(job_id)
        try:
            instance = AppliedToJob.objects.get(user_id=request.user.id, job_id=job_id)
        except AppliedToJob.DoesNotExist:
            instance = None
        if instance != None:
            if instance.status == "Approved":
                return Response({"status": 1}, status.HTTP_200_OK)
            if instance.status == "Under review":
                return Response({"status": 2}, status.HTTP_200_OK)
            if instance.status == "Rejected":
                return Response({"status": 3}, status.HTTP_200_OK)
        if instance == None:
            return Response({"status": 0}, status=status.HTTP_200_OK)
        return Response({"errors": "Something went wrong"}, status.HTTP_400_BAD_REQUEST)


class StudentSupervisorApplicationStatus(APIView):
    permission_classes = [IsAuthenticated, IsApproved]

    def get(self, request, job_id, user_id, format=None):
        try:
            instance = AppliedToJob.objects.get(user_id=user_id, job_id=job_id)
        except AppliedToJob.DoesNotExist:
            instance = None
        if instance != None:
            print(instance.status)
            if instance.status == "Approved":
                return Response({"status": 1}, status.HTTP_200_OK)
            if instance.status == "Under review":
                return Response({"status": 2}, status.HTTP_200_OK)
            if instance.status == "Rejected":
                return Response({"status": 3}, status.HTTP_200_OK)
        if instance == None:
            return Response({"status": 0}, status=status.HTTP_200_OK)
        return Response({"errors": "Something went wrong"}, status.HTTP_400_BAD_REQUEST)

# Util Functions
def makeResponse(
    user_id,
    personal_detail,
    education_detail,
    project_detail,
    experience_detail,
    url,
    applicationStatus,
):
    return {
        "email": personal_detail.get("email"),
        "first_name": personal_detail.get("first_name"),
        "last_name": personal_detail.get("last_name"),
        "other": {
            "education": education_detail,
            "project": project_detail,
            "experience": experience_detail,
            "user": user_id,
        },
        "url": url,
        "status": applicationStatus,
    }

def makeResponse2(
    user_id, personal_detail, education_detail, project_detail, experience_detail, url
):
    return {
        "user": user_id,
        "personal": personal_detail,
        "education": education_detail,
        "project": project_detail,
        "experience": experience_detail,
        "url": url,
    }


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


def getEducation(user_id):
    try:
        all_education = Education.objects.filter(user_id=user_id).order_by("-id")
        serialized_data = ViewEducationSerializer(all_education, many=True)
        return serialized_data.data
    except Exception as e:
        return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def getExperience(user_id):
    try:
        all_education = ExperienceDetails.objects.filter(user_id=user_id).order_by(
            "-id"
        )
        serialized_data = ViewExperienceSerializer(all_education, many=True)
        return serialized_data.data
    except Exception as e:
        return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def getProject(user_id):
    try:
        all_education = ProjectDetails.objects.filter(user_id=user_id).order_by("-id")
        serialized_data = ViewProjectSerializer(all_education, many=True)
        return serialized_data.data
    except Exception as e:
        return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def getResume(user_id):
    try:
        resume = UploadResume.objects.get(user_id=user_id)
        url = generateLongExpirationURL(str(resume.resume))
        return url
    except Exception as e:
        return None


def generateLongExpirationURL(key):
    object_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": str(key)},
        ExpiresIn=604800,
    )
    return object_url


def getApplicationStatus(job_id, user_id):
    try:
        instance = AppliedToJob.objects.get(user_id=user_id, job_id=job_id)
    except AppliedToJob.DoesNotExist:
        instance = None
    if instance != None:
        print(instance.status)
        if instance.status == "Approved":
            return 1
        if instance.status == "Under review":
            return 2
        if instance.status == "Rejected":
            return 3
    if instance == None:
        return 0
    return null
