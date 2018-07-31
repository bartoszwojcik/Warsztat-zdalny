from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from contact_box.models import Person, Group, Address, Phone, Email

# Simple general website skeleton with added menu
start_template = """
<html>
    <body>
        <h4 style="margin-bottom: 0px">Contact Box</h4>
        <ul style="list-style-type: none;">
            <li style="display: inline;">
                <a href="/">Home</a> &nbsp
            </li>
            <li style="display: inline;">
                <a href="/new">Dodaj osobę</a> &nbsp
                </li>
            <li style="display: inline;">
                <a href="/new_group">Utwórz grupę</a> &nbsp
            </li>
        </ul>
        <p>&nbsp</p>
        <div>
            {}
        </div>
    </body>
</html>
"""

person_list_table = """
<table style="border: 1px solid black; border-collapse: collapse" >
    <thead>
        <tr style="border: 1px solid black; border-collapse: collapse">
            <th style="border: 1px solid black">Imię i nazwisko &nbsp</th>
            <th style="border: 1px solid black">Edycja &nbsp</th>
            <th style="border: 1px solid black">Usuwanie &nbsp</th>
        </tr>
    </thead>
    <tbody>
        {}
    </tbody>
</table>
"""


# def check_room_bookings(room_object):
#     room_bookings = Booking.objects.filter(
#         room=room_object, date__gte=today
#     ).order_by("date")
#
#     html = ""
#     if room_bookings:
#         html += "<ul>"
#         # Add reserved dates
#         for booking in room_bookings:
#             html += f"<li>{booking.date}</li>"
#         html += "</ul>"
#     else:
#         html += "Brak rezerwacji."
#     return html


@csrf_exempt
def new_person(request):
    person_add_form = """
    <h2>Dodawanie nowej osoby</h2>
    <form action="#" method="POST">
        <label>Imię:
            <input type="text" name="first_name">
        </label><br><br>
        <label>Nazwisko:
            <input type="text" name="last_name">
        </label><br><br>
        <label>Opis:
            <input type="text" name="description">
        </label><br><br>
        <button type="submit" name="submit">Submit</button>
    </form>
    """

    if request.method == "GET":
        return HttpResponse(start_template.format(person_add_form))
    elif request.method == "POST":
        if request.POST.get("first_name") and request.POST.get("last_name"):

            a_new_person = Person.objects.create(
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                description=request.POST.get("description")
            )
            return redirect(
                reverse("show_person", kwargs={"id": a_new_person.id})
            )
        else:
            return HttpResponse("Brakuje imienia lub nazwiska.")


def show_person(request, id):
    try:
        person = Person.objects.get(id=id)

        person_display_html = f"""
        <h2>{person.first_name} {person.last_name}</h2>
        <p>Opis: {person.description}</p>
        <p><a href="/modify/{person.id}">Modyfikuj dane</a></p>
        """

        return HttpResponse(start_template.format(person_display_html))
    except ObjectDoesNotExist:
        return HttpResponse("Nie ma osoby o tym numerze.")


def view_all(request):
    person_data = Person.objects.all().order_by("first_name")

    table_rows = ""
    for person in person_data:

        table_rows += f"""
        <tr style="border: 1px solid black">
            <td>
                <a href="/show/{person.id}">
                {person.first_name} {person.last_name}
                </a>
            </td>
            <td style="text-align: center;">
                <a href="/modify/{person.id}">Modyfikuj</a>
            </td>
            <td style="text-align: center;">
                <a href="/delete/{person.id}">Usuń</a>
            </td>
        </tr>
        """

    return HttpResponse(
        start_template.format(person_list_table.format(table_rows))
    )


@csrf_exempt
def modify_person(request, id):

    try:
        person_data = Person.objects.get(id=id)
    except ObjectDoesNotExist:
        return Http404

    person_modify_html = f"""
        <form action="#" method="POST">
            <label>Imię:
                <input type="text" name="new_first_name"
                 value={person_data.first_name}>
            </label><br><br>
            <label>Nazwisko:
                <input type="text" name="new_last_name"
                 value={person_data.last_name}>
            </label><br><br>
            <label>Opis:
                <input type="text" name="new_description"
                 value={person_data.description}>
            </label><br><br>
            <input type="submit" name="send" value="Modyfikuj">
        </form>
        """

    if request.method == "GET":
        return HttpResponse(start_template.format(person_modify_html))
    elif request.method == "POST":
        if request.POST.get("new_first_name") \
                and request.POST.get("new_last_name"):
            person_data.first_name = request.POST.get("new_first_name")
            person_data.last_name = request.POST.get("new_last_name")
            person_data.description = request.POST.get("new_description")
            person_data.save()
            return redirect(reverse("view_all"))
        else:
            return HttpResponse("W formularzu brakuje imienia lub nazwiska.")


def delete_person(request, id):
    try:
        marked_person = Person.objects.get(id=id)
        marked_person.delete()
        return redirect(reverse("view_all"))
    except ObjectDoesNotExist:
        return HttpResponse("Nie ma osoby o tym numerze.")

