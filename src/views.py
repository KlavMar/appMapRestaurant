
from django.shortcuts import render
from  src import restaurant_dash


def folium_graph(request):
    return render(request,"map_restaurant.html")



