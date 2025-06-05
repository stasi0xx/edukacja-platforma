from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        PARENT = "parent", "Parent"

    role = models.CharField(max_length=20, choices=Role.choices)


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

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
    file = models.FileField(upload_to=submission_upload_path)
    comment = models.TextField(blank=True)
    grade = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.task.name}"


class Comment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
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
