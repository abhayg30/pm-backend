from django.urls import path, include
from .views import (
    CreatePartner,
    CreateJob,
    UpdateJobDescription,
    DeleteJobPosting,
    ViewAllJobs,
    DisplayJobs,
    DisplaySingleJob,
    ChangeStatus,
    SearchJob,
    DisplayJobsBasedOnIds,
)

app_name = "industry"

urlpatterns = [
    path("create/", CreatePartner.as_view(), name="create_partner"),
    path("job/create/", CreateJob.as_view(), name="create_job"),
    path("job/update/<int:pk>/", UpdateJobDescription.as_view(), name="update_job"),
    path("job/update/<int:pk>/", UpdateJobDescription.as_view(), name="update_job"),
    path("job/delete/<int:pk>/", DeleteJobPosting.as_view(), name="delete_job"),
    path("job/view/all/", ViewAllJobs.as_view(), name="all_jobs"),
    path("job/display/", DisplayJobs.as_view(), name="display_jobs"),
    path("job/display/<int:pk>", DisplaySingleJob.as_view(), name="display_single_job"),
    path("change/status/<int:job_id>/", ChangeStatus.as_view(), name="change-status"),
    path("search/<str:query>/", SearchJob.as_view(), name="search"),
    path("test/<str:job_ids>", DisplayJobsBasedOnIds.as_view(), name="display-job-ids")
]
