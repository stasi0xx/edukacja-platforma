import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import StudentProfile, TeacherProfile, Task, Submission, Comment


class CommentTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="student", password="pass", role="student")
        self.student_profile = StudentProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

        teacher_user = User.objects.create_user(username="teacher", password="pass", role="teacher")
        self.teacher_profile = TeacherProfile.objects.create(user=teacher_user, subject="Math")
        self.task = Task.objects.create(name="Test", description="desc", created_by=self.teacher_profile)
        self.task.assigned_students.add(self.student_profile)
        self.submission = Submission.objects.create(task=self.task, student=self.student_profile, file="test.txt")
        self.task2 = Task.objects.create(name="Test2", description="desc2", created_by=self.teacher_profile)
        self.task2.assigned_students.add(self.student_profile)

        # second submission for ranking test
        self.submission2 = Submission.objects.create(task=self.task2, student=self.student_profile, file="file2.txt")

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
        self.assertEqual(response.data[0]['username'], self.user.username)
        self.assertEqual(response.data[0]['completed'], 2)

    def test_my_tasks_endpoint_returns_sorted_tasks(self):
        url = "/api/my-tasks/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.task2.id)
        first_task = response.data[0]
        self.assertTrue(first_task["status"])  # has submission
        self.assertIsNotNone(first_task["submission_id"])
