from django.contrib import admin
from django.urls import path, include
from app.urls import appurls

urlpatterns = [
    path('api/', include(appurls)),
    path('admin/', admin.site.urls),
]
