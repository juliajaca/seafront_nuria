# %%
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.wkt import loads
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import pyproj
from geopy.distance import geodesic
from shapely.ops import transform
from scipy.optimize import curve_fit
from scipy.interpolate import griddata
from scipy.interpolate import interp1d

# %%
parche = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/prueba_runup_años.csv')
# Convertir la columna de geometría (ejemplo: "geometry") de WKT a objetos geométricos
parche["geometry"] = parche["geometry"].apply(loads)
# %%
gdf = gpd.GeoDataFrame(parche, geometry="geometry")
gdf.set_crs("EPSG:4326", inplace=True) #es cataluña
gdf['densidad'] = 674 + 24.4 * gdf['profundidad']
# %%
gdf.plot(column='profundidad')
# %%
# Encontrar el punto con el valor más alto y más bajo
punto_max = gdf.loc[gdf['profundidad'].idxmax()]
punto_min = gdf.loc[gdf['profundidad'].idxmin()]
# Crear una línea entre ellos
linea = LineString([punto_max.geometry, punto_min.geometry])

gdf['distancia'] = gdf.apply(lambda row: row.geometry.distance(linea), axis=1)
# %%
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(column='profundidad',ax= ax)
gpd.GeoDataFrame(geometry=[linea], crs = gdf.crs).plot(ax= ax, color = "red",linewidth=2, markersize = 1)
plt.title('mi parche con la batimetria')
plt.show()  # COINCIDEN
# %%
# Seleccionar los puntos más cercanos a la línea
gdf_cercanos = gdf[gdf['distancia'] < 0.00005]  # Ajusta el umbral según la escala de coordenadas
fig, ax = plt.subplots(figsize=(10, 10))
gdf_cercanos.plot(column='profundidad',ax= ax)
gpd.GeoDataFrame(geometry=[linea], crs = gdf.crs).plot(ax= ax, color = "red",linewidth=2, markersize = 1)
plt.title('mi parche con la batimetria')
plt.show()  # COINCIDEN

# %%  CREAR LA LINEA
# # --- 2️⃣ Encontrar puntos extremos ---
# punto_max = gdf.loc[gdf['profundidad'].idxmax()]  # Punto con el valor más alto
# punto_min = gdf.loc[gdf['profundidad'].idxmin()]  # Punto con el valor más bajo

# # --- 3️⃣ Crear la recta entre los puntos extremos ---
# linea = LineString([punto_min.geometry, punto_max.geometry])

# --- 4️⃣ Convertir coordenadas geográficas a UTM ---
# Definir la proyección UTM para Baleares (EPSG:32631)
proj_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32631", always_xy=True)

# Aplicar la transformación a los puntos y la línea
punto_min_utm = transform(proj_utm.transform, punto_min.geometry)
punto_max_utm = transform(proj_utm.transform, punto_max.geometry)
linea_utm = transform(proj_utm.transform, linea)

# --- 5️⃣ Proyectar puntos sobre la recta para obtener coordenadas en 1D ---
def proyectar_a_1D(punto):
    punto_utm = transform(proj_utm.transform, punto)
    distancia = linea_utm.project(punto_utm)  # Distancia sobre la recta en metros
    return distancia

# Aplicar la proyección a cada punto
gdf_cercanos["distancia_1D"] = gdf_cercanos["geometry"].apply(proyectar_a_1D)
# --- 6️⃣ Ordenar por distancia a la costa ---
gdf_cercanos = gdf_cercanos.sort_values(by="distancia_1D")
# --- 7️⃣ Visualización o exportación ---
print(gdf_cercanos[["geometry", "profundidad", "distancia_1D", 'densidad']])  # Ver los resultados

# %%
plt.figure(figsize=(8, 5))
plt.plot(gdf_cercanos.distancia_1D, gdf_cercanos['profundidad'], marker='o', linestyle='-', color='b')

plt.xlabel("Distancia desde la costa (m)")
plt.ylabel("Profundidad (m)")
plt.title("Perfil de profundidad respecto a la distancia desde la costa")
# plt.gca().invert_yaxis()  # Invertir el eje Y porque la profundidad es negativa
plt.grid()

plt.show()

# %% ################## CREAR DICT RANGOS PROFUNDIDAD
gdf_cercanos = gdf_cercanos.sort_values(by='profundidad').reset_index(drop=True)
# %%
rangos_dict = {}
for i in range(len(gdf_cercanos) - 1):
        p1 = gdf_cercanos.iloc[i].geometry
        p2 = gdf_cercanos.iloc[i+1].geometry
        # Calcular la distancia en metros entre puntos
        dist = geodesic((p1.x, p1.y), (p2.x, p2.y)).meters
        print(dist)
        # print(f'la distancia es {dist}')
        if dist <= 50:
            rango = (gdf_cercanos['profundidad'].iloc[i], gdf_cercanos['profundidad'].iloc[i + 1])
            rango_clave = f"({rango[0]:.2f}, {rango[1]:.2f})"
            rangos_dict[rango_clave] = gdf_cercanos['densidad'].iloc[i]

print(rangos_dict)

# %%
gdf= gdf_cercanos
# Crear un LineString con los puntos
line = linea


# Calcular la distancia total en metros usando geopy
distancia_total_metros = geodesic((punto_max.geometry.y, punto_max.geometry.x), (punto_min.geometry.y, punto_min.geometry.x)).meters

# Función para proyectar un punto en la línea y escalar su distancia en metros
def proyectar_distancia_metros(punto, linea, distancia_total):
    # Proyectar el punto sobre la línea en un valor entre 0 y 1
    posicion_1d = linea.project(punto, normalized=True)
    # Escalar a metros
    distancia_metros = posicion_1d * distancia_total
    return distancia_metros

# Aplicar la función a cada punto
gdf["distancia_1D_metros"] = gdf["geometry"].apply(lambda p: proyectar_distancia_metros(p, linea, distancia_total_metros))

# Mostrar resultados
print(gdf[["geometry", "distancia_1D_metros", 'profundidad']])
# %%
# Interpolacion
#  Convertir a DataFrame
# Ordenar por distancia (por seguridad)
df = gdf.sort_values(by="profundidad")

# Crear función de interpolación: ahora interpolamos DISTANCIA en función de la PROFUNDIDAD
interp_func = interp1d(df["profundidad"], df["distancia_1D_metros"], kind='linear', fill_value="extrapolate")

# Definir una malla de profundidades (por ejemplo, de 0 a -20 m en pasos de 0.1 m)
profundidades_nuevas = np.linspace(0, -20, 200)

# Calcular las distancias asociadas a esas profundidades
distancias_nuevas = interp_func(profundidades_nuevas)
print(distancias_nuevas)
# %%
# Mostrar los primeros valores de la malla generada
df_malla = pd.DataFrame({"profundidad": profundidades_nuevas, "distancia_1D_metros": distancias_nuevas})
print(df_malla.head(10))
# %%
