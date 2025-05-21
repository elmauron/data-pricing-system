from django.urls import path
from .views import get_temp, get_especies, get_origenes, get_variedades, get_productos, get_presentaciones, get_preciosdiarios

urlpatterns = [
    path('temp/', get_temp, name='get_temp' ),
    path('especies/', get_especies, name='get_especies' ),
    path('origenes/', get_origenes, name='get_origenes' ),
    path('variedades/', get_variedades, name='get_variedades' ),
    path('productos/', get_productos, name='get_productos' ),
    path('presentaciones/', get_presentaciones, name='get_presentaciones' ),
    path('preciosdiarios/', get_preciosdiarios, name='get_preciosdiarios' )
]