from rest_framework import serializers
from django.utils import timezone
from .models import (
    Task,
    Submission,
    Comment,
    Ranking,
    StudentProfile,
    ParentProfile,
    TeacherProfile,
    User,
    ParentChildRelation,
    ClassGroup,
)

class TaskSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    submission_id = serializers.SerializerMethodField()
    submission = serializers.SerializerMethodField()
    file = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "deadline",
            "file",
            "created_at",
            "status",
            "submission_id",
            "submission",
        ]

    def create(self, validated_data):
        # created_by jest ustawiany ręcznie w widoku
        return Task.objects.create(**validated_data)

    def get_status(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        user = request.user
        student = getattr(user, "studentprofile", None)
        if not student:
            return False
        return Submission.objects.filter(task=obj, student=student).exists()

    def get_submission_id(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        user = request.user
        student = getattr(user, "studentprofile", None)
        if not student:
            return None
        submission = Submission.objects.filter(task=obj, student=student).first()
        return submission.id if submission else None
    def get_submission(self, obj):  # <- NOWA METODA
        request = self.context.get("request")
        if not request:
            return None
        user = request.user
        student = getattr(user, "studentprofile", None)
        if not student:
            return None
        submission = Submission.objects.filter(task=obj, student=student).first()
        if not submission:
            return None
        return SubmissionSerializer(submission).data


class SubmissionSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), source="task", write_only=True
    )
    class Meta:
        model = Submission
        fields = ["id", "student", "task", "task_id", "grade", "file", "status", "submitted_at"]
        read_only_fields = ['id',"student", 'created_at']

    def create(self, validated_data):
        request = self.context["request"]
        student = request.user.studentprofile
        task = validated_data["task"]

        submission, created = Submission.objects.update_or_create(
            student=student,
            task=task,
            defaults={
                "file": validated_data.get("file"),
                "status": "submitted",
                "submitted_at": timezone.now()
            }
        )

        return submission

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "submission", "author", "text", "role", "created_at"]
        read_only_fields = ["author", "role", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        validated_data["author"] = user
        validated_data["role"] = (
            "teacher" if hasattr(user, "teacherprofile") else "student"
        )
        return super().create(validated_data)

class RankingSerializer(serializers.ModelSerializer):
    """Serialize ranking with username and points."""

    student_name = serializers.CharField(
        source="student.user.username", read_only=True
    )

    class Meta:
        model = Ranking
        fields = ["id", "student", "student_name", "points"]


class TopRankingSerializer(serializers.Serializer):
    username = serializers.CharField()
    completed = serializers.IntegerField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class StudentBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = StudentProfile
        fields = ['id', 'full_name', 'email']


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = '__all__'

class ParentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = '__all__'

class ParentChildRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChildRelation
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroup
        fields = '__all__'
