from datetime import datetime
import re
from dotenv import load_dotenv
import os
import requests
import json
import psycopg2 as ps
from bs4 import BeautifulSoup
import zipfile
import pandas as pd
from io import BytesIO
import logging

logging.basicConfig(
    filename='db_errors.log',                                  # fichero donde se volcarán los errores
    level=logging.ERROR,                                       # capturamos ERROR y superior
    format='%(asctime)s %(levelname)s %(message)s'
)

load_dotenv()
host_name = os.getenv("DB_HOST")
dbname    = os.getenv("DB_NAME")
port      = os.getenv("DB_PORT")
username  = os.getenv("DB_USER")
password  = os.getenv("DB_PASS")

url = 'https://mercadocentral.gob.ar/informaci%C3%B3n/precios-mayoristas'

#defino metodos que voy a utilizar
#==========================================================================================

def conectar_a_db (host_name, dbname, username, password, port): # metodo para hacer conexion con la db
    try:
        conn = ps.connect(host=host_name, database=dbname, user=username, password=password, port=port)

    except ps.OperationalError as e:
        raise e
    else:
        print('CONECTADO>>>') 
    return conn       

def web_scrap(url):                                              # metodo para sacar los datos de la web in guardarlos temporalmente en un zip en memoria
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print ("Page title:", soup.title.text)
    else:
        print("Failed to fetch page. Status code: ", response.status_code)

    # Buscar todos los <a> que tengan ".zip" en su href

    links_anuales_array = []
    links_mensuales_array = []

    for a in soup.find_all('a', href=True):
        nombre = a.text
        href = a['href']
        if ".zip" in href:
            if re.search(r"20\d{2}\.zip$", nombre):
                links_anuales_array.append(href)
            else:
                links_mensuales_array.append(href)
  

    zips_anuales = []
    df_array = []

    for link in links_anuales_array: 
      print (f"Descargando: {link}")
      response = requests.get(link)
      zips_anuales.append(BytesIO(response.content))

    for zip_mes in zips_anuales:
        
        with zipfile.ZipFile(zip_mes) as zf:
          print (">>> Archivos encontrados en el ZIP: ") #<---------DEBERIA MOSTRAR TODOS LOS MESES DE CADA Añ0
          print (zf.namelist())
          
          for nombre_archivo in zf.namelist():

            print(">>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<")
            print(nombre_archivo)

            archivo_leido = zf.read(nombre_archivo)

            with zipfile.ZipFile(BytesIO(archivo_leido)) as zm:
                for archivo_xls in zm.namelist():
                    if archivo_xls.endswith('.XLS') or archivo_xls.endswith('.xls'):
                         
                         fecha_string = archivo_xls[2:4] + "/" + archivo_xls[4:6] + "/" + archivo_xls[6:8]
                         print("\n" + f"Leyendo archivo del día: {fecha_string}" + "\n")

                         with zm.open(archivo_xls) as archivo:
                               df = pd.read_excel(archivo, engine='xlrd') # df = DATAFRAME
                               df['fecha'] = datetime.strptime(fecha_string, "%d/%m/%y").date()  # <---- PONE LA FECHA
                               df.columns = df.columns.str.replace(r'\d{6}$', '', regex=True) # <----- ELIMINO NUMEROS REDUNDANTES DE COLUMNAS DE PRECIOS 
                               df_array.append(df)

    print(df_array)

    master_df = normalize_dataFrames(df_array)
    return master_df

def normalize_dataFrames(df_array):                              # metodo para normalizar arrays de dataframes y concatenarlos en uno solo
  # TENGO QUE ELIMINAR LOS PROM.ESP
    col_map = {
        'ESP':       'especie',
        'VAR':       'variedad',
        'PROC':      'origen',
        'ENV':       'envase',
        'KG':        'kilos',
        'CAL':       'calibre',
        'TAM':       'tamano',
        'GRADO':     'grado',
        'MA':  'precio_mayorista',
        'MO':  'precio_modal',
        'MI':  'precio_minorista',
        'MAPK':      'precio_mayorista_x_kg',
        'MOPK':      'precio_modal_x_kg',
        'MIPK':      'precio_minorista_x_kg',
        'fecha':     'fecha'
    }

    normalized = []
    for df in df_array:
        df2 = df.reset_index().rename(columns={'index':'temp_id'})
        df2 = df.rename(columns=col_map)  
        normalized.append(df2)

    big_df = pd.concat(normalized, ignore_index=True)
    big_df = big_df.reset_index().rename(columns={'index':'temp_id'})

    return(big_df)               

def check_table_exists(curr, table_name):
    curr.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
        (table_name,)
        )
    return curr.fetchone()[0]

