from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, SubmissionViewSet, CommentViewSet,
    RankingViewSet, UserViewSet
)
from django.urls import path, include
from core.views import my_tasks

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'submissions', SubmissionViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'rankings', RankingViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
]
