from django.urls import path
from . import views

appurls = [
    # Schools
    path("schools/", views.SchoolListCreateAPIView.as_view(), name="school-list-create"),
    path("schools/<int:pk>/", views.SchoolDetailAPIView.as_view(), name="school-detail"),

    # Auth / Users
    path("auth/register/", views.RegisterAPIView.as_view(), name="register"),
    path("auth/login/", views.LoginAPIView.as_view(), name="login"),
    path("users/", views.UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", views.UserDetailAPIView.as_view(), name="user-detail"),

    # Images
    path("images/", views.ImageUploadListCreateAPIView.as_view(), name="image-list-create"),
    path("images/recent/", views.ImageUploadRecentAPIView.as_view(), name="image-recent"),
    path("images/<int:pk>/", views.ImageUploadDetailAPIView.as_view(), name="image-detail"),

    # Notifications
    path("notifications/", views.NotificationListCreateAPIView.as_view(), name="notif-list-create"),
    path("notifications/<int:pk>/", views.NotificationDetailAPIView.as_view(), name="notif-detail"),
    path("notifications/<int:pk>/mark-sent/", views.NotificationMarkSentAPIView.as_view(), name="notif-mark-sent"),

    # Reports
    path("reports/", views.DailyReportListCreateAPIView.as_view(), name="report-list-create"),
    path("reports/<int:pk>/", views.DailyReportDetailAPIView.as_view(), name="report-detail"),
    path("reports/summary/", views.DailyReportSummaryAPIView.as_view(), name="report-summary"),
]
