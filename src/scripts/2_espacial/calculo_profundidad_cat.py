# %%
import math
import geopandas as gpd
from shapely.geometry import LineString, Point
from io import BytesIO
from geopy.distance import geodesic
import pandas as pd
import ipympl
import matplotlib.pyplot as plt
%matplotlib widget
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
from scipy.interpolate import griddata
# %%
path = 'C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/batimetria/batimetria/cataluña/batimetria-carta-nautica-ihm.zip'
file = open(path, "rb")
cat =gpd.read_file(BytesIO(file.read()))
cat['provincia'] = 'cataluña'
cat= cat.to_crs(4326)
cat['ELEVATION'] = -abs(cat['PROF'])
cat = cat.drop(columns=['ID_GRAFIC','N_VERTEXS','LONG_ARC','NODE_FI','LONG_ARCE','NODE_INI','PROF']) 

# %%
todas_nuevas_lineas =[]
for linea in cat.geometry.iloc[:]:
    # print(linea)
    coords = list(linea.coords)
    new_coords = [coords[0]] #añado el primer punto
    for i in range(len(coords) - 1):
        p1 = coords[i]
        p2 = coords[i + 1]

        # Calcular la distancia en metros entre puntos
        dist = geodesic((p1[1], p1[0]), (p2[1], p2[0])).meters
        # print(f'la distancia es {dist}')
        if dist > 50:
            # Interpolar dos puntos intermedios
            # print(round(dist/50))
            # print('estan mas lejos!!')
            interpolated_points = np.linspace(p1, p2, num=round(dist/50) + 2)[1:-1]
            new_coords.extend(interpolated_points)

        new_coords.append(p2) #añado el segundo, tercer, ..N punto
    nueva_linea= LineString(new_coords)
    todas_nuevas_lineas.append(nueva_linea)
    # print(nueva_linea)
    print('----------------')
# %%
cat.geometry =  todas_nuevas_lineas
# %%
costa =  gpd.read_file("C:/Users/Julia\Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/linea_costa/COSTA/COSTA.shp")
costa_baja = costa.loc[(costa['BAJAMAR']==True) & (costa.geometry.bounds.minx>0.5) & (costa.geometry.bounds.miny>40.5)]
costa_baja['ELEVATION'] = 0
costa_baja['provincia'] = 'cataluña'
costa_baja= costa_baja[[ 'geometry','provincia', 'ELEVATION']]
costa_baja.plot()
# %% interpolar en la linea de costa de cataluña
todas_nuevas_lineas =[]
for linea in costa_baja.geometry.iloc[:]:
    # print(linea)
    coords = list(linea.coords)
    new_coords = [coords[0]] #añado el primer punto
    for i in range(len(coords) - 1):
        p1 = coords[i]
        p2 = coords[i + 1]

        # Calcular la distancia en metros entre puntos
        dist = geodesic((p1[1], p1[0]), (p2[1], p2[0])).meters
        # print(f'la distancia es {dist}')
        if dist > 50:
            # Interpolar dos puntos intermedios
            print(round(dist/50))
            print('estan mas lejos!!')
            interpolated_points = np.linspace(p1, p2, num=round(dist/50) + 2)[1:-1]
            new_coords.extend(interpolated_points)

        new_coords.append(p2) #añado el segundo, tercer, ..N punto
    nueva_linea= LineString(new_coords)
    todas_nuevas_lineas.append(nueva_linea)
    # print(nueva_linea)
    print('----------------')
print('fin')
# %%
costa_baja.geometry =  todas_nuevas_lineas
# %%
#  junto bati con costa
bati_cat = pd.concat([costa_baja, cat], ignore_index=True)
bati_cat.plot(column = 'ELEVATION')
# %% LA POSIDONIA
posidonia = gpd.read_file("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/areas_praderas_PeninsulaBaleares/posidonia_filtrada/output_filtrado.shp")
posi_cata =  posidonia.loc[posidonia['Prov_Isla'].isin(['Barcelona', 'Girona', 'Tarragona'])]
posi_cata = posi_cata.to_crs(4326)
# %%
fig, ax = plt.subplots(figsize=(10, 10))
bati_cat.plot(ax= ax, color = "black", linewidth=0.5)
posi_cata.plot(ax= ax, color = "green", linewidth=50, markersize= 50)
# gpd.GeoDataFrame({'geometry': [parche]}).plot(ax= ax, color = "red")
plt.show()  # COINCIDEN
# %%
contador = 0
lista_puntos  = gpd.GeoDataFrame(columns=[ 'geometry', 'profundidad'], geometry='geometry', crs= 4326) 

# posi_cata = posi_cata.loc[posi_cata['Prov_Isla'] == 'Girona']

for parche in posi_cata.geometry[0:]:
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_catainsula.crs).plot()
    filtered_gdf = bati_cat[bati_cat.geometry.intersects(parche.buffer(0.1))]

    # filtered_gdf.plot(aspect=1, column= 'ELEVATION', legend= True)
    # plt.title('profundidad')
    # plt.show()

    # fig, ax = plt.subplots(figsize=(10, 10))
    # filtered_gdf.plot(ax= ax, color = "grey",linewidth=0.5, markersize = 0.5)
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_cata.crs).plot(ax= ax, color = "red",linewidth=4000, markersize = 500)
    # plt.title('mi parche con la batimetria')
    # plt.show()  # COINCIDEN

    # 2️ Crear una malla de puntos dentro del polígono
    minx, miny, maxx, maxy = parche.bounds  # Límites del polígono
    grid_x, grid_y = np.meshgrid(
        np.linspace(minx, maxx, 50),  # 50 puntos en X
        np.linspace(miny, maxy, 50)   # 50 puntos en Y
    )

    # # Convertimos la malla en una lista de puntos
    # grid_points = np.array([Point(x, y) for x, y in zip(grid_x.ravel(), grid_y.ravel())])
    # grid_points = np.array([p for p in grid_points if parche.contains(p)])  # Filtrar puntos dentro

    # 3️ Obtener puntos y profundidades de los LineStrings
    line_points = []
    depths = []

    for _, row in filtered_gdf.iterrows():
            line = row.geometry
            depth = row['ELEVATION']
            for coord in line.coords:
                punto = Point(coord[0],coord[1] )                
                line_points.append(coord)  # Guardar coordenadas (x, y)
                depths.append(depth) # Guardar profundidad asociada

    line_points = np.array(line_points)  # Convertir a array numpy
    depths = np.array(depths)  # Profundidades

    # 4️ Interpolación de la profundidad en la malla
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
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs= posidonia.crs)

    # print(gdf)
    
    # buscar los que caben en el polygono
    gdf_filtrado = gdf[gdf.geometry.within(parche)]

    # gdf_filtrado.plot(column='profundidad', legend = True)
    # plt.title(f'profundidad {contador}')
    # plt.show()

    lista_puntos = pd.concat([lista_puntos, gdf_filtrado], ignore_index=True)

    contador = contador+1
    print(contador)
    
    # buscar los nulos
    # nulos = gdf[gdf.geometry.isnull()]  # Filtra las filas con geometría nula
    # print(len(nulos))
    
    # for row in range(len(lista_puntos)):
    #     print(lista_puntos.iloc[row].profundidad)

print('FIN')  
# %%
