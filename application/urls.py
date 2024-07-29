from django.urls import path, include
from .views import (
    ApplyForProject,
    WithdrawApplication,
    StudentSupervisorApplicants,
    ApproveOrRejectStudent,
    HasApplied,
    AppliedApplication,
    ReviewInformation,
    getApprovedPersonnelData,
    SendEmailUtil,
    StudentSupervisorApplicationStatus,
    AcceptOffer,
    ApprovedJobs,
    HasAccepted,
    EnroledProject,
)

urlpatterns = [
    path("apply/<int:job_id>/<int:user_id>/", ApplyForProject.as_view(), name="apply"),
    path(
        "withdraw/<int:job_id>/<int:user_id>/",
        WithdrawApplication.as_view(),
        name="withdraw",
    ),
    path(
        "view-applicants/<int:job_id>/",
        StudentSupervisorApplicants.as_view(),
        name="view-applicants",
    ),
    path(
        "view-approved-personnel/<int:job_id>/",
        getApprovedPersonnelData.as_view(),
        name="view-personnel",
    ),
    path(
        "update/<int:job_id>/",
        ApproveOrRejectStudent.as_view(),
        name="approve-or-reject",
    ),
    path("status/<int:job_id>/", HasApplied.as_view(), name="application-status"),
    path("view/projects/", AppliedApplication.as_view(), name="view-projects"),
    path("review/", ReviewInformation.as_view(), name="review-info"),
    path("send-email/", SendEmailUtil.as_view(), name="send-email"),
    path("accept-offer/<int:job_id>/", AcceptOffer.as_view(), name="accept-offer"),
    path(
        "application-status/<int:job_id>/<int:user_id>/",
        StudentSupervisorApplicationStatus.as_view(),
        name="application-status",
    ),
    path("approved-jobs/", ApprovedJobs.as_view(), name="approved-jobs"),
    path("has-accepted/", HasAccepted.as_view(), name="accepted-jobs"),
    path("enroled-projects/", EnroledProject.as_view(), name="enroled-projects"),
]
