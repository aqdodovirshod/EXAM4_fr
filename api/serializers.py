from rest_framework import serializers
from .models import Vacancy, Resume, Application, FavoriteVacancy
from django.contrib.auth import get_user_model

User = get_user_model()

class VacancyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = [
            "title",
            "company",
            "location",
            "description",
            "responsibilities",
            "requirements",
            "salary_from",
            "salary_to",
            "currency",
            "show_salary",
            "employment_type",
            "work_format",
            "experience_required",
            "is_active",
        ]

class VacancySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    salary_display = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "title",
            "company",
            "location",
            "description",
            "responsibilities",
            "requirements",
            "salary_from",
            "salary_to",
            "currency",
            "show_salary",
            "employment_type",
            "work_format",
            "experience_required",
            "is_active",
            "views",
            "created_at",
            "updated_at",
            "author",
            "salary_display",
        ]

    def get_salary_display(self, obj):
        return obj.salary_display()

class ResumeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating resumes - file is required"""
    class Meta:
        model = Resume
        fields = [
            "full_name",
            "file",
        ]


class ResumeSerializer(serializers.ModelSerializer):
    """Serializer for reading resumes - only file_url"""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = [
            "full_name",
            "file_url",
        ]
        read_only_fields = ["file_url"]

    def get_file_url(self, obj):
        return obj.file_url



class VacancyShortSerializer(serializers.ModelSerializer):
    """Short vacancy info for applications"""
    class Meta:
        model = Vacancy
        fields = ["id", "title", "company", "location"]


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    vacancy = VacancyShortSerializer(read_only=True)
    resume = ResumeSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "applicant",
            "vacancy",
            "resume",
            "cover_letter",
            "status",
            "applied_at",
            "updated_at",
        ]


class EmployerProfileSerializer(serializers.ModelSerializer):
    vacancies = VacancySerializer(many=True, read_only=True)
    applications = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "vacancies", "applications"]

    def get_applications(self, obj):
        qs = Application.objects.filter(vacancy__author=obj)
        return ApplicationCompactSerializer(qs, many=True).data


class SeekerProfileSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "resume"]

class ResumeShortSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ["full_name", "file_url"]

    def get_file_url(self, obj):
        return obj.file_url


class ApplicationCompactSerializer(serializers.ModelSerializer):
    vacancy_id = serializers.IntegerField(source="vacancy.id", read_only=True)
    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    resume = ResumeShortSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ["id", "vacancy_id", "vacancy_title", "status", "updated_at", "resume"]

class ApplicationCreateSerializer(serializers.ModelSerializer):
    resume_id = serializers.PrimaryKeyRelatedField(
        queryset=Resume.objects.all(),
        source="resume",
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Application
        fields = ["resume_id", "cover_letter"]



class FavoriteVacancySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    vacancy = VacancySerializer(read_only=True)
    vacancy_id = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(), source="vacancy", write_only=True
    )

    class Meta:
        model = FavoriteVacancy
        fields = ["id", "user", "vacancy", "vacancy_id", "added_at"]


class FavoriteListSerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer(read_only=True)
    class Meta:
        model = FavoriteVacancy
        fields = ["id", "vacancy", "added_at"]


class FavoriteToggleResponseSerializer(serializers.Serializer):
    message = serializers.CharField()