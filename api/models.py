from django.db import models
from django.core.validators import FileExtensionValidator
from accounts.models import CustomUser


class Vacancy(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
        ("fifo", "FIFO"),
        ("volunteer", "Volunteering"),
    ]

    WORK_FORMAT_CHOICES = [
        ("on_site", "On-site"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
        ("shift", "Shift work"),
    ]

    EXPERIENCE_CHOICES = [
        ("no_exp", "No experience"),
        ("1_3", "1–3 years"),
        ("3_6", "3–6 years"),
        ("6_plus", "6+ years"),
    ]

    title = models.CharField("Job title", max_length=200, db_index=True)
    company = models.CharField("Company", max_length=200, blank=True)
    location = models.CharField("Location", max_length=150, db_index=True)
    description = models.TextField("Description")
    responsibilities = models.TextField("Responsibilities", blank=True)
    requirements = models.TextField("Requirements", blank=True)

    salary_from = models.DecimalField("Salary from", max_digits=12, decimal_places=2, null=True, blank=True)
    salary_to = models.DecimalField("Salary to", max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField("Currency", max_length=10, default="TJS")
    show_salary = models.BooleanField("Show salary", default=True)

    employment_type = models.CharField("Employment type", max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, db_index=True)
    work_format = models.CharField("Work format", max_length=10, choices=WORK_FORMAT_CHOICES, db_index=True)
    experience_required = models.CharField("Experience", max_length=10, choices=EXPERIENCE_CHOICES, default="no_exp")

    is_active = models.BooleanField("Active", default=True)
    views = models.PositiveIntegerField("Views", default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="vacancies")

    class Meta:
        verbose_name = "Vacancy"
        verbose_name_plural = "Vacancies"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["location", "employment_type", "work_format"]),
        ]

    def __str__(self):
        company_name = self.company if self.company else "Unknown Company"
        return f"{self.title} в {company_name}"

    def increment_views(self):
        Vacancy.objects.filter(pk=self.pk).update(views=models.F("views") + 1)
        self.refresh_from_db()

    def salary_display(self):
        if not self.show_salary:
            return "By agreement"
        if self.salary_from and self.salary_to:
            return f"{self.salary_from} – {self.salary_to} {self.currency}"
        if self.salary_from:
            return f"от {self.salary_from} {self.currency}"
        if self.salary_to:
            return f"до {self.salary_to} {self.currency}"
        return "Not specified"


class Resume(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="resume")
    full_name = models.CharField("Full name", max_length=200)
    file = models.FileField(
        upload_to="resumes/", 
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text="Upload PDF or Word document (.pdf, .doc, .docx)"
    )

    class Meta:
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"

    def __str__(self):
        return self.full_name
    
    @property
    def file_url(self):
        if self.file:
            return self.file.url
        return None



class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="applications_sent")
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="applications_received")
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")

    cover_letter = models.TextField("Cover letter", blank=True)
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default="pending")

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("applicant", "vacancy")
        verbose_name = "Response"
        verbose_name_plural = "Responses"
        indexes = [
            models.Index(fields=["vacancy", "status"]),
        ]

    def __str__(self):
        return f"{self.applicant} → {self.vacancy.title}"

    def mark_reviewed(self):
        self.status = "reviewed"
        self.save(update_fields=["status", "updated_at"])

    def mark_accepted(self):
        self.status = "accepted"
        self.save(update_fields=["status", "updated_at"])

    def mark_rejected(self):
        self.status = "rejected"
        self.save(update_fields=["status", "updated_at"])

class FavoriteVacancy(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="favorites")
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="favorited_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "vacancy")
        verbose_name = "Featured vacancy"
        verbose_name_plural = "Featured vacancies"
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} Favorites {self.vacancy.title}"

    @staticmethod
    def is_favorited(user, vacancy):
        return FavoriteVacancy.objects.filter(user=user, vacancy=vacancy).exists()