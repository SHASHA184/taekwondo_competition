"""
URL configuration for taekwondo_competition project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from competition.views import home, CompetitionListView, CompetitionDetailView, CompetitionCreateView, MemberListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('competitions/', CompetitionListView.as_view(), name='competition-list'),
    path('competition/<int:pk>/', CompetitionDetailView.as_view(),
         name='competition-detail'),
    path('competition/create/', CompetitionCreateView.as_view(),
         name='competition-create'),
    path('members/', MemberListView.as_view(), name='member-list'),
]
