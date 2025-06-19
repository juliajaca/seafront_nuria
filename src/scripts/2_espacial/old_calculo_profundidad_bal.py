# %%
import geopandas as gpd
from geopy.distance import geodesic
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
import math
import matplotlib.ticker as mticker
# ------- 
# %%
# -------
# POSIDONIA
# -------
posidonia = gpd.read_file("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/areas_praderas_PeninsulaBaleares/posidonia_filtrada/output_filtrado.shp")
islas = ['Mallorca', 'Menorca', 'Ibiza', ]
posi_bal = posidonia.loc[posidonia['Prov_Isla'].isin(islas)]
# %%
posi_bal.plot()

# -------- LINEA DE COSTA
# %% 
costa =  gpd.read_file("C:/Users/Julia\Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/linea_costa/COSTA/COSTA.shp")
costa_baja = costa.loc[(costa['BAJAMAR']==True) & (costa.geometry.bounds.minx>1) & (costa.geometry.bounds.miny>38.5) & (costa.geometry.bounds.maxy <40.1)]
costa_baja['ELEVATION'] = 0
costa_baja['provincia'] = 'baleares'
costa_baja= costa_baja[['provincia', 'ELEVATION', 'geometry']]
costa_baja= costa_baja.to_crs(posidonia.crs)
costa_baja.plot()

# %%
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
# %% la hago puntos
points = []
for line in costa_baja.geometry:
    for coord in line.coords:
        points.append(Point(coord))
gdf_points = gpd.GeoDataFrame(geometry=points, crs=posidonia.crs)
gdf_points['z'] = 0 

# ''''''''''''''''''''
# '''''BATIMETRIA'''''
# ''''''''''''''''''''
# %%
# AÑADIR BALEARES
def get_geodataframe_batimetria(inputfile='C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/batimetrias_baleares_miguel/bati_mallorca_smc.xyz'):
    df = pd.read_csv(inputfile, delim_whitespace=True, header=None, names = ['x','y','z'])    
    # print(df['z'])
    # for z in df['z']:
    #     print(z)
    df = df[df['z'] <= 30]
    if (df['z'] >= 0).all():
        df['z'] *= -1
    # print(df)
    geometry = [Point(xy) for xy in zip(df['x'], df['y'])]

    gdf =  gpd.GeoDataFrame(df, geometry=geometry, crs= "EPSG:32631")
    gdf = gdf.to_crs(gdf_points.crs)
    print(gdf.crs)
    print(gdf)
    gdf.plot(column='z')
    return gdf

mallorca = get_geodataframe_batimetria()

menorca = get_geodataframe_batimetria('C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/batimetrias_baleares_miguel/bati_menorca_smc.xyz')
ibiza =get_geodataframe_batimetria('C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/batimetrias_baleares_miguel/bati_ibiza_smc.xyz')
formentera = get_geodataframe_batimetria('C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/batimetrias_baleares_miguel/bati_formentera_smc.xyz')

# %% CONCATENO Y tengo un GDF de puntos
bati_bal = pd.concat([mallorca,menorca, ibiza, formentera,  gdf_points], ignore_index=True)
bati_bal.plot(column = 'z')


# %%
# for parche in posidonia.geometry
def calcular_nx_ny_recursivo(minx, miny, maxx, maxy, latitud, distancia):
    dx= distancia /(60*1850*math.cos(latitud*math.pi/180))
    nx = round((maxx-minx)/dx)
    dy = distancia /(60*1850)
    ny = round((maxy-miny)/dy)
    print(f"Distancia: {distancia}, nx: {nx}, ny: {ny}")

    # Verificar si nx y ny cumplen con el mínimo de 25
    if nx >= 25 and ny >= 25:
        return nx, ny, distancia
    elif distancia > 1:  # Evitar que la distancia llegue a valores no realistas
        return calcular_nx_ny_recursivo(minx, miny, maxx, maxy, latitud, distancia * 0.5)
    else:
        print("Distancia mínima alcanzada, pero nx o ny no llegan a 25.")
        return nx, ny, distancia

# %%
contador = 0
lista_puntos  = gpd.GeoDataFrame(columns=[ 'geometry', 'profundidad'], geometry='geometry', crs= posi_bal.crs) 

