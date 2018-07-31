from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=40, null=False)
    last_name = models.CharField(max_length=40, null=False)
    description = models.TextField()


class Address(models.Model):
    """
    As requested, uses many-to-one relationship with Person. However, it is
    possible for a person to have several addresses.
    """
    city = models.CharField(max_length=60)
    street = models.CharField(max_length=60, null=False)
    building_no = models.CharField(max_length=6, null=False)
    flat_no = models.CharField(max_length=6)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)


class Phone(models.Model):
    """
    As before, uses one-to-many relationship with Person, but several people
    may use the same phone number, especially at work.
    """
    phone_no = models.CharField(max_length=60, null=False)
    type = models.CharField(max_length=40)


class Email(models.Model):
    """
    As before, uses one-to-many relationship with Person, but several people
    may use the same email, especially at work.
    """
    email_address = models.CharField(max_length=60, null=False)
    type = models.CharField(max_length=40)


class Group(models.Model):
    name = models.CharField(max_length=40, null=False, unique=True)
    person = models.ManyToManyField(Person, related_name="persons_in_groups")
