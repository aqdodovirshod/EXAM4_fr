from django.contrib import admin
from .models import Vacancy, Resume, Application, FavoriteVacancy

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_active", "created_at")
    list_filter = ("is_active", "employment_type", "work_format")
    search_fields = ("title", "author__username")

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "file")
    search_fields = ("full_name", "user__username")

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "vacancy", "status", "applied_at")
    list_filter = ("status",)
    search_fields = ("applicant__username", "vacancy__title")

@admin.register(FavoriteVacancy)
class FavoriteVacancyAdmin(admin.ModelAdmin):
    list_display = ("user", "vacancy", "added_at")
    search_fields = ("user__username", "vacancy__title")