from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError
from django.db.models import Q, Count
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from contact_box.models import Person, Group, Address, Phone, Email

# Warning: image uploads are simplified. They do not use unique user catalogues
# and there is currently no file-deletion system.

# Simple general website skeleton with added menu
start_template = """
<html>
    <body>
        <h4 style="margin-bottom: 0px">Contact Box</h4>
        <ul style="list-style-type: none;">
            <li style="display: inline;">
                <a href="/">Home</a> &nbsp;
            </li>
            <li style="display: inline;">
                <a href="/new">Dodaj osobę</a> &nbsp;
                </li>
            <li style="display: inline;">
                <a href="/new_group">Utwórz grupę</a> &nbsp;
            </li>
            <li style="display: inline;">
                <a href="/show_groups">Lista grup</a> &nbsp;
            </li>
            <li style="display: inline;">
                <a href="/group_search">Przeszukaj grupy</a> &nbsp;
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


# Functions for generating html tables
def gen_address_table(person_object):
    address_data = Address.objects.filter(person=person_object)
    if address_data:
        address_table = """
        <table style="border: 1px solid black; border-collapse: collapse">
            <thead>
                <tr style="border: 1px solid black; border-collapse: collapse">
                    <th style="border: 1px solid black">Ulica</th>
                    <th style="border: 1px solid black">Miasto</th>
                    <th style="border: 1px solid black">Zmień</th>
                    <th style="border: 1px solid black">Usuń</th>
                </tr>
            <tbody>
        """

        for address in address_data:
            address_table += f"""
            <tr>
                <td>{address.street} {address.building_no}"""

            if address.flat_no:
                address_table += f""" m. {address.flat_no}"""

            # Links are built based on existing path
            address_table += f"""</td>
            <td>{address.city}</td>
            <td>
            <a href="/modify/{person_object.id}/modify_address/{address.id}">
            Zmień</a>
            </td>
            <td>
            <a href="/modify/{person_object.id}/delete_address/{address.id}">
            Usuń</a>
            </td>
            </tr>
            """

        address_table += """
            </tbody>
        </table>
        """
        return address_table
    else:
        return "Brak adresów."


def gen_phone_table(person_object):
    phone_data = Phone.objects.filter(person=person_object)
    if phone_data:
        phone_table = """
        <table style="border: 1px solid black; border-collapse: collapse">
            <thead>
                <tr style="border: 1px solid black; border-collapse: collapse">
                    <th style="border: 1px solid black">Numer telefonu</th>
                    <th style="border: 1px solid black">Typ</th>
                    <th style="border: 1px solid black">Zmień</th>
                    <th style="border: 1px solid black">Usuń</th>
                </tr>
            <tbody>
        """

        for phone in phone_data:
            # Links are built based on existing path
            phone_table += f"""
            <tr>
                <td>{phone.phone_no}</td>
                <td>{phone.type}</td>
                <td>
                <a href="/modify/{person_object.id}/modify_phone/{phone.id}">
                Zmień</a>
                </td>
                <td>
                <a href="/modify/{person_object.id}/delete_phone/{phone.id}">
                Usuń</a>
                </td>
            </tr>
            """

        phone_table += """
            </tbody>
        </table>
        """
        return phone_table
    else:
        return "Brak telefonów."


def gen_email_table(person_object):
    email_data = Email.objects.filter(person=person_object)
    if email_data:
        email_table = """
        <table style="border: 1px solid black; border-collapse: collapse">
            <thead>
                <tr style="border: 1px solid black; border-collapse: collapse">
                    <th style="border: 1px solid black">Adres e-mail</th>
                    <th style="border: 1px solid black">Typ</th>
                    <th style="border: 1px solid black">Zmień</th>
                    <th style="border: 1px solid black">Usuń</th>
                </tr>
            <tbody>
        """

        for email in email_data:
            # Links are built based on existing path
            email_table += f"""
            <tr>
                <td>
                    <a href="mailto:{email.email_address}">
                    {email.email_address}</a>
                </td>
                <td>{email.type}</td>
                <td>
                <a href="/modify/{person_object.id}/modify_email/{email.id}">
                Zmień</a>
                </td>
                <td>
                <a href="/modify/{person_object.id}/delete_email/{email.id}">
                Usuń</a>
                </td>
            </tr>
            """

        email_table += """
            </tbody>
        </table>
        """
        return email_table
    else:
        return "Brak adresów e-mail."


# Function for testing whether id is valid
def check_id(type, tested_id):
    """
    Function for testing whether id is valid.
    :param type: string, one of: "person", "address", "phone", "email" or
                 "group"
    :param tested_id: integer
    :return: matching QuerySet (passed) or HttpResponse (failed)
    """
    if type == "person":
        person_data = Person.objects.get(id=tested_id)
        if person_data:
            return person_data
        else:
            return HttpResponse("Nie ma osoby o takim id.")
    elif type == "address":
        address_data = Address.objects.get(id=tested_id)
        if address_data:
            return address_data
        else:
            return HttpResponse("Nie ma adresu o takim id.")
    elif type == "email":
        email_data = Email.objects.get(id=tested_id)
        if email_data:
            return email_data
        else:
            return HttpResponse("Nie ma e-maila o takim id.")
    elif type == "phone":
        phone_data = Phone.objects.get(id=tested_id)
        if phone_data:
            return phone_data
        else:
            return HttpResponse("Nie ma numeru teleofnu o takim id.")
    elif type == "group":
        group_data = Group.objects.get(id=tested_id)
        if group_data:
            return group_data
        else:
            return HttpResponse("Nie ma grupy o takim id.")
    else:
        return HttpResponse("Nieznany typ obiektu.")


# Views
@csrf_exempt
def new_person(request):
    person_add_form = """
    <h2>Dodawanie nowej osoby</h2>
    <form action="#" method="POST" enctype="multipart/form-data">
        <label>Imię:
            <input type="text" name="first_name" maxlength="40">
        </label><br><br>
        <label>Nazwisko:
            <input type="text" name="last_name" maxlength="40">
        </label><br><br>
        <label>Opis:
            <input type="text" name="description">
        </label><br><br>
        <label>Obrazek:
            <input type="file" name="avatar">
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
                description=request.POST.get("description"),
                avatar=request.FILES.get("avatar")
            )
            return redirect(
                reverse("show_person", kwargs={"id": a_new_person.id})
            )
        else:
            return HttpResponse("Brakuje imienia lub nazwiska.")