def crear_tablas(curr):                                          # metodo para hacer CREATE de las tablas (table shells)
    
    temp_creation_command = ("""CREATE TABLE temp (
                                temp_id                 SERIAL PRIMARY KEY,
                                fecha                   date NULL,
                                especie                 VARCHAR(50) NULL,
                                variedad                VARCHAR(50) NULL,
                                origen                  VARCHAR(50) NULL,
                                envase                  VARCHAR(50) NULL,
                                kilos                   decimal(18) NULL,
                                calibre                 VARCHAR(50) NULL,
                                tamano                  VARCHAR(50) NULL,
                                precio_mayorista        decimal(18,2) NULL,
                                precio_modal            decimal(18,2) NULL,
                                precio_minorista        decimal(18,2) NULL,
                                precio_mayorista_x_kg   decimal(18,2) NULL,
                                precio_modal_x_kg       decimal(18,2) NULL,
                                precio_minorista_x_kg   decimal(18,2) NULL);
                                """)
    
    origenes_creation_command = ("""CREATE TABLE cat_origenes (
                                origen_id               SERIAL PRIMARY KEY,
                                nombre                  VARCHAR(50) NOT NULL UNIQUE);
                                """)
    
    presentaciones_creation_command = ("""CREATE TABLE cat_presentaciones (
                                       presentacion_id  SERIAL PRIMARY KEY,
                                       nombre           VARCHAR(50) NOT NULL,
                                       CONSTRAINT uq_cat_presentaciones
                                         UNIQUE (nombre));
                                       """)

    especies_creation_command = ("""CREATE TABLE cat_especies (
                                especie_id              SERIAL PRIMARY KEY,
                                nombre                  VARCHAR(50) NOT NULL UNIQUE);
                                """)

    variedades_creation_command = ("""CREATE TABLE cat_variedades (
                                variedad_id             SERIAL PRIMARY KEY, 
                                nombre                  VARCHAR(50), 
                                especie_id              INTEGER NOT NULL REFERENCES cat_especies(especie_id),
                                CONSTRAINT uq_cat_variedades_especie_nombre 
                                   UNIQUE(especie_id, nombre));
                                """)

    productos_creation_command = ("""CREATE TABLE cat_productos (
                                producto_id             SERIAL PRIMARY KEY, 
                                kilos                   decimal(18,2),
                                variedad_id             INTEGER NOT NULL REFERENCES cat_variedades(variedad_id),
                                origen_id               INTEGER NULL REFERENCES cat_origenes(origen_id),
                                presentacion_id         INTEGER NOT NULL REFERENCES cat_presentaciones(presentacion_id),  
                                UNIQUE (presentacion_id, origen_id, variedad_id, kilos));
                            """)

    precios_diarios_creation_command = ("""CREATE TABLE PreciosDiarios (
                                precio_id               SERIAL PRIMARY KEY,
                                producto_id             INTEGER NOT NULL REFERENCES cat_productos(producto_id),
                                fecha                   date NOT NULL,
                                precio_mayorista        decimal(18,2),
                                precio_minorista        decimal(18,2),
                                precio_modal            decimal(18,2),
                                precio_mayorista_x_kg   decimal(18,2),
                                precio_minorista_x_kg   decimal(18,2),
                                precio_modal_x_kg       decimal(18,2),
                                UNIQUE (producto_id, fecha));
                        """)
    
    curr.execute(temp_creation_command)
    curr.execute(origenes_creation_command)
    curr.execute(presentaciones_creation_command)
    curr.execute(especies_creation_command)
    curr.execute(variedades_creation_command)
    curr.execute(productos_creation_command)
    curr.execute(precios_diarios_creation_command)

def check_procedure_exists(curr):
    sql = ("""
            SELECT EXISTS (
              SELECT 1
                FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
               WHERE p.proname  = 'importar_desde_temp'  -- procedure
                 AND n.nspname = 'public'                -- esquema
            );
    """)
    curr.execute(sql)
    return curr.fetchone()[0]

