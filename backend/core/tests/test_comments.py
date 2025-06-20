import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import (
    StudentProfile,
    TeacherProfile,
    Task,
    Submission,
    Comment,
    Group,
)


class CommentTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="student", password="pass", role="student")
        self.student_profile = StudentProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

        teacher_user = User.objects.create_user(username="teacher", password="pass", role="teacher")
        self.teacher_profile = TeacherProfile.objects.create(user=teacher_user, subject="Math")
        self.group = Group.objects.create(name="G1", teacher=self.teacher_profile)
        self.student_profile.group = self.group
        self.student_profile.save()
        self.task = Task.objects.create(name="Test", description="desc", created_by=self.teacher_profile)
        self.task.assigned_students.add(self.student_profile)
        self.submission = Submission.objects.create(task=self.task, student=self.student_profile, file="test.txt")
        self.task2 = Task.objects.create(name="Test2", description="desc2", created_by=self.teacher_profile)
        self.task2.assigned_students.add(self.student_profile)

        # second submission for ranking test
        self.submission2 = Submission.objects.create(task=self.task2, student=self.student_profile, file="file2.txt")

        # assign grades so ranking has points
        self.submission.grade = 80
        self.submission.save()
        self.submission2.grade = 90
        self.submission2.save()

    def test_comment_viewset_creates_comment_with_authenticated_user(self):
        url = reverse('comment-list')
        data = {"submission": self.submission.id, "text": "Hello"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(id=response.data['id'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.role, "student")

    def test_add_comment_action_assigns_author_and_role(self):
        url = reverse('submission-add-comment', args=[self.submission.id])
        response = self.client.patch(url, {"text": "Hi"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.first()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.role, "student")

    def test_submission_comments_endpoint_returns_comments(self):
        Comment.objects.create(submission=self.submission, author=self.user, text="a", role="student")
        Comment.objects.create(submission=self.submission, author=self.user, text="b", role="student")
        url = reverse('submission-comments', args=[self.submission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['text'], "a")

    def test_top_ranking_endpoint(self):
        url = "/api/top-ranking/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['student_name'], self.user.username)
        self.assertEqual(response.data[0]['points'], 170)

    def test_my_tasks_endpoint_returns_sorted_tasks(self):
        url = "/api/my-tasks/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.task2.id)
        first_task = response.data[0]
        self.assertTrue(first_task["status"])  # has submission
        self.assertIsNotNone(first_task["submission_id"])

    def test_teacher_my_students_endpoint(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        url = "/api/teacher/my-students/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.student_profile.id)

    def test_teacher_student_submissions_endpoint(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        url = f"/api/teacher/student/{self.student_profile.id}/submissions/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["status"], "submitted")

    def test_teacher_add_comment_endpoint(self):
        self.client.force_authenticate(user=self.teacher_profile.user)
        url = f"/api/teacher/submission/{self.submission.id}/add_comment/"
        response = self.client.post(url, {"text": "Well done"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment = Comment.objects.last()
        self.assertEqual(comment.role, "teacher")

