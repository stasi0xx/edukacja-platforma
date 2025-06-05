from rest_framework import serializers
from django.contrib.auth import get_user_model
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

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = StudentProfile
        fields = ["id", "user", "points"]


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TeacherProfile
        fields = ["id", "user", "bio"]


class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ParentProfile
        fields = ["id", "user"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "name", "description", "deadline", "created_by", "created_at"]


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            "id",
            "task",
            "student",
            "file",
            "comment",
            "grade",
            "feedback",
            "created_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "submission", "author", "text", "created_at"]


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ["id", "student", "points"]


class ParentChildRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChildRelation
        fields = ["id", "parent", "child"]
