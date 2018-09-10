from django.contrib import admin
from .models import Person, Vaccine, Pet, AdoptionApplication
from .forms import PetForm


class PetAdmin(admin.ModelAdmin):
    form = PetForm


admin.site.register(Pet, PetAdmin)


# Register your models here.
admin.site.register(Person)
admin.site.register(Vaccine)
admin.site.register(AdoptionApplication)
