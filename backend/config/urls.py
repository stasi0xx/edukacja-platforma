"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from core import views as core_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
schema_view = get_schema_view(
    openapi.Info(title="Edukacja API", default_version="v1"),
    public=True,
    permission_classes=[AllowAny],
)
from core import urls as core_urls
from core.views import my_tasks, SubmissionUploadView, GroupRankingView
from core.views import (
    TeacherMyStudentsView,
    TeacherStudentSubmissionsView,
    TeacherAddCommentView,
    TeacherSubmissionCommentsView,
    TeacherTaskCreateView,
)

router = routers.DefaultRouter()
router.register(r"users", core_views.UserViewSet)
router.register(r"students", core_views.StudentProfileViewSet)
router.register(r"teachers", core_views.TeacherProfileViewSet)
router.register(r"parents", core_views.ParentProfileViewSet)
router.register(r"tasks", core_views.TaskViewSet)
router.register(r"submissions", core_views.SubmissionViewSet)
router.register(r"comments", core_views.CommentViewSet)
router.register(r"rankings", core_views.RankingViewSet)
router.register(r"relations", core_views.ParentChildRelationViewSet)


print("Loaded core urls:", core_urls.urlpatterns)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("core.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/my-student-profile/", core_views.MyStudentProfileView.as_view()),
    path("api/me/", core_views.CurrentUserView.as_view()),
    path("api/my/", core_views.MeView.as_view()),
    path("api/my-tasks/", my_tasks),
    path("api/submit-task/", SubmissionUploadView.as_view(), name="submit-task"),
    path(
        "api/submissions/<int:pk>/add_comment/",
        core_views.SubmissionViewSet.as_view({"patch": "add_comment", "post": "add_comment"}),
    ),
    path(
        "api/submissions/<int:pk>/comments/",
        core_views.SubmissionViewSet.as_view({"get": "comments"}),
    ),
    path("api/ranking/group/<int:group_id>/", GroupRankingView.as_view(), name='group-ranking'),
    path(
        "api/teacher/student/<int:pk>/submissions/",
        TeacherStudentSubmissionsView.as_view(),
    ),
    path(
        "api/teacher/submission/<int:pk>/add_comment/",
        TeacherAddCommentView.as_view(),
    ),
    path(
        "api/teacher/submission/<int:pk>/comments/",
        TeacherSubmissionCommentsView.as_view(),
    ),
    path("api/teacher/tasks/create/", TeacherTaskCreateView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)