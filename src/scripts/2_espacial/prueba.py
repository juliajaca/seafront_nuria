# %%
import geopandas as gpd
# import ipympl
import matplotlib.pyplot as plt
# %matplotlib widget
import matplotlib.pyplot as plt
import pandas as pd

from shapely.geometry import Point
import numpy as np
# from shapely.geometry.polygon import Polygon
# from unidecode import unidecode
import matplotlib
import matplotlib as mpl
# import geopandas as gpd
# from scipy import datasets
from netCDF4 import Dataset
# import fiona

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
from scipy.interpolate import griddata
# ------- 
# VERIFICAR LAS LINEAS DE COSTA
# --------
# %% 
costa =  gpd.read_file("C:/Users/Julia\Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/linea_costa/COSTA/COSTA.shp")
costa_baja = costa.loc[(costa['BAJAMAR']==True) & (costa.geometry.bounds.minx>-5) & (costa.geometry.bounds.miny>36)]
costa_baja['profundidad'] = 0
costa_baja= costa_baja[['profundidad', 'geometry']]
# %%
cataluña = gpd.read_file("zip://C:/Users/Julia\Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/linea_costa/linia-costa-cataluña.zip!Linia_costa_Lmunicipal 5k.shp")
cataluña = cataluña.to_crs(costa_baja.crs)
# %%
murcia = gpd.read_file("zip://C:/Users/Julia\Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/linea_costa/LINEA_CERO_tcm30-288147murcia/LINEA_CERO.kmz")
#%% baleares
menorca = gpd.read_file("zip://C:/Users/Julia\Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/linea_costa/linea_cero_tcm30-288170_menorca/linea_cero.kmz")
# %%
fig, ax = plt.subplots(figsize=(10, 10))
costa_baja.plot(ax= ax, color = "blue")
cataluña.plot(ax= ax, color = "red")
murcia.plot(ax= ax, color = "green")
menorca.plot(ax=ax, color = 'violet')
plt.show()  # COINCIDEN
# %%
# -------
# POSIDONIA
# -------

posidonia = gpd.read_file("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/areas_praderas_PeninsulaBaleares/posidonia_filtrada/output_filtrado.shp")

# %%
posidonia.plot()
# %%
parche = posidonia.geometry[1]

# %% bati catal
cataluña = gpd.read_file("zip://C:/Users/Julia\Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/batimetrias/cataluña.zip!Batimetria_IHM.shp")
cataluña = cataluña.rename(columns={'PROF': 'profundidad'})
cataluña = cataluña.to_crs(costa_baja.crs)
cataluña= cataluña[['profundidad', 'geometry']]
cataluña = pd.concat([cataluña, costa_baja], ignore_index=True)
cataluña = cataluña.to_crs(posidonia.crs)
cataluña.plot()
# %%
fig, ax = plt.subplots(figsize=(10, 10))
cataluña.plot(ax= ax, color = "white")
gpd.GeoDataFrame({'geometry': [parche]}).plot(ax= ax, color = "red")

plt.show()  # COINCIDEN

# %%
filtered_gdf = cataluña[cataluña.geometry.intersects(parche)]

filtered_gdf.plot(column= 'profundidad')
plt.title('profundidad')
plt.show()
# %%
fig, ax = plt.subplots(figsize=(10, 10))
filtered_gdf.plot(ax= ax, color = "grey")
gpd.GeoDataFrame({'geometry': [parche]}).plot(ax= ax, color = "red")

plt.show()  # COINCIDEN

# %%
# 1️⃣ Cargar el GeoDataFrame de LineStrings y el polígono
gdf_lines = filtered_gdf  # GeoDataFrame con LineStrings y columna 'profundidad'
polygon = parche # Polígono

# 2️⃣ Crear una malla de puntos dentro del polígono
minx, miny, maxx, maxy = polygon.bounds  # Límites del polígono
grid_x, grid_y = np.meshgrid(
    np.linspace(minx, maxx, 50),  # 50 puntos en X
    np.linspace(miny, maxy, 50)   # 50 puntos en Y
)