def show_person(request, id):
    try:
        person_data = Person.objects.get(id=id)
    except ObjectDoesNotExist:
        return HttpResponse("Nie ma osoby o tym numerze.")

    image = ""
    if person_data.avatar:
        image = f"""<img src=/media/{person_data.avatar} 
                style="max-width: 200px; max-height: 200px">
                </img><br><br>"""

    person_display_html = f"""
    <h2>{person_data.first_name} {person_data.last_name}</h2>
    {image}
    <p>Opis: {person_data.description}</p><br>
    <p><a href="/modify/{person_data.id}">Modyfikuj dane</a></p><br>
    <h4>Adresy:</h4>
    {gen_address_table(person_data)}
    <br>
    <h4>Numery telefonu:</h4>
    {gen_phone_table(person_data)}
    <br>
    <h4>Adresy e-mail:</h4>
    {gen_email_table(person_data)}
    <br>
    """

    return HttpResponse(start_template.format(person_display_html))


def view_all(request):
    person_data = Person.objects.all().order_by("first_name", "last_name")

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
        return HttpResponse("Nie ma osoby o tym numerze.")

    person_contact_data = f"""
    <h4>Adresy:</h4>
    {gen_address_table(person_data)}
    <p><a href="{person_data.id}/add_address/">Dodaj nowy adres</a></p><br>
    <h4>Numery telefonu:</h4>
    {gen_phone_table(person_data)}
    <p><a href="{person_data.id}/add_phone/">Dodaj nowy numer telefonu</a></p><br>
    <h4>Adresy e-mail:</h4>
    {gen_email_table(person_data)}
    <p><a href="{person_data.id}/add_email/">Dodaj nowy adres e-mail</a></p><br>
    """

    image = ""
    if person_data.avatar:
        image = f"""<img src=/media/{person_data.avatar} 
            style="max-width: 200px; max-height: 200px">
            </img><br><br>"""

    person_modify_html = f"""
        <h2>{person_data.first_name} {person_data.last_name}</h2>
        <form action="#" method="POST" enctype="multipart/form-data">
            {image}
            <label>Imię:
                <input type="text" name="new_first_name" maxlength="40"
                 value="{person_data.first_name}">
            </label><br><br>
            <label>Nazwisko:
                <input type="text" name="new_last_name" maxlength="40"
                 value="{person_data.last_name}">
            </label><br><br>
            <label>Opis:
                <input type="text" name="new_description"
                 value="{person_data.description}">
            </label><br><br>
            <label>Nowy obrazek:
            <input type="file" name="new_avatar">
            <br><br>
            <label>Usunąć obrazek?
                <select name="remove_avatar">
                    <option value="1">Tak</option>
                    <option selected value="0">Nie</option>
                </select><br><br>
            </label>
            <input type="submit" name="send" value="Modyfikuj">
        </form>
        {person_contact_data}
        """

    if request.method == "GET":
        return HttpResponse(start_template.format(person_modify_html))
    elif request.method == "POST":
        if request.POST.get("new_first_name") \
                and request.POST.get("new_last_name"):
            person_data.first_name = request.POST.get("new_first_name")
            person_data.last_name = request.POST.get("new_last_name")
            person_data.description = request.POST.get("new_description")
            if request.FILES.get("new_avatar"):
                person_data.avatar = request.FILES.get("new_avatar")
            if int(request.POST.get("remove_avatar")) == 1:
                person_data.avatar = None
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


