from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("user.urls")),
    path("integrations/", include("integrations.urls")),
    path("", include("integrations.urls"))
]
