from rest_framework import serializers
from .models import Temp, CatEspecies, CatOrigenes, CatPresentaciones, CatProductos, CatVariedades, PreciosDiarios

class TempSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temp
        fields = '__all__'

class CatEspeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatEspecies
        fields = '__all__'        

class CatOrigenesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatOrigenes
        fields = '__all__'

class CatPresentacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatPresentaciones
        fields = '__all__'

class CatProductosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatProductos
        fields = '__all__'

class CatVariedadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatVariedades
        fields = '__all__'

class PreciosDiariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreciosDiarios
        fields = '__all__'