# Address functions
@csrf_exempt
def add_address(request, id):
    person_data = check_id("person", id)

    address_add_form = f"""
        <h2>
        Nowy adres dla: {person_data.first_name} {person_data.last_name}
        </h2>
        <form action="#" method="POST">
            <label>Ulica:
                <input type="text" name="new_street" maxlength="60">
            </label><br><br>
            <label>Numer budynku:
                <input type="text" name="new_building_no" maxlength="6">
            </label><br><br>
            <label>Numer mieszkania:
                <input type="text" name="new_flat_no" maxlength="6">
            </label><br><br>
            <label>Miasto:
                <input type="text" name="new_city" maxlength="60">
            </label><br><br>
            <button type="submit" name="submit">Utwórz</button>
        </form>
        """

    if request.method == "GET":
        return HttpResponse(start_template.format(address_add_form))
    elif request.method == "POST":
        if request.POST.get("new_street") \
                and request.POST.get("new_building_no"):
            try:
                a_new_address = Address.objects.create(
                    street=request.POST.get("new_street"),
                    building_no=request.POST.get("new_building_no"),
                    flat_no=request.POST.get("new_flat_no"),
                    city=request.POST.get("new_city")
                )
                a_new_address.person.add(person_data)
            except DataError:
                return HttpResponse("Nieprawidłowe dane.")
            return redirect(
                reverse("show_person", kwargs={"id": person_data.id})
            )
        else:
            return HttpResponse("Ulica i numer budynku są wymagane.")


@csrf_exempt
def modify_address(request, id, address_id):
    person_data = check_id("person", id)
    address_data = check_id("address", address_id)

    address_modify_form = f"""
            <h2>
            Zmiana adresu dla: {person_data.first_name} {person_data.last_name}
            </h2>
            <form action="#" method="POST">
                <label>Ulica:
                    <input type="text" name="new_street" maxlength="60"
                     value="{address_data.street}">
                </label><br><br>
                <label>Numer budynku:
                    <input type="text" name="new_building_no" maxlength="6"
                     value="{address_data.building_no}">
                </label><br><br>
                <label>Numer mieszkania:
                    <input type="text" name="new_flat_no"
                     value="{address_data.flat_no}">
                </label><br><br>
                <label>Miasto:
                    <input type="text" name="new_city" maxlength="60"
                     value="{address_data.city}">
                </label><br><br>
                <button type="submit" name="submit">Zmień</button>
            </form>
            """

    if request.method == "GET":
        return HttpResponse(start_template.format(address_modify_form))
    elif request.method == "POST":
        if request.POST.get("new_street") \
                and request.POST.get("new_building_no"):
            try:
                address_data.street = request.POST.get("new_street")
                address_data.building_no = request.POST.get("new_building_no")
                address_data.flat_no = request.POST.get("new_flat_no")
                address_data.city = request.POST.get("new_city")
                address_data.save()

            except DataError:
                return HttpResponse("Nieprawidłowe dane.")
            return redirect(
                reverse("show_person", kwargs={"id": person_data.id})
            )
        else:
            return HttpResponse("Ulica i numer budynku są wymagane.")


