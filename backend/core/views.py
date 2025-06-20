from rest_framework import viewsets, generics
from .models import (
    Task,
    Submission,
    Comment,
    Ranking,
    User,
    StudentProfile,
    TeacherProfile,
    ParentProfile,
    ParentChildRelation,
    Group,
)
from django.db import models
from .serializers import (
    TaskSerializer,
    SubmissionSerializer,
    CommentSerializer,
    RankingSerializer,
    UserSerializer,
    StudentProfileSerializer,
    TeacherProfileSerializer,
    ParentProfileSerializer,
    ParentChildRelationSerializer,
    StudentBriefSerializer,
    GroupSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser, FormParser

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_tasks(request):
    student_profile = getattr(request.user, "studentprofile", None)
    if not student_profile:
        return Response({"error": "Brak profilu ucznia"}, status=403)

    tasks = (
        Task.objects.filter(assigned_students=student_profile)
        .order_by("-created_at")
    )
    serializer = TaskSerializer(tasks, many=True, context={"request": request})
    return Response(serializer.data)
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def _has_access(self, user, submission):
        if hasattr(user, "studentprofile") and submission.student == user.studentprofile:
            return True
        if hasattr(user, "teacherprofile") and submission.task.created_by == user.teacherprofile:
            return True
        return False

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        submission = self.get_object()
        if not self._has_access(request.user, submission):
            return Response(status=403)
        comments = submission.comments.order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch", "post"], permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk=None):
        submission = self.get_object()
        if not self._has_access(request.user, submission):
            return Response(status=403)
        text = request.data.get("text") or request.data.get("comment")
        if not text:
            return Response({"error": "Brak komentarza"}, status=400)
        comment = Comment.objects.create(
            submission=submission,
            author=request.user,
            text=text,
            role="teacher" if hasattr(request.user, "teacherprofile") else "student",
        )
        comments = submission.comments.order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=201)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

class RankingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ranking.objects.all().order_by('-points')  # lub bez .order_by()
    serializer_class = RankingSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer

class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer

class SubmissionUploadView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

class ParentChildRelationViewSet(viewsets.ModelViewSet):
    queryset = ParentChildRelation.objects.all()
    serializer_class = ParentChildRelationSerializer

class MyStudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = StudentProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({"detail": "Brak profilu ucznia."}, status=404)
        return Response(StudentProfileSerializer(profile).data)


class CurrentUserView(APIView):
    """Return basic info about the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "role": getattr(user, "role", None),
        }
        return Response(data)


class TopRankingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = (
            StudentProfile.objects.annotate(
                completed=models.Count("submissions")
            )
            .order_by("-completed")[:10]
        )
        data = [
            {"username": s.user.username, "completed": s.completed} for s in students
        ]
        return Response(data)


class TeacherMyStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teacher = getattr(request.user, "teacherprofile", None)
        if not teacher:
            return Response(status=403)
        students = (
            StudentProfile.objects.filter(group__teacher=teacher)
            .select_related("user")
            .order_by("user__first_name", "user__last_name")
        )
        serializer = StudentBriefSerializer(students, many=True)
        return Response(serializer.data)


class TeacherStudentSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        teacher = getattr(request.user, "teacherprofile", None)
        if not teacher:
            return Response(status=403)
        student = StudentProfile.objects.filter(id=pk, group__teacher=teacher).first()
        if not student:
            return Response(status=404)
        submissions = Submission.objects.filter(student=student).select_related("task")
        data = [
            {
                "task_name": s.task.name,
                "file": request.build_absolute_uri(s.file.url) if s.file else None,
                "submitted_at": s.submitted_at,
                "comment_count": s.comments.count(),
                "status": s.status,
            }
            for s in submissions
        ]
        return Response(data)


class TeacherAddCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        teacher = getattr(request.user, "teacherprofile", None)
        if not teacher:
            return Response(status=403)
        submission = Submission.objects.filter(id=pk, task__created_by=teacher).first()
        if not submission:
            return Response(status=404)
        text = request.data.get("text")
        if not text:
            return Response({"error": "Brak komentarza"}, status=400)
        Comment.objects.create(
            submission=submission,
            author=request.user,
            text=text,
            role="teacher",
        )
        comments = submission.comments.order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class TeacherSubmissionCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        teacher = getattr(request.user, "teacherprofile", None)
        if not teacher:
            return Response(status=403)
        submission = Submission.objects.filter(id=pk, task__created_by=teacher).first()
        if not submission:
            return Response(status=404)
        comments = submission.comments.order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class TeacherTaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        teacher = getattr(request.user, "teacherprofile", None)
        if not teacher:
            return Response(status=403)
        serializer = TaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        group_id = request.data.get("group_id")
        group = Group.objects.filter(id=group_id, teacher=teacher).first()
        if not group:
            return Response({"error": "Brak grupy"}, status=404)
        task = serializer.save(created_by=teacher)
        assigned_students = list(group.students.all())
        task.assigned_students.set(assigned_students)
        for student in assigned_students:
            Submission.objects.create(task=task, student=student, status="pending")
        names = [s.user.get_full_name() or s.user.username for s in assigned_students]
        return Response({"task_id": task.id, "students": names}, status=201)
