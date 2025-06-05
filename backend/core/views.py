from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import viewsets, permissions, decorators, response
from rest_framework.exceptions import NotFound

from .models import (
    StudentProfile,
    TeacherProfile,
    ParentProfile,
    Task,
    Submission,
    Comment,
    Ranking,
    ParentChildRelation,
)
from .serializers import (
    UserSerializer,
    StudentProfileSerializer,
    TeacherProfileSerializer,
    ParentProfileSerializer,
    TaskSerializer,
    SubmissionSerializer,
    CommentSerializer,
    RankingSerializer,
    ParentChildRelationSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

    @decorators.action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        try:
            student = self.get_object()
        except Exception:
            raise NotFound()
        submissions = Submission.objects.filter(student=student, grade__isnull=False)
        total_tasks = Task.objects.count()
        submitted = submissions.count()
        points = submissions.aggregate(models.Sum("grade"))["grade__sum"] or 0
        avg = submissions.aggregate(models.Avg("grade"))["grade__avg"] or 0
        data = {
            "submitted": submitted,
            "total": total_tasks,
            "points": points,
            "average": avg,
        }
        return response.Response(data)


class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer


class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class RankingViewSet(viewsets.ModelViewSet):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer


class ParentChildRelationViewSet(viewsets.ModelViewSet):
    queryset = ParentChildRelation.objects.all()
    serializer_class = ParentChildRelationSerializer
