# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CatEspecies(models.Model):
    especie_id = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'cat_especies'


class CatOrigenes(models.Model):
    origen_id = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'cat_origenes'


class CatPresentaciones(models.Model):
    presentacion_id = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'cat_presentaciones'


class CatProductos(models.Model):
    producto_id = models.AutoField(primary_key=True)
    kilos = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    variedad = models.ForeignKey('CatVariedades', models.DO_NOTHING)
    origen = models.ForeignKey(CatOrigenes, models.DO_NOTHING, blank=True, null=True)
    presentacion = models.ForeignKey(CatPresentaciones, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cat_productos'
        unique_together = (('presentacion', 'origen', 'variedad', 'kilos'),)


class CatVariedades(models.Model):
    variedad_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    especie = models.ForeignKey(CatEspecies, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cat_variedades'
        unique_together = (('especie', 'nombre'),)


class PreciosDiarios(models.Model):
    precio_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(CatProductos, models.DO_NOTHING)
    fecha = models.DateField()
    precio_mayorista = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_minorista = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_modal = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_mayorista_x_kg = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_minorista_x_kg = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_modal_x_kg = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'preciosdiarios'
        unique_together = (('producto', 'fecha'),)


class Temp(models.Model):
    temp_id = models.AutoField(primary_key=True)
    fecha = models.DateField(blank=True, null=True)
    especie = models.CharField(max_length=50, blank=True, null=True)
    variedad = models.CharField(max_length=50, blank=True, null=True)
    origen = models.CharField(max_length=50, blank=True, null=True)
    envase = models.CharField(max_length=50, blank=True, null=True)
    kilos = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    calibre = models.CharField(max_length=50, blank=True, null=True)
    tamano = models.CharField(max_length=50, blank=True, null=True)
    precio_mayorista = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_modal = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_minorista = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_mayorista_x_kg = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_modal_x_kg = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_minorista_x_kg = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'temp'
