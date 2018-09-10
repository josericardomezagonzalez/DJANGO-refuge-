

"""    def update_pet(self, pets):
        for p in pets:
            pet = Pet.objects.get(id=p.id)
            pet.adopted = True
            pet.save()"""

"""
@login_required
def list_pet(request):
    pets = serializers.serialize('json', Pet.objects.all())
    return JsonResponse(pets)
"""

"""
class PetCreate(FormView):
    model = Pet
    form_class = PetForm
    template_name = 'pet/pet_form.html'
    success_url = reverse_lazy('refuge:pet_list')

    def form_valid(self, form):
        pet = form.save(commit=False)    
        pet.create_by= User.objects.get(id=self.request.user.id)
        pet.save() 
        return HttpResponseRedirect(self.get_success_url())
"""


"""
def pet_view(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('refuge:pet_list')
    else:
        form = PetForm()

    return render(request, 'form/form.html', {'form': form})


def pet_list(request):
    pet = Pet.objects.all()
    context = {'pets': pet}
    return render(request, 'pet/pet_list.html', context)


def pet_edit(request, id_pet):
    pet = Pet.objects.get(id=id_pet)
    if request.method == 'GET':
        form = PetForm(instance=pet)
    else:
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
        return redirect('refuge:pet_list')
    return render(request, 'form/form.html', {'form': form})


def pet_delete(request, id_pet):
    pet = Pet.objects.get(id=id_pet)
    if request.method == 'POST':
        pet.delete()
        return redirect('refuge:pet_list')
    return render(request, 'pet/pet_delete.html', {'pet': pet})
"""
