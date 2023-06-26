from django.urls import path
from src import views

urlpatterns = [
path("",views.folium_graph,name="folium_index"),
]  