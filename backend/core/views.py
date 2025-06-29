from rest_framework import viewsets, generics, status
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
    ClassGroup,
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
    permission_classes = [IsAuthenticated]

    def _has_access(self, user, submission):
        if hasattr(user, "studentprofile") and submission.student == user.studentprofile:
            return True
        if hasattr(user, "teacherprofile") and submission.task.created_by == user.teacherprofile:
            return True
        return False

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def set_grade(self, request, pk=None):
        submission = self.get_object()

        if not hasattr(request.user, "teacherprofile"):
            return Response({"error": "Tylko nauczyciel może oceniać"}, status=403)

        grade = request.data.get("grade")
        if grade is None or not (0 <= int(grade) <= 6):
            return Response({"error": "Ocena musi być liczbą z przedziału 0–6"}, status=400)

        submission.grade = int(grade)
        submission.save()

        return Response({"message": "Ocena została zapisana", "grade": submission.grade}, status=200)

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
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user.studentprofile)

    def create(self, request, *args, **kwargs):
        student = request.user.studentprofile
        task_id = request.data.get('task')
        submission = Submission.objects.filter(student=student, task_id=task_id).first()
        print('student:', student)
        print('task_id:', task_id)
        print('existing submission:', submission)
        if submission:
            serializer = self.get_serializer(submission, data=request.data, partial=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) if not submission else serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK if submission else status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get("student")
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

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

    def create(self, request, *args, **kwargs):
        student = request.user.studentprofile
        task_id = request.data.get('task')

        if not task_id:
            return Response({"error": "Brakuje ID zadania (task_id)"}, status=400)

        # Sprawdź, czy istnieje już submission dla tego ucznia i zadania
        submission = Submission.objects.filter(student=student, task_id=task_id).first()

        if submission:
            # Update istniejącego submission
            serializer = self.get_serializer(submission, data=request.data, partial=True)
        else:
            # Tworzenie nowego submission
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        
        if submission:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer.save(student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        rankings = (
            Ranking.objects.select_related("student__user")
            .order_by("-points")[:10]
        )
        serializer = RankingSerializer(rankings, many=True)
        return Response(serializer.data)


class TeacherMyStudentsView(APIView):
    permission_classes = [IsAuthenticated]
    print("test")
    def get(self, request):
        print("✅ wszedłem do TeacherMyStudentsView")
        teacher = getattr(request.user, "teacherprofile", None)
        if not teacher:
            print("Blad")
        print("🔎 Authenticated user:", request.user)
        print("🎓 TeacherProfile:", teacher)
        if not teacher:
            return Response(status=403)

        students = StudentProfile.objects.filter(group__teacher=teacher).select_related("user").order_by("user__first_name", "user__last_name")
        print("👨‍🏫 Students found:", list(students))
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
                "id": pk,
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
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        teacher = getattr(request.user, "teacherprofile", None)
        print(request.data)
        if not teacher:
            return Response(status=403)
        serializer = TaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        group_id = request.data.get("group")
        print("RECEIVED group_id:", group_id)
        print("Authenticated user:", request.user)
        print("Teacher profile:", teacher)
        print("Available groups:", ClassGroup.objects.all())
        group = ClassGroup.objects.filter(id=group_id, teacher=teacher).first()
        if not group:
            return Response({"error": "Brak grupy"}, status=404)
        task = serializer.save(created_by=teacher)
        assigned_students = list(group.students.all())
        task.assigned_students.set(assigned_students)
        for student in assigned_students:
            Submission.objects.create(task=task, student=student, status="pending")
        names = [s.user.get_full_name() or s.user.username for s in assigned_students]
        return Response({"task_id": task.id, "students": names}, status=201)

class FullUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        data = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        }

        if hasattr(user, "teacherprofile"):
            data["profile_type"] = "teacher"
            data["profile_id"] = user.teacherprofile.id
        elif hasattr(user, "studentprofile"):
            data["profile_type"] = "student"
            data["profile_id"] = user.studentprofile.id
        else:
            data["profile_type"] = None
            data["profile_id"] = None

        return Response(data)

class MyGroupsView(APIView):
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        print("testujemyGrupy")
        teacher = getattr(request.user, "teacherprofile", None)
        if not teacher:
            return Response(status=403)

        groups = ClassGroup.objects.filter(teacher=teacher)
        serialized = [{"id": g.id, "name": g.name} for g in groups]
        return Response(serialized)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "name": user.get_full_name(),
            "group_id": user.studentprofile.group.id if hasattr(user, "studentprofile") else None
        })
    
class GroupRankingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        # 1. Pobierz wszystkich uczniów w danej grupie i ich ranking
        group_rankings = (
            Ranking.objects
            .filter(student__group_id=group_id)
            .select_related("student__user")
            .order_by("-points")
        )

        # 2. Serializacja TOP 3
        top_3 = group_rankings[:3]
        top_3_serialized = RankingSerializer(top_3, many=True).data

        # 3. Znajdź pozycję aktualnego ucznia (jeśli należy do tej grupy)
        try:
            student = StudentProfile.objects.get(user=request.user)
            my_ranking = group_rankings.filter(student=student).first()
            my_index = list(group_rankings).index(my_ranking) if my_ranking else None
            my_serialized = RankingSerializer(my_ranking).data if my_ranking else None
        except StudentProfile.DoesNotExist:
            my_index = None
            my_serialized = None

        return Response({
            "top": top_3_serialized,
            "my_position": {
                "rank": my_index + 1 if my_index is not None else None,
                "data": my_serialized
            }
        })