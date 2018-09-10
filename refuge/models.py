from django.db import models
from django.conf import settings


class Person(models.Model):
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=70)
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=12)
    email = models.EmailField(unique=True)
    home = models.TextField()

    def __str__(self):
        return f'{self.name} {self.last_name}'


class Vaccine(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Pet(models.Model):
    vaccine = models.ManyToManyField(Vaccine, blank=True)
    name = models.CharField(max_length=50)
    sex = models.CharField(max_length=10)
    age = models.PositiveIntegerField()
    rescue_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class PetCharacteristic(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    key = models.CharField(max_length=300)
    value = models.CharField(max_length=200)

    class Meta:
        verbose_name = "PetCharacteristic"
        verbose_name_plural = "PetCharacteristics"

    def __str__(self):
        return f'{self.key} {self.value}'


class AdoptionApplication(models.Model):
    person = models.ForeignKey(
        Person, null=False, blank=False, on_delete=models.CASCADE)
    reasons = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.reasons

    def get_adoption(user):
        return AdoptionApplication.objects.filter(
            created_by=user).order_by('id')
