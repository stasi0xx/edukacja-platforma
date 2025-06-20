from rest_framework import serializers
from .models import (
    Task, Submission, Comment, Ranking,
    StudentProfile, ParentProfile, TeacherProfile, User, ParentChildRelation
)

class TaskSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    submission_id = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "deadline",
            "created_at",
            "status",
            "submission_id",
        ]

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

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["id", "student", "task", "file"]
        read_only_fields = ["student"]
    def create(self, validated_data):
        request = self.context["request"]
        validated_data["student"] = request.user.studentprofile
        return super().create(validated_data)
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
    student_name = serializers.CharField(source='student.user.username', read_only=True)

    class Meta:
        model = Ranking
        fields = ['id', 'student', 'student_name', 'score', 'position']


class TopRankingSerializer(serializers.Serializer):
    username = serializers.CharField()
    completed = serializers.IntegerField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
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
