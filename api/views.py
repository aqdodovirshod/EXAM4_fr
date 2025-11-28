from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Company
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Vacancy, Resume

from rest_framework import viewsets


from .serializers import (
    VacancySerializer, 
    ResumeSerializer, 
    ApplicationSerializer,
    CompanyWithVacanciesSerializer,
    EmployerProfileSerializer,
    SeekerProfileSerializer,
    VacancyCreateSerializer,
    ApplicationCreateSerializer,
)

class CompanyDetailWithVacanciesView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyWithVacanciesSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == "seeker":
            serializer = SeekerProfileSerializer(user)
        else:
            serializer = EmployerProfileSerializer(user)
        return Response(serializer.data)


class VacancyListCreateView(generics.ListCreateAPIView):
    queryset = Vacancy.objects.order_by("-created_at")
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VacancyCreateSerializer
        return VacancySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        title = self.request.query_params.get("t")
        if title:
            qs = qs.filter(title__icontains=title)

        date_obj = self.request.query_params.get("d")
        if date_obj:
            filter_date = datetime.strptime(date_obj, "%Y-%m-%d")
            qs = qs.filter(
                created_at__year=filter_date.year,
                created_at__month=filter_date.month,
                created_at__day=filter_date.day,
            )
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'employer':
            raise PermissionDenied("Only employers can create vacancies")
        serializer.save(author=self.request.user)

class VacancyRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        vacancy = self.get_object()
        vacancy.increment_views()
        serializer = self.get_serializer(vacancy)
        return Response(serializer.data)

    def perform_update(self, serializer):
        vacancy = self.get_object()
        if vacancy.author != self.request.user:
            raise PermissionDenied("You can only edit your own vacancies")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own vacancies")
        instance.delete()


class ResumeListCreateView(generics.ListCreateAPIView):
    queryset = Resume.objects.filter(is_active=True).order_by("-id")  
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        skill = self.request.query_params.get("skill")
        if skill:
            qs = qs.filter(skills__name__icontains=skill)  
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'seeker':
            raise PermissionDenied("Only seekers can create resumes")
        serializer.save(user=self.request.user)


class ResumeRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        resume = self.get_object()
        if resume.user != self.request.user:
            raise PermissionDenied("You can only edit your own resume")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own resume")
        instance.delete()


class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.role != 'seeker':
            raise PermissionDenied("Only seekers can apply for vacancies")
        vacancy = get_object_or_404(Vacancy, id=self.kwargs["vacancy_id"])
        serializer.save(applicant=self.request.user, vacancy=vacancy)

class CompanyListView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyWithVacanciesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CompanyCreateView(generics.CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyWithVacanciesSerializer  
    permission_classes = [IsAuthenticated]  


