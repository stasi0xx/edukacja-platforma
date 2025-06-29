from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, SubmissionViewSet, CommentViewSet,
    RankingViewSet, UserViewSet, TeacherMyStudentsView, FullUserProfileView, MyGroupsView
)
from django.urls import path, include
from core.views import my_tasks
from rest_framework.views import APIView
from rest_framework.response import Response

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'submissions', SubmissionViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'rankings', RankingViewSet)
router.register(r'users', UserViewSet)

class DebugTest(APIView):
    def get(self, request):
        return Response({"status": "ok"})

urlpatterns = [
    path('', include(router.urls)),
    path("me/full-profile/", FullUserProfileView.as_view(), name="full-profile"),
    path("teacher/my-students/", TeacherMyStudentsView.as_view()),
    path("teacher/my-groups/", MyGroupsView.as_view()),
]
