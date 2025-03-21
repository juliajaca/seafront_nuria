# %%
import geopandas as gpd
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib widget
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from scipy.interpolate import griddata
import math
import matplotlib.ticker as mticker
# ------- 
# %%
# -------
# POSIDONIA
# -------
posidonia = gpd.read_file("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/areas_praderas_PeninsulaBaleares/posidonia_filtrada/output_filtrado.shp")
islas = ['Mallorca', 'Menorca', 'Ibiza', ]
posi_bal = posidonia.loc[posidonia['Prov_Isla'].isin(islas)].reset_index(drop=True)
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
    df = df[df['z'] <= 40]
    if (df['z'] >= 0).all():
        df['z'] *= -1
    # print(df)
    geometry = [Point(xy) for xy in zip(df['x'], df['y'])]

    gdf =  gpd.GeoDataFrame(df, geometry=geometry, crs= "EPSG:32631")
    gdf = gdf.to_crs(gdf_points.crs)
    print(gdf.crs)
    print(gdf)
    # gdf.plot(column='z') #quito el plot que tarda mucho
    return gdf

mallorca = get_geodataframe_batimetria()

menorca = get_geodataframe_batimetria('C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/batimetrias_baleares_miguel/bati_menorca_smc.xyz')
ibiza =get_geodataframe_batimetria('C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/batimetrias_baleares_miguel/bati_ibiza_smc.xyz')
formentera = get_geodataframe_batimetria('C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/batimetrias_baleares_miguel/bati_formentera_smc.xyz')

# %% CONCATENO Y tengo un GDF de puntos
bati_bal = pd.concat([mallorca,menorca, ibiza, formentera,  gdf_points], ignore_index=True)
bati_bal.plot(column = 'z')

# %%
# PLOT PARA VER DONDE ESTAN
fig, ax = plt.subplots(figsize=(10, 10))
bati_bal.plot(ax= ax, color = "black", linewidth=0.00001)
posi_bal[6094:6095].plot(ax= ax, color="green", edgecolor="black", linewidth=0.1, alpha=0.5)
# Agregar el índice de cada polígono en su posición
for idx, row in posi_bal[6094:6095].iterrows():
    centroid = row.geometry.centroid  # Obtener el centro del polígono
    ax.text(centroid.x, centroid.y, str(idx), fontsize=12, color='red', ha='center', va='center')
plt.show()
# gpd.GeoDataFrame({'geometry': [parche]}).plot(ax= ax, color = "red")
# COINCIDEN

# %%
contador = 0
lista_puntos  = gpd.GeoDataFrame(columns=['geometry', 'profundidad'], geometry='geometry', crs= posi_bal.crs) 

for parche in posi_bal.geometry[6094:6095]:
    filtered_gdf = bati_bal[bati_bal.geometry.intersects(parche.buffer(0.05))]# original
    filtered_gdf = bati_bal[bati_bal.geometry.intersects(parche.buffer(0.0005))]


    # fig, ax = plt.subplots(figsize=(2, 2))
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_bal.crs).plot(ax= ax)
    # ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    # ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f')) 
    # plt.title('mi parche')
    # plt.show()

    # fig, ax = plt.subplots(figsize=(2, 2))
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_bal.crs).plot(ax= ax, color = "red")
    # filtered_gdf.plot(ax= ax,aspect=1, column= 'z', linewidth=0.5, legend=True)
    # ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    # ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f')) 
    # plt.title('lineas de batimetria que intersectan con mi parche')
    # plt.show()

    # fig, ax = plt.subplots(figsize=(10, 10))
    # filtered_gdf.plot(ax= ax,cmap= 'viridis', legend = True,linewidth=5, markersize = 5, column = 'z')
    # gpd.GeoDataFrame(geometry=[parche], crs = posi_bal.crs).plot(ax= ax, color = "red",linewidth=4000, markersize = 500)
    # gpd.GeoDataFrame(geometry=[parche.centroid], crs = posi_bal.crs).plot(ax= ax, color = "black", markersize = 100)
    # plt.title('mi parche con la batimetria')
    # plt.show()  # COINCIDEN
 
    # 2️⃣ Crear una malla de puntos dentro del polígono
    minx, miny, maxx, maxy = parche.bounds  # Límites del polígono
    # PUNTOS CADA 10 METROS
    metros = 10
    dist_x = geodesic((minx, 0), (maxx, 0)).meters
    dist_y = geodesic((0, miny), (0, maxy)).meters
    # print(dist_x, dist_y)

    # grid_x, grid_y = np.meshgrid(
    #     np.linspace(minx, maxx, round(dist_x/metros)),
    #     np.linspace(miny, maxy, round(dist_y/metros))   
    # )
    grid_x, grid_y = np.meshgrid(
        np.linspace(minx, maxx, 50),
        np.linspace(miny, maxy, 50)   
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

    line_points = np.array([(point.x, point.y) for point in filtered_gdf.geometry])
    # print(line_points) #de lista de puntos a lista xy
    
    # 3 Interpolación de la profundidad en la malla
    print('voy a interpolar')
    grid_depths = griddata(line_points, filtered_gdf['z'], xy_array, method='linear')
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
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs= posidonia.crs)
    # print(gdf)

    # PLOT TODOS LOS PUNTOS INTERPOLADOS
    # gdf.plot(column='profundidad', legend = True)
    # plt.title(f'Todos los puntos')
    # plt.show() 
    
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(column='profundidad', legend=True, ax=ax)
    plt.title(f'profundidad {contador}')
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))    
    plt.show()

    contador = contador+1
    lista_puntos = pd.concat([lista_puntos, gdf], ignore_index=True)

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
