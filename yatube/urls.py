from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views

urlpatterns = [

    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path("", include("posts.urls")),
]

urlpatterns += [
        path('about/about-author/', views.flatpage, name='author'),
        path('about/about-spec/', views.flatpage, name='spec'),
] 