def crear_procedure(curr):                                       #metodo para crear un PROCEDURE que reorganice las tablas de la db
    procedure_creaion_command = ("""CREATE OR REPLACE FUNCTION importar_desde_temp()
                                      RETURNS void
                                      LANGUAGE plpgsql
                                    AS $$
                                    BEGIN
                                      -- 2) Orígenes
                                      INSERT INTO cat_origenes(nombre)
                                      SELECT DISTINCT origen
                                      FROM temp
                                      WHERE origen IS NOT NULL
                                      ON CONFLICT(nombre) DO NOTHING;

                                      -- 3) Presentaciones (Envase - Tamaño - Calibre)
                                      INSERT INTO cat_presentaciones(nombre)
                                      SELECT DISTINCT
                                        coalesce(envase,'')
                                        || ' - ' || coalesce(tamano,'')                                 
                                        || ' - ' || coalesce(calibre,'')
                                      FROM temp
                                      ON CONFLICT(nombre) DO NOTHING;

                                      -- 4) Especies
                                      INSERT INTO cat_especies(nombre)
                                      SELECT DISTINCT especie
                                      FROM temp
                                      WHERE especie IS NOT NULL
                                      ON CONFLICT(nombre) DO NOTHING;

                                      -- 5) Variedades
                                      INSERT INTO cat_variedades(especie_id, nombre)
                                      SELECT
                                        e.especie_id,
                                        t.variedad
                                      FROM (
                                        SELECT DISTINCT especie, variedad
                                        FROM temp
                                      ) AS t
                                      JOIN cat_especies AS e
                                        ON e.nombre = t.especie
                                      ON CONFLICT(especie_id, nombre) DO NOTHING;

                                      -- 6) Productos
                                      INSERT INTO cat_productos(variedad_id, origen_id, presentacion_id, kilos)
                                      SELECT
                                        v.variedad_id,
                                        o.origen_id,
                                        p.presentacion_id,
                                        t.kilos
                                      FROM (
                                        SELECT DISTINCT especie, variedad, origen, envase, tamano, calibre, kilos
                                        FROM temp
                                      ) AS t
                                      JOIN cat_especies AS e
                                        ON e.nombre = t.especie
                                      JOIN cat_variedades AS v
                                        ON v.especie_id = e.especie_id
                                       AND v.nombre     = t.variedad
                                      LEFT JOIN cat_origenes AS o
                                        ON o.nombre = t.origen
                                      JOIN cat_presentaciones AS p
                                        ON p.nombre = coalesce(envase,'') || ' - ' || coalesce(tamano,'') || ' - ' || coalesce(calibre,'')
                                      WHERE kilos IS NOT NULL
                                      ON CONFLICT(variedad_id, origen_id, presentacion_id, kilos) DO NOTHING;
                                 
                                      --7) PreciosDiarios
                                      INSERT INTO PreciosDiarios (producto_id, fecha, precio_mayorista, precio_minorista, precio_modal, precio_mayorista_x_kg, precio_minorista_x_kg, precio_modal_x_kg)  
                                      SELECT 
                                        p.producto_id,
                                        t.fecha::date,
                                        t.precio_mayorista, 
                                        t.precio_minorista, precio_modal, 
                                        t.precio_mayorista_x_kg, 
                                        t.precio_minorista_x_kg, 
                                        t.precio_modal_x_kg
                                      FROM (
                                        SELECT DISTINCT fecha, especie, variedad, origen, envase, tamano, calibre, 
                                                        precio_mayorista, precio_minorista, precio_modal,
                                                        precio_mayorista_x_kg, precio_minorista_x_kg, precio_modal_x_kg
                                        FROM temp
                                        WHERE fecha IS NOT NULL
                                      ) AS t
                                      JOIN cat_especies AS e
                                        ON e.nombre = t.especie
                                      JOIN cat_variedades AS v
                                        ON v.especie_id = e.especie_id
                                       AND v.nombre     = t.variedad
                                      LEFT JOIN cat_origenes AS o
                                        ON o.nombre = t.origen
                                      JOIN cat_presentaciones AS pr
                                        ON pr.nombre = coalesce(envase,'') || ' - ' || coalesce(tamano,'') || ' - ' || coalesce(calibre,'')
                                      JOIN cat_productos AS p
                                        ON p.variedad_id     = v.variedad_id
                                       AND p.origen_id       = o.origen_id
                                       AND p.presentacion_id = pr.presentacion_id
                                        ON CONFLICT(producto_id, fecha) DO NOTHING;
                                    END;
                                    $$;
""")
    curr.execute(procedure_creaion_command)
        
def check_if_temp_exists(curr, temp_id):
    query = ("""SELECT temp_id FROM temp WHERE temp_id = %s""")
    curr.execute(query, (temp_id,))
    
    return curr.fetchone() is not None

