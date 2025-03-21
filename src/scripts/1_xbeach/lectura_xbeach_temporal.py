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
# %%
df["Valor"] = pd.to_numeric(df["Valor"])
# Crear el gráfico de línea
plt.figure(figsize=(8, 5))
plt.plot(df["Nombre"], round(df["Valor"],2), marker="o", linestyle="-", color="b", label="Valor")
plt.xticks(rotation=90)
plt.xticks(df["Nombre"][::5])
plt.xlabel("año")
plt.ylabel("ru")
plt.title("Runup en la playa l'almadrava")
plt.show()
# %%
