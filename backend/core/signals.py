from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Submission, Ranking, StudentProfile


@receiver(post_save, sender=Submission)
def update_ranking_on_submission(sender, instance, **kwargs):
    ranking, _ = Ranking.objects.get_or_create(student=instance.student)
    ranking.update_points()
