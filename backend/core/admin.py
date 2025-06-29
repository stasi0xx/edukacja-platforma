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
    ClassGroup
)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "deadline")
    filter_horizontal = ("assigned_students",)

class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "teacher"]
    search_fields = ["name", "teacher__user__username"]





admin.site.register(User, UserAdmin)
admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(ParentProfile)
admin.site.register(Task, TaskAdmin)
admin.site.register(Submission)
admin.site.register(Comment)
admin.site.register(Ranking)
admin.site.register(ParentChildRelation)