for parche in posi_bal.geometry[4:100]:
    filtered_gdf = bati_bal[bati_bal.geometry.intersects(parche.buffer(0.05))]

    fig, ax = plt.subplots(figsize=(2, 2))
    gpd.GeoDataFrame(geometry=[parche], crs = posi_bal.crs).plot(ax= ax)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f')) 
    plt.title('mi parche')
    plt.show()

    # fig, ax = plt.subplots(figsize=(2, 2))
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_bal.crs).plot(ax= ax, color = "red")
    # filtered_gdf.plot(ax= ax,aspect=1, column= 'z', linewidth=0.5, legend=True)
    # ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    # ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f')) 
    # plt.title('lineas de batimetria que intersectan con mi parche')
    # plt.show()

    # fig, ax = plt.subplots(figsize=(10, 10))
    # filtered_gdf.plot(ax= ax, color = "grey",linewidth=0.5, markersize = 0.5)
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_bal.crs).plot(ax= ax, color = "red",linewidth=200)
    # plt.title('mi parche con la batimetria')
    # plt.show()  # COINCIDEN

    # 2️⃣ Crear una malla de puntos dentro del polígono
    minx, miny, maxx, maxy = parche.bounds  # Límites del polígono
    # calcular
    # 1   OPCION PUNTOS SEGUN EL TAMAÑOA
    # tupla = calcular_nx_ny_recursivo(minx, miny, maxx, maxy, parche.centroid.y, 50)

    # grid_x, grid_y = np.meshgrid(
    #     np.linspace(minx, maxx, tupla[0]),  # x puntos en X
    #     np.linspace(miny, maxy, tupla[1])   # y puntos en Y
    # )
    # 2 OPCION 50 pUNTOS
    # grid_x, grid_y = np.meshgrid(
    #     np.linspace(minx, maxx, 50),  # 50 puntos en X
    #     np.linspace(miny, maxy, 50)   # 50 puntos en Y
    # )

    # 3  OPCION PUNTOS CADA 10 METROS
    metros = 10
    dist_x = geodesic((minx, 0), (maxx, 0)).meters
    dist_y = geodesic((0, miny), (0, maxy)).meters
    print(dist_x, dist_y)

    grid_x, grid_y = np.meshgrid(
        np.linspace(minx, maxx, round(dist_x/metros)),  # 50 puntos en X
        np.linspace(miny, maxy, round(dist_y/metros))   # 50 puntos en Y
    )
    # El area sera el numero de puntos por 10
    if len(grid_x)==0 or len(grid_y)==0:
        grid_x = np.array ([parche.centroid.x])
        grid_y = np.array([parche.centroid.y])
    # print(grid_x, grid_y)


    # Convertimos la malla en una lista de puntos
    grid_points = np.array([Point(x, y) for x, y in zip(grid_x.ravel(), grid_y.ravel())])
    grid_points = np.array([p for p in grid_points if parche.contains(p)])  # Filtrar puntos dentro
    xy_array = np.array([(p.x, p.y) for p in grid_points])

    if len(xy_array)==0:
        xy_array = np.array([parche.centroid.x, parche.centroid.y])

    line_points = np.array([(point.x, point.y) for point in filtered_gdf.geometry])
    print(line_points)
    # line_points = np.array([(point.x, point.y) for point in bati_bal.geometry])
    
    # 3 Interpolación de la profundidad en la malla
    grid_depths = griddata(line_points, filtered_gdf['z'], xy_array, method='linear')
    # grid_depths = griddata(line_points, bati_bal['z'], (grid_x, grid_y), method='linear')
    print('las profs son')
    print(grid_depths)

    #  HAcer un dataframe
    # # Aplanar las matrices en arrays 1D
    # x_flat = grid_x.ravel()
    # y_flat = grid_y.ravel()
    temp_flat = grid_depths.ravel()

    # Crear lista de objetos Point
    # puntos = [Point(x, y) for x, y in zip(x_flat, y_flat)]
    points = []
    # Si el array es 1D (un solo conjunto de coordenadas)
    if xy_array.ndim == 1:
        # Crear un solo punto
        points.append(Point(xy_array[0], xy_array[1]))

    # Si el array es 2D (múltiples puntos)
    elif xy_array.ndim == 2:
        for i in range(xy_array.shape[0]):
            points.append(Point(xy_array[i, 0], xy_array[i, 1]))

    # Construir un DataFrame yC onvertir a GeoDataFrame
    df = pd.DataFrame({"geometry": points, "profundidad": temp_flat, 'parche': contador,})
    gdf = gpd.GeoDataFrame(df, geometry="geometry" ,crs= posidonia.crs)

    # print(gdf)
    # PLOT TODOS LOS PUNTOS INTERPOLADOS
    gdf.plot(column='profundidad', legend = True)
    plt.title(f'Todos los puntos')
    plt.show() 
    
    # buscar los que caben en el polygono
    # gdf_filtrado = gdf[gdf.geometry.within(parche)]
    # if len(gdf_filtrado) == 0:
    #     gdf_filtrado= gdf
    # print(gdf_filtrado)
    gdf_filtrado = gdf

    lista_puntos = pd.concat([lista_puntos, gdf_filtrado], ignore_index=True)

    contador = contador+1
    
    # buscar los nulos
    nulos = gdf[gdf.geometry.isnull()]  # Filtra las filas con geometría nula
    # print(len(nulos))

    fig, ax = plt.subplots(figsize=(2, 2))
    gdf_filtrado.plot(column='profundidad', legend=True, ax=ax)
    plt.title(f'profundidad {contador}')
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))    
    plt.show()

    print(f'--{contador}-----------------')
