from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Vacancy, Resume, Application, FavoriteVacancy

from rest_framework import viewsets


from .serializers import (
    VacancySerializer, 
    ResumeSerializer,
    ResumeCreateSerializer,
    ApplicationSerializer,
    FavoriteToggleResponseSerializer,
    FavoriteListSerializer,
    EmployerProfileSerializer,
    SeekerProfileSerializer,
    VacancyCreateSerializer,
    ApplicationCreateSerializer,
    ApplicationCompactSerializer,
)


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
    queryset = Resume.objects.all().order_by("-id")  
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ResumeCreateSerializer
        return ResumeSerializer

    def perform_create(self, serializer):
        if self.request.user.role != 'seeker':
            raise PermissionDenied("Only seekers can create resumes")
        serializer.save(user=self.request.user)


class ResumeRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resume.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ResumeCreateSerializer
        return ResumeSerializer

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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'seeker':
            raise PermissionDenied("Only seekers can apply for vacancies")
        vacancy = get_object_or_404(Vacancy, id=self.kwargs["vacancy_id"])
        
        # Check if user already applied
        if Application.objects.filter(applicant=self.request.user, vacancy=vacancy).exists():
            raise PermissionDenied("You have already applied for this vacancy")
        
        # Automatically get user's resume if exists
        resume = None
        if hasattr(self.request.user, 'resume'):
            resume = self.request.user.resume
        
        serializer.save(applicant=self.request.user, vacancy=vacancy, resume=resume)


class ApplicationListView(generics.ListAPIView):
    """List applications - for employer: all applications to their vacancies, for seeker: their own applications"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'employer':
            # Get all applications for employer's vacancies
            return Application.objects.filter(
                vacancy__author=self.request.user
            ).order_by("-applied_at")
        elif self.request.user.role == 'seeker':
            # Get seeker's own applications
            return Application.objects.filter(
                applicant=self.request.user
            ).order_by("-applied_at")
        else:
            raise PermissionDenied("Invalid user role")


class ApplicationAcceptView(APIView):
    """Accept an application"""
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        if request.user.role != 'employer':
            raise PermissionDenied("Only employers can accept applications")
        
        application = get_object_or_404(Application, id=application_id)
        
        # Check if application belongs to employer's vacancy
        if application.vacancy.author != request.user:
            raise PermissionDenied("You can only accept applications for your own vacancies")
        
        application.mark_accepted()
        return Response(
            {"message": "Application accepted", "status": application.status},
            status=status.HTTP_200_OK
        )


class ApplicationRejectView(APIView):
    """Reject an application"""
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        if request.user.role != 'employer':
            raise PermissionDenied("Only employers can reject applications")
        
        application = get_object_or_404(Application, id=application_id)
        
        # Check if application belongs to employer's vacancy
        if application.vacancy.author != request.user:
            raise PermissionDenied("You can only reject applications for your own vacancies")
        
        application.mark_rejected()
        return Response(
            {"message": "Application rejected", "status": application.status},
            status=status.HTTP_200_OK
        )


class FavoriteVacancyToggleView(generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = FavoriteToggleResponseSerializer

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return FavoriteToggleResponseSerializer()
        return super().get_serializer(*args, **kwargs)

    def post(self, request, vacancy_id):
        if request.user.role != 'seeker':
            raise PermissionDenied("Only seekers can add vacancies to favorites")
        vacancy = get_object_or_404(Vacancy, id=vacancy_id)
        if FavoriteVacancy.is_favorited(request.user, vacancy):
            FavoriteVacancy.objects.filter(user=request.user, vacancy=vacancy).delete()
            return Response({"message": "Removed from favorites"}, status=status.HTTP_200_OK)
        else:
            FavoriteVacancy.objects.create(user=request.user, vacancy=vacancy)
            return Response({"message": "Added to favorites"}, status=status.HTTP_201_CREATED)
        

class FavoriteVacancyListView(generics.ListAPIView):
    serializer_class = FavoriteListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteVacancy.objects.filter(user=self.request.user)

class FavoriteVacancyDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, vacancy_id):
        if request.user.role != 'seeker':
            raise PermissionDenied("Only seekers can delete favorites")
        vacancy = get_object_or_404(Vacancy, id=vacancy_id)
        favorite = FavoriteVacancy.objects.filter(user=request.user, vacancy=vacancy).first()
        if not favorite:
            return Response({"message": "Not in favorites"}, status=status.HTTP_404_NOT_FOUND)
        favorite.delete()
        return Response({"message": "Deleted from favorites"}, status=status.HTTP_200_OK)