def update_row(curr, temp_id, fecha, especie, variedad, origen, envase, kilos, calibre, tamano, precio_mayorista, precio_modal, precio_minorista, precio_mayorista_x_kg, precio_modal_x_kg, precio_minorista_x_kg):
    query = ("""UPDATE temp
                SET fecha = %s,               
                    especie = %s,              
                    variedad = %s,             
                    origen = %s,               
                    envase = %s,               
                    kilos = %s,                
                    calibre = %s,              
                    tamano = %s,               
                    precio_mayorista = %s,     
                    precio_modal = %s,         
                    precio_minorista = %s,     
                    precio_mayorista_x_kg = %s,
                    precio_modal_x_kg = %s,    
                    precio_minorista_x_kg = %s
                WHERE temp_id = %s;""")
    variables_to_update = (fecha, especie, variedad, origen, envase, kilos, calibre, tamano, precio_mayorista, precio_modal, precio_minorista, precio_mayorista_x_kg, precio_modal_x_kg, precio_minorista_x_kg, temp_id)
    curr.execute(query, variables_to_update)

def update_db(curr, df):
    temp_df = pd.DataFrame(columns=['temp_id', 'fecha', 'especie', 
                                    'variedad', 'origen', 'envase', 
                                    'kilos', 'calibre', 'tamano', 
                                    'precio_mayorista', 'precio_modal', 
                                    'precio_minorista', 'precio_mayorista_x_kg', 
                                    'precio_modal_x_kg', 'precio_minorista_x_kg'])

    for i, row in df.iterrows():
        if check_if_temp_exists(curr, row['temp_id']): 
            update_row(curr, row['temp_id'], 
                       row['fecha'], 
                       row['especie'], 
                       row['variedad'], 
                       row['origen'], 
                       row['envase'], 
                       row['kilos'], 
                       row['calibre'], 
                       row['tamano'], 
                       row['precio_mayorista'], 
                       row['precio_modal'], 
                       row['precio_minorista'], 
                       row['precio_mayorista_x_kg'], 
                       row['precio_modal_x_kg'],
                       row['precio_minorista_x_kg'])               
        else:
            temp_df.loc[len(temp_df)] = row                 # Si la fila NO existe, se creara

    return temp_df

def insert_into_table(curr, fecha, especie, variedad, origen, envase, kilos, calibre, tamano, precio_mayorista, precio_modal, precio_minorista, precio_mayorista_x_kg, precio_modal_x_kg, precio_minorista_x_kg):
  insert_into_temp = ("""INSERT INTO temp (fecha, especie, variedad, origen, envase, kilos, calibre, 
                      tamano, precio_mayorista, precio_modal, precio_minorista, precio_mayorista_x_kg, 
                      precio_modal_x_kg, precio_minorista_x_kg)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""")
  row_to_insert = (fecha, especie, variedad, origen, envase, kilos, calibre, tamano, precio_mayorista, precio_modal, precio_minorista, precio_mayorista_x_kg, precio_modal_x_kg, precio_minorista_x_kg)
  curr.execute(insert_into_temp, row_to_insert)

def append_from_df_to_db(curr,df):
  for i, row in df.iterrows():
      insert_into_table(curr, 
                         row['fecha'], 
                         row['especie'], 
                         row['variedad'], 
                         row['origen'], 
                         row['envase'], 
                         row['kilos'], 
                         row['calibre'], 
                         row['tamano'], 
                         row['precio_mayorista'], 
                         row['precio_modal'], 
                         row['precio_minorista'], 
                         row['precio_mayorista_x_kg'], 
                         row['precio_modal_x_kg'],
                         row['precio_minorista_x_kg'])
      
  print('INSERT EXITOSO>>>')

#==========================================================================================
# Scrapeo los datos de la web
master_df = web_scrap(url)

try:
  conn = conectar_a_db(host_name, dbname, username, password, port)         # Me conecto a la base de datos
  curr = conn.cursor()                                                      # Permite que el codigo python ejecute comandos SQL en la base de datos

  table_name = "temp"
  if check_table_exists(curr, table_name):
      print(f"Las tablas ya existen.")
  else: 
      crear_tablas(curr)  
      print('CREACION DE TABLAS EXITOSO>>>')                                      # Creo las tablas usando curr para ejecutar en SQL# Creo las tablas usando curr para ejecutar en SQL
except ps.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")  

try:                                                                              # Pruebo crear el PROCEDURE y si falla loggea el error
  procedure_name = "procedure_creaion_command"
  if check_procedure_exists(curr):
      print(f"El PROCEDURE ya existe.")
  else: 
      crear_procedure(curr)   
      print('CREACION DE PROCEDURE EXITOSO>>>')                                   # Creo las tablas usando curr para ejecutar en SQL# Creo las tablas usando curr para ejecutar en SQL
except ps.Error as e:
    logging.exception("Detalle de la excepción:")
    raise

new_temp_df = update_db(curr, master_df)

append_from_df_to_db(curr, new_temp_df)
curr.callproc('importar_desde_temp')

conn.commit()

print('Esto es lo último:' + '\n')
print(new_temp_df)