def delete_address(request, id, address_id):
    person_data = check_id("person", id)
    address_data = check_id("address", address_id)
    address_data.delete()
    return redirect(
        reverse("show_person", kwargs={"id": person_data.id})
    )


# Email functions
@csrf_exempt
def add_email(request, id):
    person_data = check_id("person", id)

    email_add_form = f"""
            <h2>
            Nowy adres e-mail dla: {person_data.first_name}
             {person_data.last_name}
            </h2>
            <form action="#" method="POST">
                <label>Adres e-mail:
                    <input type="email" name="new_email_address" 
                     maxlength="60">
                </label><br><br>
                <label>Rodzaj adresu:
                    <input type="text" name="new_type" maxlength="40">
                </label><br><br>
                <button type="submit" name="submit">Utwórz</button>
            </form>
            """

    if request.method == "GET":
        return HttpResponse(start_template.format(email_add_form))
    elif request.method == "POST":
        if request.POST.get("new_email_address"):
            try:
                a_new_email = Email.objects.create(
                    email_address=request.POST.get("new_email_address"),
                    type=request.POST.get("new_type"),
                    person=person_data
                )
            except DataError:
                return HttpResponse("Nieprawidłowe dane.")
            return redirect(
                reverse("show_person", kwargs={"id": person_data.id})
            )
        else:
            return HttpResponse("Adres e-mail jest wymagany.")


@csrf_exempt
def modify_email(request, id, email_id):
    person_data = check_id("person", id)
    email_data = check_id("email", email_id)

    email_modify_form = f"""
                <h2>
                Zmiana adresu e-mail dla: {person_data.first_name}
                 {person_data.last_name}
                </h2>
                <form action="#" method="POST">
                    <label>Adres e-mail:
                        <input type="email" name="new_email_address" 
                         maxlength="60" value="{email_data.email_address}">
                    </label><br><br>
                    <label>Typ:
                        <input type="text" name="new_type" maxlength="40"
                         value="{email_data.type}">
                    </label><br><br>
                    <button type="submit" name="submit">Zmień</button>
                </form>
                """

    if request.method == "GET":
        return HttpResponse(start_template.format(email_modify_form))
    elif request.method == "POST":
        if request.POST.get("new_email_address"):
            try:
                email_data.email_address = request.POST.get(
                    "new_email_address"
                )
                email_data.type = request.POST.get("new_type")
                email_data.save()

            except DataError:
                return HttpResponse("Nieprawidłowe dane.")
            return redirect(
                reverse("show_person", kwargs={"id": person_data.id})
            )
        else:
            return HttpResponse("Adres e-mail jest wymagany.")


def delete_email(request, id, email_id):
    person_data = check_id("person", id)
    email_data = check_id("email", email_id)
    email_data.delete()
    return redirect(
        reverse("show_person", kwargs={"id": person_data.id})
    )


# Phone functions
@csrf_exempt
def add_phone(request, id):
    person_data = check_id("person", id)

    phone_add_form = f"""
            <h2>
            Nowy numer telefonu dla: {person_data.first_name}
             {person_data.last_name}
            </h2>
            <form action="#" method="POST">
                <label>Numer telefonu:
                    <input type="phone" name="new_phone_no" 
                     maxlength="60">
                </label><br><br>
                <label>Rodzaj adresu:
                    <input type="text" name="new_type" maxlength="40">
                </label><br><br>
                <button type="submit" name="submit">Utwórz</button>
            </form>
            """

    if request.method == "GET":
        return HttpResponse(start_template.format(phone_add_form))
    elif request.method == "POST":
        if request.POST.get("new_phone_no"):
            try:
                a_new_phone = Phone.objects.create(
                    phone_no=request.POST.get("new_phone_no"),
                    type=request.POST.get("new_type"),
                    person=person_data
                )
            except DataError:
                return HttpResponse("Nieprawidłowe dane.")
            return redirect(
                reverse("show_person", kwargs={"id": person_data.id})
            )
        else:
            return HttpResponse("Numer telefonu jest wymagany.")


