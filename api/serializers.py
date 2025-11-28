from rest_framework import serializers
from .models import Company, Vacancy, Resume, Application
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"

class VacancyCreateSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source="company",
        write_only=True
    )

    class Meta:
        model = Vacancy
        fields = [
            "title",
            "company_id",
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
    company = CompanySerializer(read_only=True)
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

class ResumeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Resume
        fields = [
            "id",
            "user",
            "full_name",
            "desired_position",
            "location",
            "phone",
            "email",
            "salary_expectation",
            "experience_years",
            "about",
            "skills",
            "is_active",
            "created_at",
            "updated_at",
            "file_url",
        ]
    def get_file_url(self, obj):
        return obj.file.url if obj.file else None



class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    vacancy = serializers.StringRelatedField(read_only=True)
    resume = ResumeSerializer(read_only=True)
    resume_id = serializers.PrimaryKeyRelatedField(
        queryset=Resume.objects.all(), source="resume", write_only=True, required=False
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "applicant",
            "vacancy",
            "resume",
            "resume_id",
            "cover_letter",
            "status",
            "applied_at",
            "updated_at",
        ]


class CompanyWithVacanciesSerializer(serializers.ModelSerializer):
    vacancies = VacancySerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ["id", "name", "logo", "description", "website", "vacancies"]


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
        return obj.file.url if obj.file else None


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
        write_only=True
    )
    class Meta:
        model = Application
        fields = ["resume_id", "cover_letter"]