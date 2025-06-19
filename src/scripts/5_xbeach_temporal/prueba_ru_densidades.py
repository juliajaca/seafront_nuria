# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys


import os
sys.path.append(os.path.abspath("C:/Users/Julia/Documents/VSCODE/src/carpeta_ignorada/9_paper/"))
from funciones import take_closest, get_depth_index

# %%
path = 'C:/Users/Julia/Documents/VSCODE/src/carpeta_ignorada/7_calculo_nuevas_matrices_atlantico/MATRICES/'
posidonia200 = np.stack((
                    np.loadtxt(path+'POSIDONIA_200_0.5.txt'),
                    np.loadtxt(path+'POSIDONIA_200_2.txt'),
                    np.loadtxt(path+'POSIDONIA_200_5.txt'),
                     np.loadtxt(path+'POSIDONIA_200_7.txt')))

posidonia400 = np.stack((
                     np.loadtxt(path+'POSIDONIA_400_0.5.txt'),
                    np.loadtxt(path+'POSIDONIA_400_2.txt'),
                    np.loadtxt(path+'POSIDONIA_400_5.txt'),
                     np.loadtxt(path+'POSIDONIA_400_7.txt')))

posidonia600 = np.stack((
                     np.loadtxt(path+'POSIDONIA_05_600.txt'),
                    np.loadtxt(path+'POSIDONIA_2_600.txt'),
                    np.loadtxt(path+'POSIDONIA_5_600.txt'),
                     np.loadtxt(path+'POSIDONIA_7_600.txt')))

posidonia0 = np.loadtxt(path+'SIN_PLANTA.txt')

lista_deans = [13.27, 7.568,5.515,4.315,3.530,2.573,2.013,1.647,1.390,1.200,1.054,0.939, 0.869 ]

olas_todo = [[0.5, 11], [1,11], [1,18],[1.5,10], [1.5, 11], [1.5,19], [1.5,20],
        [2,10],[2,11], [2,18], [2,19], [2,20], [2,21],
        [2.5,9],[2.5,10],[2.5,11], [2.5, 18],[2.5, 19], [2.5,20],
        [3,10],[3,11], [3,17], [3,18], [3,19], [3,20],
        [3.5,10],[3.5,17],[3.5,18],[3.5,19],
        [4,10],[4,16], [4,17], [4,18], [4,19], 
        [4.5,10], [4.5 ,16], [4.5, 17], [4.5,18], [4.5,19],
        [5,16], [5,17], [5,18], [5,19], [5.5,17],[5.5,18],[5.5,19],
        [6,17], [6,18], [6,19],[6.5,17],[6.5,18],
        [7,17],[7,18]]

listaH = [x for x,y in olas_todo]
listaT = [y for x,y in olas_todo]

# %%
play = pd.read_csv('C:/Users/Julia/Documents/VSCODE/src/carpeta_ignorada/9_paper/med_con_ss.csv', sep=';')
play= play.loc[play['lon'] >= -5.61].reset_index(drop=True) # quito cadiz atlantico
print(len(play))

# %%
play = play.loc[play['d50']<1] #quitamos los d50 grandes
print(len(play))
play = play.loc[play['d50']!=-999] #quitamos los d50 que no tengo
print(len(play))
play= play.reset_index(drop=True)
fig, ax = plt.subplots(1,1)
sc =ax.scatter(x=play['lon'],y= play['lat'],  s =10)
plt.show()
# %%
for i in range(len(play[:1])):
    i=1
    print(i)
    prof_planta = play.iloc[i]['profundidad']
    d50 = (play.iloc[i]['d50'])/1000

    #  calculo perfil
    h = play.iloc[i]['DOW_hsm_mean']
    t = play.iloc[i]['DOW_Tpm_mean']
    dean = h/((273 * d50**1.1)*(t))
    ola = np.array([play.iloc[i]["DOW_Hs99_mean"],play.iloc[i]["DOW_Tp99_mean"]])
    print(f'planta --> {prof_planta} m, d50 --> {d50}, h--> {h}, t-->{t}, dean -->{dean}, ola --> {ola}')

    # para pruebas, sale este array
    #array([[0.2402186 , 0.2402186 , 0.2402186 , 0.2402186 , 0.2402186 ],
    #    [0.15513411, 0.21724975, 0.23148698, 0.2335527 , 0.2402186 ],
    #    [0.10791428, 0.19856644, 0.22346873, 0.23048899, 0.2402186 ],
    #    [0.08236263, 0.1807039 , 0.21527274, 0.22369121, 0.2402186 ]])
    dean = 11
    ola = np.array([0.5,10])

    closestDean = take_closest(lista_deans[::-1],dean )

    index_matrix_perfiles =  lista_deans.index(closestDean)
    n_perfil = lista_deans.index(closestDean) +1
    print(f'el perfil es {n_perfil}')

    # Calculate Euclidean distance between the beach wave and each wave combination  and Find the index of the minimum distance
    index_matrix_seastate = np.argmin(np.linalg.norm(np.array(olas_todo) - ola, axis=1))

    print(f'min index es {index_matrix_seastate} con ola {ola}')

    # %%
    # fila de la matriz donde tengo el ru para todas las profundidaes
    ru600= posidonia600[:,index_matrix_perfiles, index_matrix_seastate]
    print(ru600)
    ru400= posidonia400[:,index_matrix_perfiles, index_matrix_seastate]
    print(ru400)
    ru200= posidonia200[:,index_matrix_perfiles, index_matrix_seastate]
    print(ru200)
    ru0 = posidonia0[index_matrix_perfiles, index_matrix_seastate]
    print(ru0)
    todo = np.stack((ru200, ru400, ru600))
    print(todo)
    # Añadir una columna detras y una fila encima con el valor de sin planta
    todo = np.hstack([ todo,np.full((todo.shape[0], 1), ru0)])
    
    densities = np.array([0, 200, 400, 600])
    depths = np.array([0.5, 2, 5, 7, 20])

    todo = np.vstack([ np.full((1, todo.shape[1]), ru0), todo])
    print('----------')
    print(todo)
