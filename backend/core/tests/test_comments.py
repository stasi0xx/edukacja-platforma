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

    def test_comment_viewset_creates_comment_with_authenticated_user(self):
        url = reverse('comment-list')
        data = {"submission": self.submission.id, "text": "Hello"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(id=response.data['id'])
        self.assertEqual(comment.user, self.user)

    def test_add_comment_action_assigns_user(self):
        url = reverse('submission-add-comment', args=[self.submission.id])
        response = self.client.patch(url, {"comment": "Hi"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.first()
        self.assertEqual(comment.user, self.user)
