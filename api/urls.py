from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VacancyListCreateView,
    VacancyRetrieveUpdateDeleteView,
    ResumeListCreateView,
    ResumeRetrieveUpdateDeleteView,
    ApplicationCreateView,
    FavoriteVacancyListView,
    FavoriteVacancyToggleView,
    CompanyDetailWithVacanciesView,
    CompanyListView,
    CompanyCreateView,
    UserProfileView,
)


urlpatterns = [
    path("vacancies/", VacancyListCreateView.as_view(), name="vacancy-list-create"),
    path("vacancies/<int:pk>/", VacancyRetrieveUpdateDeleteView.as_view(), name="vacancy-detail"),

    path("resumes/", ResumeListCreateView.as_view(), name="resume-list-create"),
    path("resumes/<int:pk>/", ResumeRetrieveUpdateDeleteView.as_view(), name="resume-detail"),

    path("vacancies/<int:vacancy_id>/apply/", ApplicationCreateView.as_view(), name="application-create"),
    path("vacancies/<int:vacancy_id>/favorite/", FavoriteVacancyToggleView.as_view(), name="favorite-toggle"),
    path("favorites/", FavoriteVacancyListView.as_view(), name="favorite-list"),

    path("companies/", CompanyListView.as_view(), name="company-list"),
    path("companies/create/", CompanyCreateView.as_view(), name="company-create"),
    path("companies/<int:pk>/profile/", CompanyDetailWithVacanciesView.as_view(), name="company-profile"),
    path("my-account/", UserProfileView.as_view(), name="user-profile"),
]
