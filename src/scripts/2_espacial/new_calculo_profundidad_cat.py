# %%
import geopandas as gpd
from shapely.geometry import LineString, Point
from io import BytesIO
import matplotlib.ticker as mticker
from geopy.distance import geodesic
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib widget
import matplotlib.pyplot as plt
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

# %% interpolar la batimetria
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
            print('estan mas lejos!!')
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
# Agregar el índice de cada polígono en su posición
for idx, row in posi_cata.iterrows():
    centroid = row.geometry.centroid  # Obtener el centro del polígono
    ax.text(centroid.x, centroid.y, str(idx), fontsize=12, color='red', ha='center', va='center')
plt.show()
# gpd.GeoDataFrame({'geometry': [parche]}).plot(ax= ax, color = "red")
plt.show()  # COINCIDEN
# %%
contador = 0
lista_puntos  = gpd.GeoDataFrame(columns=[ 'geometry', 'profundidad'], geometry='geometry', crs= 4326 )

for parche in posi_cata.geometry[1:2]:
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_catainsula.crs).plot()
    filtered_gdf = bati_cat[bati_cat.geometry.intersects(parche.buffer(0.1))] #esta es la que va bien
    # filtered_gdf = bati_cat[bati_cat.geometry.intersects(parche.buffer(0.001))] #pruebas para pintar mapas

    # filtered_gdf.plot(aspect=1, column= 'ELEVATION', legend= True)
    # plt.title('profundidad')
    # plt.show()

    fig, ax = plt.subplots(figsize=(10, 10))
    filtered_gdf.plot(ax= ax,cmap= 'viridis', legend = True,linewidth=5, markersize = 5, column = 'ELEVATION')
    gpd.GeoDataFrame(geometry=[parche], crs = posi_cata.crs).plot(ax= ax, color = "red",linewidth=4000, markersize = 500)
    gpd.GeoDataFrame(geometry=[parche.centroid], crs = posi_cata.crs).plot(ax= ax, color = "black", markersize = 100)
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
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs= 4326)
    # print(gdf)

    # PLOT TODOS LOS PUNTOS INTERPOLADOS
    # gdf.plot(column='profundidad', legend = True)
    # plt.title(f'Todos los puntos')
    # plt.show() 
    
    fig, ax = plt.subplots(figsize=(2, 2))
    gdf.plot(column='profundidad', legend=True, ax=ax)
    plt.title(f'profundidad {contador}')
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))    
    plt.show()

    contador = contador+1
    # print(lista_puntos)
    lista_puntos = pd.concat([lista_puntos, gdf], ignore_index=True)

    print(f'--{contador}-----------------')

print('FIN') 
print(lista_puntos) 
# %%
# lista_puntos["geometry"] = lista_puntos["geometry"].apply(lambda geom: geom.wkt)
# lista_puntos.to_csv("bat_parches_cat.csv", index=False)

#  ABRIR EN GOOGLE EARTH
# gpd.GeoDataFrame(geometry=[parche], crs = posi_cata.crs).to_file("poligonos.kml", driver="KML")