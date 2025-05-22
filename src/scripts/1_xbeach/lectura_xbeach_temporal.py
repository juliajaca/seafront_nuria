# %%
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# %%
# Ruta de la carpeta donde están los archivos
carpeta = Path("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/1_xbeach/playa_almadrava")

# Listas para almacenar los datos
valores = []
nombres = []

# Recorrer los archivos en la carpeta
for archivo in carpeta.glob("*.txt"):  # Solo archivos .txt
    # Leer el contenido del archivo
    contenido = archivo.read_text(encoding="utf-8").strip()
    valores.append(contenido)  # Agregar el contenido a la lista
    nombres.append(archivo.stem[-4:])  # Últimos 4 caracteres del nombre sin extensión

# Crear el DataFrame
df = pd.DataFrame({"Nombre": nombres, "Valor": valores})
print(df)
df["Valor"] = pd.to_numeric(df["Valor"])

# %% Playa2
carpeta = Path("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/1_xbeach/playa_almadrava2")

# Listas para almacenar los datos
valores = []
nombres = []

# Recorrer los archivos en la carpeta
for archivo in carpeta.glob("*.txt"):  # Solo archivos .txt
    # Leer el contenido del archivo
    contenido = archivo.read_text(encoding="utf-8").strip()
    valores.append(contenido)  # Agregar el contenido a la lista
    nombres.append(archivo.stem[12:16])
df2 = pd.DataFrame({"Nombre": nombres, "Valor": valores})
print(df)

df2["Valor"] = pd.to_numeric(df2["Valor"])

# %% Playa3
carpeta = Path("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/1_xbeach/almadrava3")

# Listas para almacenar los datos
valores = []
nombres = []

# Recorrer los archivos en la carpeta
for archivo in carpeta.glob("*.txt"):  # Solo archivos .txt
    # Leer el contenido del archivo
    contenido = archivo.read_text(encoding="utf-8").strip()
    valores.append(contenido)  # Agregar el contenido a la lista
    nombres.append(archivo.stem[22:26])
df3 = pd.DataFrame({"Nombre": nombres, "Valor": valores})
print(df3)
df3["Valor"] = pd.to_numeric(df3["Valor"])

# %% Playa3
carpeta = Path("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/1_xbeach/almadrava5")

# Listas para almacenar los datos
valores = []
nombres = []

# Recorrer los archivos en la carpeta
for archivo in carpeta.glob("*.txt"):  # Solo archivos .txt
    # Leer el contenido del archivo
    contenido = archivo.read_text(encoding="utf-8").strip()
    valores.append(contenido)  # Agregar el contenido a la lista
    nombres.append(archivo.stem[22:26])
df4 = pd.DataFrame({"Nombre": nombres, "Valor": valores})
print(df4)
df4["Valor"] = pd.to_numeric(df4["Valor"])

# %%
# Crear el gráfico de línea
plt.figure(figsize=(8, 5))
plt.axhline(y=1.51, color='black', linestyle='--', label="matrices d50=0.3, sin pradera")
plt.plot(df["Nombre"], round(df["Valor"],2), marker="o", linestyle="-", color="red", label="d50=0.3, inicio pradera -3")

plt.axhline(y=1.14, color='red', linestyle='--', label="matrices d50=0.3, inicio pradera -3")

plt.plot(df2["Nombre"], round(df2["Valor"],2), marker="o", linestyle="-", color="blue", label="d50=0.3, inicio pradera -1")
plt.axhline(y=0.94, color='blue', linestyle='--', label="matrices d50=0.3, inicio pradera -1")

plt.axhline(y=1.36, color='saddlebrown', linestyle='--', label="matrices d50=0.97, sin pradera")
plt.plot(df3["Nombre"], round(df3["Valor"],2), linestyle="-", color="darkorange", label="d50=0.97, inicio pradera -3")
plt.axhline(y=0.74, color='darkorange', linestyle='--', label="matrices d50=0.97, inicio pradera -3")

plt.plot(df4["Nombre"], round(df4["Valor"],2), linestyle="-", color="green", label="d50=0.97, inicio pradera -1")
plt.axhline(y=0.47, color='green', linestyle='--', label="matrices d50=0.97, inicio pradera -1")
plt.legend()
plt.xticks(rotation=90)
plt.xticks(df["Nombre"][::5])
plt.xlabel("año")
plt.ylabel("ru")
plt.title("Runups")
plt.show()
# %%
