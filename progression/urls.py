from django.urls import path, include
from .progresslogs.views import (
    CreateProgressLog, ViewProgressLogsByStudentId,
    ViewProgressLogsByProjectID, UpdateProgressLog,
    DeleteProgressLog
)

from .comments.views import (
    CreateCommentOnLog,
    ViewCommentLogsByProjectID, ViewCommentLogsByProgressLogID,
    UpdateComment, DeleteComment
)


urlpatterns = [
    #progress logs
    path('create/progresslog/', CreateProgressLog.as_view(), name = 'create-progresslog'),
    path('view/progresslogstudent/<int:pk>', ViewProgressLogsByStudentId.as_view(), name = 'view-progresslog-student'),
    path('view/progresslogproject/<int:pk>', ViewProgressLogsByProjectID.as_view(), name = 'view-progresslog-project'),
    path('edit/progresslog/<int:pk>', UpdateProgressLog.as_view(), name = 'update-progresslog'),
    path('delete/progresslog/<int:pk>', DeleteProgressLog.as_view(), name = 'delete-progresslog'),

    #comments
    path('create/comment/', CreateCommentOnLog.as_view(), name = 'create-comment'),
    path('view/commentproject/<int:pk>', ViewCommentLogsByProjectID.as_view(), name = 'view-comment-project'),
    path('view/commentprogresslog/<int:pk>', ViewCommentLogsByProgressLogID.as_view(), name = 'view-comment-progresslog'),
    path('edit/commentprogresslog/<int:pk>', UpdateComment.as_view(), name = 'update-comment'),
    path('delete/commentprogresslog/<int:pk>', DeleteComment.as_view(), name = 'delete-comment'),

]