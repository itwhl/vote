"""vote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from polls.views import show_subjects, show_teachers, praise_or_criticize, login, register, logout, send_mobile_code, \
    get_stat_date, export_excel, show_index

urlpatterns = [
    path('',show_index),
    path('admin/', admin.site.urls),
    path('api/subjects/', show_subjects),
    path('api/teachers/', show_teachers),
    path('parise/', praise_or_criticize),
    path('criticize/', praise_or_criticize),
    path('login/', login),
    path('register/', register),
    path('logout/', logout),
    path('mobile/<str:tel>', send_mobile_code),
    path('data/', get_stat_date),
    path('export', export_excel),
]

# 开发测试性能
if settings.DEBUG:

    import debug_toolbar

    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))