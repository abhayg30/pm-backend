"""
URL configuration for powerpuff project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    #path for user authentication and profile handling
    path("api/user/", include("auths.urls")),
    #path for industry partner and project related apis
    path("partner/", include("industry.urls")),
    #path for student and supervisor functionalities and apis
    path("stusup/", include("student.urls")),
    #path for progression logs apis
    path("progressLogs/", include("progression.urls")),
    #path for rating apis
    path("ratings/", include("ratings.urls")),
    #path for application apis
    path("application/", include("application.urls")),
]