@csrf_exempt
def modify_phone(request, id, phone_id):
    person_data = check_id("person", id)
    phone_data = check_id("phone", phone_id)

    phone_modify_form = f"""
                <h2>
                Zmiana numeru telefonu dla: {person_data.first_name}
                 {person_data.last_name}
                </h2>
                <form action="#" method="POST">
                    <label>Numer telefonu:
                        <input type="phone" name="new_phone_no" 
                         maxlength="60" value="{phone_data.phone_no}">
                    </label><br><br>
                    <label>Typ:
                        <input type="text" name="new_type" maxlength="40"
                         value="{phone_data.type}">
                    </label><br><br>
                    <button type="submit" name="submit">Zmień</button>
                </form>
                """

    if request.method == "GET":
        return HttpResponse(start_template.format(phone_modify_form))
    elif request.method == "POST":
        if request.POST.get("new_phone_no"):
            try:
                phone_data.phone_address = request.POST.get(
                    "new_phone_no"
                )
                phone_data.type = request.POST.get("new_type")
                phone_data.save()

            except DataError:
                return HttpResponse("Nieprawidłowe dane.")
            return redirect(
                reverse("show_person", kwargs={"id": person_data.id})
            )
        else:
            return HttpResponse("Numer telefonu jest wymagany.")


def delete_phone(request, id, phone_id):
    person_data = check_id("person", id)
    phone_data = check_id("phone", phone_id)
    phone_data.delete()
    return redirect(
        reverse("show_person", kwargs={"id": person_data.id})
    )


# Group functions
@csrf_exempt
def new_group(request):
    group_add_form = """
        <h2>Tworzenie nowej grupy</h2>
        <form action="#" method="POST">
            <label>Nazwa:
                <input type="text" name="name" maxlength="40">
            </label><br><br>
            <button type="submit" name="submit">Utwórz</button>
        </form>
        """

    if request.method == "GET":
        return HttpResponse(start_template.format(group_add_form))
    elif request.method == "POST":
        if request.POST.get("name"):

            Group.objects.create(name=request.POST.get("name"))
            return redirect(reverse("show_groups"))
        else:
            return HttpResponse("Brak nazwy grupy.")


def show_groups(request):
    group_data = Group.objects.all()

    if group_data:

        group_list_html = """<h2>Lista istniejących grup</h2>
        <p><a href="/search-groups">Przeszukaj grupy</a></p>
        <table style="border: 1px solid black; border-collapse: collapse">
                <thead>
                    <tr style="border: 1px solid black;
                     border-collapse: collapse">
                        <th style="border: 1px solid black">Nazwa grupy</th>
                        <th style="border: 1px solid black">
                        Liczba użytkowników
                        </th>
                        <th style="border: 1px solid black">
                        Dodaj członka
                        </th>
                    </tr>
                <tbody>
        """

        for group in group_data:
            person_count = Group.objects.filter(
                id=group.id
            ).annotate(count=Count('person'))[0].count

            group_list_html += f"""<tr style="border: 1px solid black;
             border-collapse: collapse">
            <td><a href="/display_group/{group.id}">{group.name}</a></td>
            <td style="text-align: right;">{person_count}</td>
            <td style="text-align: center;"><a href="/add_member/{group.id}">
            Dodaj
            </a></td>
            </tr>"""

        group_list_html += """
            </tbody>
        </table>
        """

        return HttpResponse(start_template.format(group_list_html))
    else:
        return HttpResponse(start_template.format("Brak istniejących grup."))


