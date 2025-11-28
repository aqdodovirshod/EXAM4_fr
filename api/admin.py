from django.contrib import admin
from .models import Vacancy, Resume, Application, Company

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "author", "is_active", "created_at")
    list_filter = ("is_active", "employment_type", "work_format")
    search_fields = ("title", "company__name", "author__username")

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "desired_position", "location", "is_active")
    list_filter = ("is_active", "location")
    search_fields = ("full_name", "desired_position")

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "vacancy", "status", "applied_at")
    list_filter = ("status",)
    search_fields = ("applicant__username", "vacancy__title")

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "description")
    search_fields = ("name", "website")