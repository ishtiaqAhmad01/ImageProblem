from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ----------------------------------School-------------------------------------------------

class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)


    class Meta:
        verbose_name = "School"
        verbose_name_plural = "Schools"
        ordering = ["name"]
    
    def __str__(self):
        return self.name
    

# ----------------------------------User-------------------------------------------------

class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_UPLOADER = "uploader"
    ROLE_VIEWER = "viewer"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_UPLOADER, "Uploader"),
        (ROLE_VIEWER, "Viewer"),
    ]
    
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_UPLOADER)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="users")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

# ---------------------------------- ImageUpload -------------------------------------------------

class ImageUpload(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="image_uploads")
    image_file = models.ImageField(upload_to="images/%Y/%m/%d/")
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=512)
    duplicate_flag = models.BooleanField(null=True) 
    image_hash = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    attendence = models.PositiveIntegerField()
    head_count = models.PositiveIntegerField(null=True)
    
    class Meta:
        ordering = ["-upload_timestamp"]
        indexes = [
            models.Index(fields=["image_hash"]),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.user})"
    

# ---------------------------------- Notification -------------------------------------------------

class Notification(models.Model):
    TYPE_DUPLICATE_ALERT = "duplicate_alert"
    TYPE_DAILY_REPORT = "daily_report"
    TYPE_CHOICES = [
        (TYPE_DUPLICATE_ALERT, "Duplicate alert"),
        (TYPE_DAILY_REPORT, "Daily report"),
    ]

    image = models.ForeignKey(ImageUpload, null=True, blank=True, on_delete=models.SET_NULL, related_name="notifications")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField(null=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["type"]),
        ]
    
    def __str__(self):
        return f"Notification[{self.type}] to {self.user}"


# ---------------------------------- DailyReport -------------------------------------------------

class DailyReport(models.Model):
    report_date = models.DateField(unique=True)
    total_uploads = models.PositiveIntegerField(default=0)
    total_duplicates = models.PositiveIntegerField(default=0)
    report_path = models.FileField(upload_to="reports/%Y/%m/%d/")
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-report_date"]
    
    def __str__(self):
        return f"DailyReport {self.report_date} (uploads={self.total_uploads})"