def display_group(request, id):
    group_data = check_id("group", id)
    member_data = group_data.person.all().order_by(
        "first_name", "last_name")

    group_display_html = f"""
    <h2>{group_data.name}</h2>
    <h4>Członkowie grupy:</h4>
    """

    if member_data:
        group_display_html += "<ul>"

        for member in member_data:
            group_display_html += f"""
            <li>{member.first_name} {member.last_name}</li>
            """

        group_display_html += "</ul>"
    else:
        group_display_html += "<p>Brak członków w tej grupie.</p>"

    group_display_html += f"""<p>
        <a href="/add_member/{group_data.id}">Dodaj osobę</a>
    </p>"""

    return HttpResponse(start_template.format(group_display_html))


@csrf_exempt
def add_member(request, id):
    group_data = check_id("group", id)
    persons_data = Person.objects.all().order_by("first_name", "last_name")

    member_add_form = f"""
            <h2>Dodawanie członka do grupy: {group_data.name}</h2>
            <form action="#" method="POST">
                <select name="new_member">Wybierz osobę:
                <option selected="true" disabled="true">Lista dostępnych</option>"""

    i = 0
    for person in persons_data:
        if person in group_data.person.all():
            continue
        else:
            member_add_form += f"""<option value="{person.id}">
            {person.first_name} {person.last_name}
            </option>
            """
            i += 1

    if i == 0:
        member_add_form = f"""
            <h2>Dodawanie członka do grupy: {group_data.name}</h2>
            <p>Brak osób możliwych do dodania.</p>"""
    else:
        member_add_form += """</select>
                    <button type="submit" name="submit">Dodaj</button>
                </form>
                """

    if request.method == "GET":
        return HttpResponse(start_template.format(member_add_form))
    elif request.method == "POST":
        if request.POST.get("new_member"):
            group_data.person.add(
                Person.objects.get(id=request.POST.get("new_member"))
            )
            return redirect(
                reverse("display_group", kwargs={"id": group_data.id})
            )
        else:
            return HttpResponse("Błąd.")


@csrf_exempt
def group_search(request):

    search_form_html = """
            <h2>Wyszukiwanie osób w grupach</h2>
            <br>
            <form method="POST" action="#">
                <label>Imię:
                    <input type="text" name="first_name">
                </label><br><br>
                <label>Nazwisko:
                    <input type="text" name="last_name">
                </label><br><br>
                <button type="submit" name="search">Szukaj</button>
            </form>
        """

    def search_results(s_first_name=None, s_last_name=None):

        person_data = None

        if s_first_name and s_last_name:
            person_data = Person.objects.filter(
                Q(first_name__icontains=s_first_name)
                & Q(last_name__icontains=s_last_name)
            ).order_by("first_name", "last_name")

        elif s_first_name:
            person_data = Person.objects.filter(
                Q(first_name__icontains=s_first_name)
            ).order_by("first_name", "last_name")

        elif s_last_name:
            person_data = Person.objects.filter(
                Q(last_name__icontains=s_last_name)
            ).order_by("first_name", "last_name")

        else:
            person_data = Person.objects.order_by("first_name", "last_name")

        # Build result list
        search_result_output = ""
        if not person_data:
            search_result_output = "Brak wyników."
        else:
            search_result_output += """Wyniki wyszukiwania:<br>
            <table style="border: 1px solid black; border-collapse: collapse">
                <thead>
                <tr style="border: 1px solid black; border-collapse: collapse">
                    <th style="border: 1px solid black">Imię i nazwisko</th>
                    <th style="border: 1px solid black">Grupy</th>
                    </tr>
                <tbody>
            """
            for person in person_data:
                search_result_output += f"""
                <tr style="border: 1px solid black; border-collapse: collapse">
                    <td><a href="/show/{person.id}">
                    {person.first_name} {person.last_name}</a></td>
                    <td style="border: 1px solid black">"""
                print(person)
                for group in person.persons_in_groups.all():
                    search_result_output += f"""
                        <a href="/display_group/{group.id}">{group.name}</a>
                        <br>"""
                search_result_output += """</td>
                </tr>
                """
            search_result_output += "</tbody></table>"
        return search_result_output

    # Function begins here

    if request.method == "GET":
        return HttpResponse(start_template.format(search_form_html))
    elif request.method == "POST":
        result_html = search_results(
            s_first_name=request.POST.get("first_name"),
            s_last_name=request.POST.get("last_name")
        )

        return HttpResponse(start_template.format(result_html))
