# %%
import geopandas as gpd
import fiona
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
import numpy as np
import matplotlib
import matplotlib as mpl
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry import LineString
from scipy.interpolate import griddata
import zipfile
import os
# ------- 
# VERIFICAR LAS LINEAS DE COSTA
# --------
# %% 
costa =  gpd.read_file("C:/Users/Julia\Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/linea_costa/COSTA/COSTA.shp")
costa_baja = costa.loc[(costa['BAJAMAR']==True) & (costa.geometry.bounds.minx>-5) & (costa.geometry.bounds.miny>36)]
costa_baja['ELEVATION'] = 0
costa_baja['provincia'] = ''
costa_baja= costa_baja[['provincia', 'ELEVATION', 'geometry']]

# %%
# -------
# POSIDONIA
# -------
posidonia = gpd.read_file("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/areas_praderas_PeninsulaBaleares/posidonia_filtrada/output_filtrado.shp")
posi_pen =  posidonia.loc[~posidonia['Prov_Isla'].isin(['Mallorca', 'Menorca', 'Ibiza', 'Islas Chafarinas'])]
# %%
posidonia.plot()
# %%
batimetria = gpd.read_file('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/batimetria_med/dataframe_med_julia.shp')
batimetria = batimetria.to_crs(posi_pen.crs)
costa_baja = costa_baja.to_crs(posi_pen.crs)

# %%
# def leer_kmz( path):
#     gdf_list = []
#     for layer in fiona.listlayers(path):    
#         gdf = gpd.read_file(path, driver='LIBKML', layer=layer, engine= 'fiona')
#         gdf_list.append(gdf)

#     gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))
#     gdf.plot()
#     return gdf

# %%

# %%
# posidonia.groupby(['Prov_Isla']).size()
parche = posidonia.geometry[1]

# %%
batimetria2 = pd.concat([batimetria, costa_baja], ignore_index=True)

# %%
fig, ax = plt.subplots(figsize=(10, 10))
batimetria2.plot(ax= ax, color = "black")
gpd.GeoDataFrame({'geometry': [parche]}).plot(ax= ax, color = "red")
plt.show()  # COINCIDEN


# %%
contador = 0
lista_puntos  = gpd.GeoDataFrame(columns=[ 'geometry', 'profundidad'], geometry='geometry', crs= posi_pen.crs) 

posi_cata = posi_pen.loc[posi_pen['Prov_Isla'] == 'Barcelona']

for parche in posi_cata.geometry[148:149]:
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_peninsula.crs).plot()
    filtered_gdf = batimetria2[batimetria2.geometry.intersects(parche.buffer(0.01))]

    filtered_gdf.plot(aspect=1, column= 'ELEVATION')
    plt.title('profundidad')
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 10))
    filtered_gdf.plot(ax= ax, color = "grey",linewidth=0.5, markersize = 0.5)
    gpd.GeoDataFrame(geometry=[parche], crs = posi_pen.crs).plot(ax= ax, color = "red",linewidth=4000, markersize = 500)
    plt.title('mi parche con la batimetria')
    plt.show()  # COINCIDEN

    # 2️⃣ Crear una malla de puntos dentro del polígono
    minx, miny, maxx, maxy = parche.bounds  # Límites del polígono
    grid_x, grid_y = np.meshgrid(
        np.linspace(minx, maxx, 50),  # 50 puntos en X
        np.linspace(miny, maxy, 50)   # 50 puntos en Y
    )

    # # Convertimos la malla en una lista de puntos
    # grid_points = np.array([Point(x, y) for x, y in zip(grid_x.ravel(), grid_y.ravel())])
    # grid_points = np.array([p for p in grid_points if parche.contains(p)])  # Filtrar puntos dentro

    # 3️⃣ Obtener puntos y profundidades de los LineStrings
    line_points = []
    depths = []

    for _, row in filtered_gdf.iterrows():
            line = row.geometry
            depth = row['ELEVATION']
            for coord in line.coords:
                punto = Point(coord[0],coord[1] )
             
                # print(parche)
                # if punto.within(parche):
                
                line_points.append(coord)  # Guardar coordenadas (x, y)
                depths.append(depth) 
                # else: print('no esta')      # Guardar profundidad asociada

    line_points = np.array(line_points)  # Convertir a array numpy
    depths = np.array(depths)  # Profundidades

    # 4️⃣ Interpolación de la profundidad en la malla
    grid_depths = griddata(line_points, depths, (grid_x, grid_y), method='linear')
    
    #  HAcer un dataframe
    # Aplanar las matrices en arrays 1D
    x_flat = grid_x.ravel()
    y_flat = grid_y.ravel()
    temp_flat = grid_depths.ravel()

    # Crear lista de objetos Point
    puntos = [Point(x, y) for x, y in zip(x_flat, y_flat)]

    # Construir un DataFrame y convertidr a geodataframe
    df = pd.DataFrame({"geometry": puntos, "profundidad": temp_flat})
    gdf = gpd.GeoDataFrame(df, geometry="geometry")

    # print(gdf)
    
    # buscar los que caben en el polygono
    gdf_filtrado = gdf[gdf.geometry.within(parche)]
    gdf_filtrado.plot(column='profundidad', legend = True)
    plt.title(f'profundidad {contador}')
    plt.show()

    lista_puntos = pd.concat([lista_puntos, gdf_filtrado], ignore_index=True)

    contador = contador+1
    
    # buscar los nulos
    nulos = gdf[gdf.geometry.isnull()]  # Filtra las filas con geometría nula
    print(len(nulos))
print('FIN')  
# %%