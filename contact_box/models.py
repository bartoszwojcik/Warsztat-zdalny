from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=40, null=False)
    last_name = models.CharField(max_length=40, null=False)
    description = models.TextField()
    avatar = models.ImageField(upload_to="media/", null=True)


class Address(models.Model):
    """
    Possibility to add addresses to a person had been requested, so the initial
    "many person-to-one address" relation was abandoned in favour of
    many-to-many relationship with persons. It is possible for a person to have
    several addresses and it is possible that many people live under the same
    address.
    The current version does not remove addresses when a person is deleted.
    """
    city = models.CharField(max_length=60)
    street = models.CharField(max_length=60, null=False)
    building_no = models.CharField(max_length=6, null=False)
    flat_no = models.CharField(max_length=6)
    person = models.ManyToManyField(Person, related_name="person_addresses")


class Phone(models.Model):
    """
    Uses one-to-many relationship with Person, but several people
    may use the same phone number, especially at work.
    """
    phone_no = models.CharField(max_length=60, null=False)
    type = models.CharField(max_length=40)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)


class Email(models.Model):
    """
    Uses one-to-many relationship with Person, but several people
    may use the same email, especially at work.
    """
    email_address = models.CharField(max_length=60, null=False)
    type = models.CharField(max_length=40)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)


class Group(models.Model):
    name = models.CharField(max_length=40, null=False, unique=True)
    person = models.ManyToManyField(Person, related_name="persons_in_groups")
