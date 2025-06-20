from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone



class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        PARENT = "parent", "Parent"

    role = models.CharField(max_length=20, choices=Role.choices)



class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Group(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey("TeacherProfile", on_delete=models.CASCADE, related_name="groups")

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="students", null=True, blank=True)

    def __str__(self):
        return self.user.username

class ParentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    assigned_students = models.ManyToManyField(
    StudentProfile,
    related_name="tasks"
)
    created_by = models.ForeignKey(
        TeacherProfile, related_name="tasks", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def submission_upload_path(instance, filename):
    return f"submissions/{instance.student.user.id}/{filename}"


class Submission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to=submission_upload_path, null=True, blank=True)
    comment = models.TextField(blank=True)
    grade = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("submitted", "Submitted")],
        default="submitted",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.task.name}"


class Comment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    role = models.CharField(max_length=20, choices=[("student", "Student"), ("teacher", "Teacher")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username}"


class Ranking(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)

    def update_points(self):
        total = Submission.objects.filter(student=self.student, grade__isnull=False).aggregate(models.Sum("grade"))["grade__sum"] or 0
        self.points = total
        self.save()

    def __str__(self):
        return f"{self.student.user.username} - {self.points} pts"


class ParentChildRelation(models.Model):
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, related_name="children")
    child = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="parents")

    class Meta:
        unique_together = ("parent", "child")

    def __str__(self):
        return f"{self.parent.user.username} -> {self.child.user.username}"


# Create your models here.
