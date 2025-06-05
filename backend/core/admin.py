from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    StudentProfile,
    TeacherProfile,
    ParentProfile,
    Task,
    Submission,
    Comment,
    Ranking,
    ParentChildRelation,
)

admin.site.register(User, UserAdmin)
admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(ParentProfile)
admin.site.register(Task)
admin.site.register(Submission)
admin.site.register(Comment)
admin.site.register(Ranking)
admin.site.register(ParentChildRelation)
