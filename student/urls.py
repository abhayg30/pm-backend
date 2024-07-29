from django.urls import path, include
from .education.views import (
    CreateEducation, ViewEducation, 
    UpdateEducation, DeleteEducation, 
    ViewSingleEducation, DisplayUserEducation
)

from .project.views import (
    CreateProject, ViewProjects,
    ViewSingleProject, UpdateProject,
    DeleteProject, DisplayUserProject
)

from .experience.views import (
    CreatExperience, ViewExperiences,
    ViewSingleExperience, UpdateExperience,
    DeleteExperience, DisplayUserExperience
)

from .resume.views import (
    UploadResumeView, ViewResume
)

from .views import (
    IndustryPartnerDetails, ViewPersonlisedProjects,
    SendEmailUtil
)

urlpatterns = [
    #education
    path('create/education/', CreateEducation.as_view(), name = 'create-education'),
    path('view/education/', ViewEducation.as_view(), name = 'view-education'),
    path('view/education/<int:pk>', ViewSingleEducation.as_view(), name = 'view-single-education'),
    path('update/education/<int:pk>', UpdateEducation.as_view(), name = 'update-education'),
    path('delete/education/<int:pk>', DeleteEducation.as_view(), name = 'update-education'),
    path('display/education/', DisplayUserEducation.as_view(), name = 'display-education'),
    #project
    path('create/project/', CreateProject.as_view(), name = 'create-project'),
    path('view/project/', ViewProjects.as_view(), name = 'view-project'),
    path('view/project/<int:pk>', ViewSingleProject.as_view(), name = 'view-single-project'),
    path('update/project/<int:pk>', UpdateProject.as_view(), name = 'update-project'),
    path('delete/project/<int:pk>', DeleteProject.as_view(), name = 'update-project'),
    path('display/project/', DisplayUserProject.as_view(), name = 'display-project'),
    #work_experience
    path('create/experience/', CreatExperience.as_view(), name = 'create-experience'),
    path('view/experience/', ViewExperiences.as_view(), name = 'view-experience'),
    path('view/experience/<int:pk>', ViewSingleExperience.as_view(), name = 'view-single-experience'),
    path('update/experience/<int:pk>', UpdateExperience.as_view(), name = 'update-experience'),
    path('delete/experience/<int:pk>', DeleteExperience.as_view(), name = 'update-experience'),
    path('display/experience/', DisplayUserExperience.as_view(), name = 'display-experience'),
    #resume_upload
    path('resume/', UploadResumeView.as_view(), name = 'upload-resume'),
    path('view/resume/', ViewResume.as_view(), name = 'view-resume'),
    #view
    path('partner-detail/', IndustryPartnerDetails.as_view(), name = "partner-details"),
    path('dashboard/',ViewPersonlisedProjects.as_view(), name = 'personalised-projects'),
    path('send-email/', SendEmailUtil.as_view(), name = 'send-email')
]