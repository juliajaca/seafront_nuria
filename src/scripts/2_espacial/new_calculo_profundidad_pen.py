# %%
import geopandas as gpd
import matplotlib.pyplot as plt
# %matplotlib widget
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, MultiLineString
from scipy.interpolate import griddata
from geopy.distance import geodesic

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
posi_pen =  posidonia.loc[~posidonia['Prov_Isla'].isin(['Mallorca', 'Menorca', 'Ibiza', 'Islas Chafarinas', 'Barcelona', 'Tarragona', 'Girona'])]
# %%
posidonia.plot()
# # %% hecho aparte en un fichero que cargo despues porque tardaba mucho cada vez
# batimetria = gpd.read_file('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/batimetria_med/dataframe_med_julia.shp')
# batimetria = batimetria.to_crs(posi_pen.crs)
# costa_baja = costa_baja.to_crs(posi_pen.crs)

# # %%
# batimetria2 = pd.concat([batimetria, costa_baja], ignore_index=True)
# # %%
# # INTERPOLAR LA BATIMETRIA
# todas_nuevas_lineas =[]
# for linea in batimetria2.geometry.iloc[:]:

#     if(isinstance(linea, MultiLineString)): #si es multistring dejala como esta
#         nueva_linea= linea
#     else:
#         coords = list(linea.coords)

#         new_coords = [coords[0]] #añado el primer punto
#         for i in range(len(coords) - 1):
#             p1 = coords[i]
#             p2 = coords[i + 1]

#             # Calcular la distancia en metros entre puntos
#             dist = geodesic((p1[1], p1[0]), (p2[1], p2[0])).meters
#             # print(f'la distancia es {dist}')
#             if dist > 50:
#                 # Interpolar dos puntos intermedios
#                 # print(round(dist/50))
#                 print('estan mas lejos!!')
#                 interpolated_points = np.linspace(p1, p2, num=round(dist/50) + 2)[1:-1]
#                 new_coords.extend(interpolated_points)

#             new_coords.append(p2) #añado el segundo, tercer, ..N punto
#         nueva_linea= LineString(new_coords)
#     todas_nuevas_lineas.append(nueva_linea)
#     # print(nueva_linea)
#     print('-----------tarda 24 min-----')
# # %%
# batimetria2.geometry =  todas_nuevas_lineas

# %%
batimetria2 = gpd.read_file('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/batimetria_med_interpolada/mi_shapefile.shp')
# %%
contador = 0
lista_puntos  = gpd.GeoDataFrame(columns=[ 'geometry', 'profundidad'], geometry='geometry', crs= posi_pen.crs) 

for parche in posi_pen.geometry[148:149]:
        # gpd.GeoDataFrame(geometry=[parche], crs = posi_catainsula.crs).plot()
    filtered_gdf = batimetria2[batimetria2.geometry.intersects(parche.buffer(0.1))] #esta es la que va bien
    # filtered_gdf = bati_cat[bati_cat.geometry.intersects(parche.buffer(0.001))] #pruebas para pintar mapas

    # filtered_gdf.plot(aspect=1, column= 'ELEVATION', legend= True)
    # plt.title('profundidad')
    # plt.show()

    fig, ax = plt.subplots(figsize=(10, 10))
    filtered_gdf.plot(ax= ax,cmap= 'viridis', legend = True,linewidth=5, markersize = 5, column = 'ELEVATION')
    gpd.GeoDataFrame(geometry=[parche], crs = posi_pen.crs).plot(ax= ax, color = "red",linewidth=4000, markersize = 500)
    gpd.GeoDataFrame(geometry=[parche.centroid], crs = posi_pen.crs).plot(ax= ax, color = "black", markersize = 100)
    plt.title('mi parche con la batimetria')
    plt.show()  # COINCIDEN
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

    # 2Crear una malla de puntos dentro del polígono
    minx, miny, maxx, maxy = parche.bounds  # Límites del polígono
   # PUNTOS CADA 10 METROS
    metros = 10
    dist_x = geodesic((minx, 0), (maxx, 0)).meters
    dist_y = geodesic((0, miny), (0, maxy)).meters
    # print(dist_x, dist_y)

    grid_x, grid_y = np.meshgrid(
        np.linspace(minx, maxx, round(dist_x/metros)),  # 50 puntos en X
        np.linspace(miny, maxy, round(dist_y/metros))   # 50 puntos en Y
    )
    # El area sera el numero de puntos por 10
    if len(grid_x)==0 or len(grid_y)==0:
        grid_x = np.array ([parche.centroid.x])
        grid_y = np.array([parche.centroid.y])
    # print(grid_x, grid_y)

    grid_points = np.array([Point(x, y) for x, y in zip(grid_x.ravel(), grid_y.ravel())])  # malla a  lista de puntos
    grid_points = np.array([p for p in grid_points if parche.contains(p)])  # Filtrar puntos dentro
    xy_array = np.array([(p.x, p.y) for p in grid_points]) #de lista de ppuntos a lista x,y

    if len(xy_array)==0:
        xy_array = np.array([parche.centroid.x, parche.centroid.y])

    # line_points = np.array([(point.x, point.y) for point in filtered_gdf.geometry])
    # print(line_points) #de lista de puntos a lista xy
    
    # 3 Interpolación de la profundidad en la malla
    grid_depths = griddata(line_points, depths, xy_array, method='linear')
    # print('las profs son')
    # print(grid_depths)

    #  HAcer un dataframe
    # Aplanar las matrices en arrays 1D
    temp_flat = grid_depths.ravel()

    # Crear lista de objetos Point
    points = []
    # Si el array es 1D (un solo conjunto de coordenadas)
    if xy_array.ndim == 1:
        # Crear un solo punto
        points.append(Point(xy_array[0], xy_array[1]))

    # Si el array es 2D (múltiples puntos)
    elif xy_array.ndim == 2:
        for i in range(xy_array.shape[0]):
            points.append(Point(xy_array[i, 0], xy_array[i, 1]))

    # Construir un DataFrame y C onvertir a GeoDataFrame
    df = pd.DataFrame({"geometry": points, "profundidad": temp_flat, 'parche': contador,})
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs= posi_pen.crs)
    # print(gdf)

    # PLOT TODOS LOS PUNTOS INTERPOLADOS
    # gdf.plot(column='profundidad', legend = True)
    # plt.title(f'Todos los puntos')
    # plt.show() 
    
    fig, ax = plt.subplots(figsize=(2, 2))
    gdf.plot(column='profundidad', legend=True, ax=ax)
    plt.title(f'profundidad {contador}')
    # ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    # ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))    
    plt.show()

    contador = contador+1
    # print(lista_puntos)
    lista_puntos = pd.concat([lista_puntos, gdf], ignore_index=True)

    print(f'--{contador}-----------------')
print('FIN')  
# %%