# Convertimos la malla en una lista de puntos
grid_points = np.array([Point(x, y) for x, y in zip(grid_x.ravel(), grid_y.ravel())])
grid_points = np.array([p for p in grid_points if polygon.contains(p)])  # Filtrar puntos dentro

# 3️⃣ Obtener puntos y profundidades de los LineStrings
line_points = []
depths = []

for _, row in gdf_lines.iterrows():
    line = row.geometry
    depth = row['profundidad']
    for coord in line.coords:
        line_points.append(coord)  # Guardar coordenadas (x, y)
        depths.append(depth)       # Guardar profundidad asociada

line_points = np.array(line_points)  # Convertir a array numpy
depths = np.array(depths)  # Profundidades

# 4️⃣ Interpolación de la profundidad en la malla
grid_depths = griddata(line_points, depths, (grid_x, grid_y), method='linear')

# %% HAcer un dataframe
# Aplanar las matrices en arrays 1D
x_flat = grid_x.ravel()
y_flat = grid_y.ravel()
temp_flat = grid_depths.ravel()

# Crear lista de objetos Point
puntos = [Point(x, y) for x, y in zip(x_flat, y_flat)]

# Construir un DataFrame
df = pd.DataFrame({"geometry": puntos, "profundidad": temp_flat})

# Convertir a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry="geometry")

print(gdf)
# %%
# buscar los que caben en el polygono
gdf_filtrado = gdf[gdf.geometry.within(polygon)]
gdf_filtrado.plot(column='profundidad', legend = True)
plt.title('profundidad')
plt.show()

# %%
# buscar los nulos
nulos = gdf[gdf.geometry.isnull()]  # Filtra las filas con geometría nula

print(nulos)
# %%
plt.figure(figsize=(8, 6))
plt.contourf(grid_x, grid_y, grid_depths, cmap="coolwarm", levels=20)
plt.colorbar(label="Profundidad")
plt.plot(*polygon.exterior.xy, color='black', linewidth=2)  # Dibujar polígono
# plt.scatter(line_points[:, 0], line_points[:, 1], color='black', label="LineStrings (puntos)")
plt.scatter([p.x for p in grid_points], [p.y for p in grid_points], color='green', s=5, label="Puntos Malla")
plt.legend()
plt.title("Interpolación de Profundidad")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()
# %%

# %%
# tasa mortalidad por año = 0.021 * temperatura - 0.471 
# tasa mortalidad = 0.02 por año
# reclutamiento = 0.05 por año (es sumado tambien)
# %%
# año1 =
gdf_filtrado['presente'] =  674 - 24.4 * gdf_filtrado['profundidad'] 
gdf_filtrado.plot(column='presente', legend=True)
# gdf_filtrado['+1'] = gdf_filtrado['presente'] - (gdf_filtrado['presente']*0.02) - gdf_filtrado['presente']*0.05 - (gdf_filtrado['presente'] * 0.021 * (0.0277*1) -0.471)

# %%
for year in range(1,75):
    print(year)
    columna = gdf_filtrado.iloc[:,-1:] - (gdf_filtrado.iloc[:,-1:]*0.02) - gdf_filtrado.iloc[:,-1:]*0.05 - (gdf_filtrado.iloc[:,-1:] * 0.021 * (25+0.0277*year) -0.471)
    gdf_filtrado[year] = columna
    gdf_filtrado['final'] = columna

# %%
gdf_filtrado.plot(column='presente', legend=True)
plt.title('Densidad Presente')
# %%
gdf_filtrado.plot(column='final', legend=True)
plt.title('Densidad 2100')
# %%
# gdf_filtrado.to_file('prueba_parche_cataluña.shp')
# %%
df1 = pd.DataFrame(gdf_filtrado)

# %%
df1.to_csv('pruebacsv2.csv')

# %%
