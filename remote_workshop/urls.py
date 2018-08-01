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
    delete_person, show_person, add_address, modify_address, delete_address,\
    add_email, modify_email, delete_email, add_phone, modify_phone,\
    delete_phone, new_group, show_groups, display_group

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
    re_path(
        r"""^modify/(?P<id>(\d)+)/add_address/$""",
        add_address, name="add_address"
    ),
    re_path(
        r"""^modify/(?P<id>(\d)+)/modify_address/(?P<address_id>(\d)+)$""",
        modify_address, name="modify_address"
    ),
    re_path(
        r"""^modify/(?P<id>(\d)+)/delete_address/(?P<address_id>(\d)+)$""",
        delete_address, name="delete_address"
    ),
    re_path(
        r"""^modify/(?P<id>(\d)+)/add_phone/$""",
        add_phone, name="add_phone"
    ),
    re_path(
        r"""^modify/(?P<id>(\d)+)/modify_phone/(?P<phone_id>(\d)+)$""",
        modify_phone, name="modify_phone"
    ),
    re_path(
        r"""^modify/(?P<id>(\d)+)/delete_phone/(?P<phone_id>(\d)+)$""",
        delete_phone, name="delete_phone"
    ),
    re_path(
        r"""^modify/(?P<id>(\d)+)/add_email/$""",
        add_email, name="add_email"
    ),
    re_path(
        r"""^modify/(?P<id>(\d)+)/modify_email/(?P<email_id>(\d)+)$""",
        modify_email, name="modify_email"
    ),
    re_path(
        r"""^modify/(?P<id>(\d)+)/delete_email/(?P<email_id>(\d)+)""",
        delete_email, name="delete_email"
    ),
    path("new_group/", new_group, name="new_group"),
    path("show_groups/", show_groups, name="show_groups"),
    re_path(
        r"""^display_group/(?P<id>(\d)+)$""", display_group,
        name="display_group"
    ),
]

