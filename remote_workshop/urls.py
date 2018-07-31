"""remote_workshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, re_path
from contact_box.views import new_person, view_all, modify_person,\
    delete_person, show_person

urlpatterns = [
    path('admin/', admin.site.urls),
    path("new/", new_person, name="new_person"),
    re_path(
        r"""^modify/(?P<id>(\d)+)$""", modify_person, name="modify_person"
    ),
    re_path(
        r"""^delete/(?P<id>(\d)+)$""", delete_person, name="delete_person"
    ),
    re_path(r"""^show/(?P<id>(\d)+)$""", show_person, name="show_person"),
    path('', view_all, name="view_all"),
]

