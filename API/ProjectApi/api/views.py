from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Temp, CatEspecies, CatOrigenes, CatPresentaciones, CatProductos, CatVariedades, PreciosDiarios
from .serializer import TempSerializer, CatEspeciesSerializer, CatOrigenesSerializer, CatPresentacionesSerializer, CatProductosSerializer, CatVariedadesSerializer, PreciosDiariosSerializer

@api_view(['GET'])
def get_temp(request):
    temp = Temp.objects.all()
    serializer = TempSerializer(temp, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_especies(request):
    especies = CatEspecies.objects.all()
    serializer = CatEspeciesSerializer(especies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_origenes(request):
    origenes = CatOrigenes.objects.all()
    serializer = CatOrigenesSerializer(origenes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_presentaciones(request):
    presentaciones = CatPresentaciones.objects.all()
    serializer = CatPresentacionesSerializer(presentaciones, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_productos(request):
    productos = CatProductos.objects.all()
    serializer = CatProductosSerializer(productos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_variedades(request):
    variedades = CatVariedades.objects.all()
    serializer = CatVariedadesSerializer(variedades, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_preciosdiarios(request):
    preciosdiarios = PreciosDiarios.objects.all()
    serializer = PreciosDiariosSerializer(preciosdiarios, many=True)
    return Response(serializer.data)


