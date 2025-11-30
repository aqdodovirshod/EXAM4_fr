from django.urls import path
from .views import (
    VacancyListCreateView,
    VacancyRetrieveUpdateDeleteView,
    ResumeListCreateView,
    ResumeRetrieveUpdateDeleteView,
    ApplicationCreateView,
    ApplicationListView,
    ApplicationAcceptView,
    ApplicationRejectView,
    ApplicationReviewView,
    FavoriteVacancyListView,
    FavoriteVacancyToggleView,
    FavoriteVacancyDeleteView,
    UserProfileView,
)

urlpatterns = [
    path("vacancies/", VacancyListCreateView.as_view(), name="vacancy-list-create"),
    path("vacancies/<int:pk>/", VacancyRetrieveUpdateDeleteView.as_view(), name="vacancy-detail"),

    path("resumes/", ResumeListCreateView.as_view(), name="resume-list-create"),
    path("resumes/<int:pk>/", ResumeRetrieveUpdateDeleteView.as_view(), name="resume-detail"),

    path("vacancies/<int:vacancy_id>/apply/", ApplicationCreateView.as_view(), name="application-create"),
    path("applications/", ApplicationListView.as_view(), name="application-list"),
    path("applications/<int:application_id>/accept/", ApplicationAcceptView.as_view(), name="application-accept"),
    path("applications/<int:application_id>/reject/", ApplicationRejectView.as_view(), name="application-reject"),
    path("applications/<int:application_id>/review/", ApplicationReviewView.as_view(), name="application-review"),

    path("vacancies/<int:vacancy_id>/favorite/", FavoriteVacancyToggleView.as_view(), name="favorite-toggle"),
    path("favorites/", FavoriteVacancyListView.as_view(), name="favorite-list"),
    path("vacancies/<int:vacancy_id>/favorite/delete/", FavoriteVacancyDeleteView.as_view(), name="favorite-delete"),

    path("my-account/", UserProfileView.as_view(), name="user-profile"),
]
