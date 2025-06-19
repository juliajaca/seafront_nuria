# %%
import numpy as np
import matplotlib.pyplot as plt
# %%
path = 'C:/Users/Julia/Documents/VSCODE/src/carpeta_ignorada/7_calculo_nuevas_matrices_atlantico/MATRICES/'

posidonia_0 = np.loadtxt(path+'SIN_PLANTA.txt') #13 * 53
posidonia_200 = np.loadtxt(path+'POSIDONIA_200_0.5.txt')
posidonia_400 = np.loadtxt(path+'POSIDONIA_400_0.5.txt')
posidonia_600 = np.loadtxt(path+'POSIDONIA_05_600.txt')

# %% ME Quedo con un perfil y pinto todas las olas
posidonia_0_perfil= posidonia_0[6]
posidonia_400_perfil= posidonia_400[6]
posidonia_600_perfil= posidonia_600[6]
posidonia_200_perfil= posidonia_200[6]

estados_mar = [[0.5, 11], [1,11], [1,18],[1.5,10], [1.5, 11], [1.5,19], [1.5,20],
        [2,10],[2,11],  [2,18], [2,19], [2,20], [2,21],
        [2.5,9],[2.5,10],[2.5,11], [2.5, 18],[2.5, 19], [2.5,20],
        [3,10],[3,11], [3,17], [3,18], [3,19], [3,20],
        [3.5,10],[3.5,17],[3.5,18],[3.5,19],
        [4,10],[4,16], [4,17], [4,18], [4,19], 
        [4.5,10], [4.5 ,16], [4.5, 17], [4.5,18], [4.5,19],
        [5,16], [5,17], [5,18], [5,19], [5.5,17],[5.5,18],[5.5,19],
        [6,17], [6,18], [6,19],[6.5,17],[6.5,18],
        [7,17],[7,18]]
densidades = [0, 200, 400, 600] 
# Crear figura
fig, ax = plt.subplots(figsize=(10, 8))

# Dibujar una línea por cada estado de mar
for i in range(53):
    valores_y = [posidonia_0_perfil[i], posidonia_200_perfil[i], posidonia_400_perfil[i], posidonia_600_perfil[i]]
    ax.plot(densidades, valores_y, label=estados_mar[i])  # baja opacidad para ver superposición

# Opcional: Etiquetas
ax.set_xticks(densidades)
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize="small", ncol=1)

# Ajustar para que quepa todo
ax.set_xlabel("Densidad de planta")
ax.set_ylabel("RU")
ax.set_title("RU por densidad para cada estado del mar (empieza a 0.5)")
ax.grid(True)
plt.tight_layout(rect=[0, 0, 0.78, 1])
plt.show()


# %% Me quedo con una ola y pinto todo el perfil --> OLA [1.5,10]
posidonia_0_d50= posidonia_0[:,3]
posidonia_200_d50= posidonia_200[:,3]
posidonia_400_d50= posidonia_400[:,3]
posidonia_600_d50= posidonia_600[:,3]
# %%
d50s =  [13.27, 7.568,5.515,4.315,3.530,2.573,2.013,1.647,1.390,1.200,1.054,0.939, 0.869 ]
fig, ax = plt.subplots(figsize=(10, 8))

# Dibujar una línea por cada estado de mar
for i in range(13):
    valores_y = [posidonia_0_d50[i], posidonia_200_d50[i] ,posidonia_400_d50[i], posidonia_600_d50[i]]
    ax.plot(densidades, valores_y, label=d50s[i])

# Opcional: Etiquetas
ax.set_xticks(densidades)
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize="small", ncol=1)

# Ajustar para que quepa todo
ax.set_xlabel("Densidad de planta")
ax.set_ylabel("RU")
ax.set_title("RU por densidad para cada d50")
ax.grid(True)
plt.tight_layout(rect=[0, 0, 0.78, 1])
plt.show()


# %%
# PRADERA QUE EMPIEZA A 2 m, me quedo con un perfil y pinto todas las olas
posidonia_0 = np.loadtxt(path+'SIN_PLANTA.txt') #13 * 53
posidonia_400 = np.loadtxt(path+'POSIDONIA_400_2.txt')
posidonia_200 = np.loadtxt(path+'POSIDONIA_200_2.txt')
posidonia_600 = np.loadtxt(path+'POSIDONIA_2_600.txt')

posidonia_0_perfil= posidonia_0[6]
posidonia_200_perfil= posidonia_200[6]
posidonia_400_perfil= posidonia_400[6]
posidonia_600_perfil= posidonia_600[6]

fig, ax = plt.subplots(figsize=(10, 8))
for i in range(53):
    valores_y = [posidonia_0_perfil[i], posidonia_200_perfil[i], posidonia_400_perfil[i], posidonia_600_perfil[i]]
    ax.plot(densidades, valores_y, label=estados_mar[i])  

ax.set_xticks(densidades)
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize="small", ncol=1)
ax.set_xlabel("Densidad de planta")
ax.set_ylabel("RU")
ax.set_title("RU por densidad para cada estado del mar (empiezo a 2m)")
ax.grid(True)
plt.tight_layout(rect=[0, 0, 0.78, 1])
plt.show()
# %%
# FIGURA DENSIDADES CADA 100 M
# %%
ola_pequeña= [0.19475298692602866,0.14939960575538141, 0.13833013595547053, 0.11487763169614143, 0.10071564412520584, 0.08862365940367985 ,0.07850687999745445,   ]

ola_grande = [1.6811555074034017, 1.0106396797349582, 0.6971957626569396, 0.4896303142209408, 0.3705438969313865, 0.2929994739099559 ,0.24747814939210627]
densidades = range(0,700,100)

fig, ax = plt.subplots(figsize=(10, 8))
ax.plot( densidades,ola_pequeña, label='ola pequeña 0.6788, 5.2827')  
ax.plot( densidades, ola_grande,label='ola grande 3,10')  

ax.set_xticks(densidades)
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize="small", ncol=1)
ax.set_xlabel("Densidad de planta")
ax.set_ylabel("RU")
ax.set_title("RU por cada densidad de posidonia")
ax.grid(True)
plt.tight_layout(rect=[0, 0, 0.78, 1])
plt.show()
# %%