print('FIN') 
print(lista_puntos) 
# %%
lista_puntos[2025] =  674 + 24.4 * lista_puntos['profundidad'] 
# %%
# for year in range(1,75):
#     print(year)
#     d_anterior = lista_puntos.iloc[:,-1:]
#     r = d_anterior * 0.05 #por año
#     sst = 25+0.0277*year
#     m_temp =  d_anterior* (0.021 * sst - 0.471)
#     m_frente = 0.07 * d_anterior
#     d_año = d_anterior + r  - m_temp - m_frente
#     print(sst)
#     print(m_temp)
#     print(m_frente)
#     # print(d_año)
#     lista_puntos[year+2025] = d_año
#     # lista_puntos['final'] = columna
# %%
datos = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/SST_AR4_timeseries_Balear.dat', delim_whitespace=True, header=None, skiprows=1)
df =datos.iloc[:, [0, 1]]

# %%
for año in range(2026, 2100):
    valor_modelo = df.loc[df.iloc[:, 0] == año]
    sst = float(valor_modelo.iloc[0, 1])  # Primera fila, segunda columna
    print(sst)
    d_anterior = lista_puntos.iloc[:,-1:]
    r = d_anterior * 0.05 #por año
    m_temp =  d_anterior* (0.021 * sst - 0.471)
    m_frente = 0.07 * d_anterior
    d_año = d_anterior + r  - m_temp - m_frente
    lista_puntos[año] = d_año
    # print(valor_modelo)
    # print(type(valor_modelo))
    print('---')
# %% PLOT MAPAS
# Suponiendo que el GeoDataFrame se llama gdf
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True, sharey=True)

# Definir los años a graficar
years = [2025, 2050, 2099]

# Definir escala de colores común
vmin = lista_puntos[years].min().min()  # Mínima densidad en los 3 años
vmax = lista_puntos[years].max().max()  # Máxima densidad en los 3 años

# Crear los tres plots
for i, year in enumerate(years):
    ax = axes[i]
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f')) 
    lista_puntos.plot(column=year, cmap='viridis', legend=True, ax=ax, vmin=vmin, vmax=vmax)
    ax.set_title(f"Densidad en {year}")
plt.show()

# %%
# Extraer los años (asumiendo que las columnas de densidad son de 2000 a 2010)
years = list(range(2025, 2099))  # Ajusta según tus datos

# Crear la figura
fig, ax = plt.subplots(figsize=(10, 6))

# Iterar sobre cada punto del GeoDataFrame
for idx, row in lista_puntos.iterrows():
    ax.plot(years, row[years], label=f"Punto {idx}")  # Graficar cada punto

# Etiquetas y título
ax.set_xlabel("Año")
ax.set_ylabel("Densidad")
ax.set_title("Evolución de la Densidad en cada Punto")
ax.legend(loc="upper right", fontsize="small", ncol=2)  # Leyenda con múltiples columnas

# Mostrar el gráfico
plt.show()
# %%
fig, ax = plt.subplots(figsize=(2, 2))
lista_puntos.plot(column=2025, cmap='viridis', legend=True, ax=ax,)
ax.set_title(f"Densidad en {2025}")
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
plt.show()
# %%