# %%
def bilinear_ru_interp(depth, density, ru_matrix, depths, densities):
    # Clamp valores a los rangos
    if depth <= depths[0]:
        print('fuera ranto por abajo')
        i_low = i_high = 0
    elif depth >= depths[-1]:
        print('fuera de rango por arruba')
        i_low = i_high = len(depths) - 1
        print(i_low)
    elif depth in depths:
        i_low = i_high = np.where(depths == depth)[0][0]
    else:
        i_high = np.searchsorted(depths, depth)
        i_low = i_high - 1

    if density <= densities[0]:
        print('fuera de rango por arruba')
        j_low = j_high = 0
    elif density >= densities[-1]:
        print('fuera de rango por arruba')
        j_low = j_high =  len(densities) - 1
    elif density in densities:
        j_low = j_high = np.where(densities == density)[0][0]
    else:
        j_high = np.searchsorted(densities, density)
        j_low = j_high - 1
    print(f'las profundaides sn {i_low}, {i_high}')
    print(f'las densidades sin {j_low}, {j_high}')

    d1, d2 = depths[i_low], depths[i_high]
    dens1, dens2 = densities[j_low], densities[j_high]
    print(f'las depths son {d1} y {d2}, las desities {dens1} y {dens2}')

    # Valores en los vértices
    q11 = ru_matrix[j_low, i_low]
    q12 = ru_matrix[j_low, i_high] #estas 2 son las profundides
    q21 = ru_matrix[j_high, i_low]
    q22 = ru_matrix[j_high, i_high] #estas 2 son las densidades
    print('las q1 son')
    print(q11)
    print(q12)
    print('lasq2 son')
    print(q21)
    print(q22)

    # Interpolación lineal (bilineal simplificada si fuera en un borde)
    if d1 == d2 and dens1 == dens2:
        return q11
    elif d1 == d2: #las profundidades son iguales
        # Interpolar solo en densidad
        print('profundidades iguales')
        alpha = (density - dens1) / (dens2 - dens1)
        return q11 * (1 - alpha) + q21 * alpha
    elif dens1 == dens2:
        # Interpolar solo en profundidad
        alpha = (depth - d1) / (d2 - d1)
        return q11 * (1 - alpha) + q12 * alpha
    else:
        # Bilinear
        alpha = (depth - d1) / (d2 - d1)  # Factor de interpolación para profundidad (eje Y)
        beta = (density - dens1) / (dens2 - dens1) # Factor de interpolación para densidad (eje X)

        # Interpolamos para las profundidades
        top = q11 * (1 - alpha) + q12 * alpha 

        #Interpolamos para las densidades
        bottom = q21 * (1 - alpha) + q22 * alpha 

        # Luego interpolamos entre esos dos resultados a lo largo de la densidad
        return top * (1 - beta) + bottom * beta



# %%
sst = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/SST_AR4_timeseries_Balear.dat', delim_whitespace=True, header=None, skiprows=1)
df_sst =sst.iloc[:, [0, 1]]

# %%
#  la densidad inicial
densidades =  [674 + 24.4 * -5 ]

for año in range(2026, 2100):
    valor_modelo = df_sst.loc[df_sst.iloc[:, 0] == año]
    sst = float(valor_modelo.iloc[0, 1])  # Primera fila, segunda columna
    # print(sst)
    d_anterior =densidades[-1]
    r = d_anterior * 0.05 # reclutamento por año
    m_temp =  d_anterior* (0.021 * sst - 0.471) #muerte por calo
    m_frente = 0.07 * d_anterior # muerte del frente

    d_año = d_anterior + r  - m_temp - m_frente
    densidades.append(d_año)
    # print(valor_modelo)
    # print(type(valor_modelo))
    print(d_año, año)
    print('---')
print('fin')
# %%
lista_rus= []
for densidad in densidades:
    # print(f'la densidad es {densidad}')
    ru= bilinear_ru_interp(depth=-prof_planta, density=densidad, ru_matrix=todo, depths=depths, densities=densities)
    print(f'para la densidad {densidad } a profundidad {prof_planta} el ru es {ru}')
    print('-----')
    lista_rus.append(ru)   

# %% 
# plt.figure(figsize=(10, 5))
plt.plot(range(2025, 2100), lista_rus, marker='o', linestyle='-', color='teal')
plt.title("Serie temporal de RU (2025–2099) para playa de la Almadrava (Alicante)")
plt.xlabel("Año")
plt.ylabel("Valor RU")
plt.grid(True)
plt.tight_layout()
plt.show()                                            
# %%
