from django.urls import path
from . import views


app_name = 'refuge'
urlpatterns = [
    path('', views.index, name='index'),
    path('list.json/', views.list_pet, name='pet_list_json'),
    path('list/', views.PetListView.as_view(), name='pet_list'),
    path('create/', views.PetCreateView.as_view(), name='pet_create'),
    path('update/<int:pk>/', views.PetUpdateView.as_view(), name='pet_update'),
    path('delete/<int:pk>/', views.PetDeleteView.as_view(), name='pet_delete'),

    path('adoption/list/', views.AdoptionListView.as_view(), name='adoption_list'),
    path('adoption/create/', views.AdoptionCreateView.as_view(), name='adoption_create'),
    path('adoption/update/<int:pk>/',
         views.AdoptionUpdateView.as_view(), name='adoption_update'),
    path('adoption/delete/<int:pk>/',
         views.AdoptionDeleteView.as_view(), name='adoption_delete'),
    path('person/list.json', views.list_person, name='person_list_json'),
    path('person/list/', views.view_person, name='person_list'),
    path('vaccine/autocomplete/', views.VaccineAutocompleteView.as_view(),
         name='vaccine_autocomplete'),
    path('pet/autocomplete/', views.PetAutocompleteView.as_view(),
         name='pet_autocomplete'),

    path('person/autocomplete/', views.PersonAutocompleteView.as_view(),
         name='person_autocomplete'),
    path('create_instance/',views.create_instance_example,name='create_instance'),


]
