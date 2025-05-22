# %%
import os
import pandas as pd
from unidecode import unidecode
import numpy as np
import re
import matplotlib.pyplot as plt
'''
FECHA SINIESTRO
2020-01-26    
2001-11-11    
2009-01-25   
2017-01-22    
2017-02-05     
'''
# %%
dinero= pd.read_excel("C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/seguros/225-RREE Inun+Emb - Litoral 1996-2020.xlsx", skiprows=5, index_col='FECHA SINIESTRO')

#  %%
dinero['POBLACION'] = (dinero['POBLACION']).astype("string").str.lower().apply(unidecode)
dinero['MUNICIPIO'] = (dinero['MUNICIPIO']).str.lower().apply(unidecode)
dinero.loc[dinero['PROVINCIA'] == 'Balears, Illes', 'PROVINCIA'] ='Illes Balears'

dinero['PROVINCIA'] = dinero['PROVINCIA'].str.lower().apply(unidecode)
dinero = dinero.loc[dinero['CAUSA SINIESTRO'] == 'CAUSAS NATURALES/EMBATE DE MAR']

bal = dinero.loc[dinero['PROVINCIA'] == 'illes balears']

# %%
# 2020-01-26 (GLORIA; ENTRE EL 19 y el 21 de enero) https://es.wikipedia.org/wiki/Borrasca_Gloria
fechas1 = ['2020-01-18 00:00:00', '2020-01-19 00:00:00', '2020-01-20 00:00:00', '2020-01-21 00:00:00','2020-01-22 00:00:00','2020-01-25 00:00:00',]
bal_fechas1 = bal.loc[bal.index.isin(fechas1)]

# 2001-11-11 (del 11 al 17)
fechas2 = ['2001-11-10 00:00:00', '2001-11-11 00:00:00', '2001-11-13 00:00:00','2001-11-15 00:00:00','2001-11-16 00:00:00','2001-11-17 00:00:00',]
bal_fechas2 = bal.loc[bal.index.isin(fechas2)]

# 2009-01-25   TODAS EN MENORCA OESTE
fechas3= ['2009-01-24 00:00:00','2009-01-23 00:00:00','2009-01-25 00:00:00',]
bal_fechas3 = bal.loc[bal.index.isin(fechas3)]

# 2017-01-22 
fechas4= ['2017-01-20 00:00:00','2017-01-21 00:00:00','2017-01-22 00:00:00','2017-01-23 00:00:00']
bal_fechas4 = bal.loc[bal.index.isin(fechas4)]

# 2017-02-05   todo menorca oeste
fechas5= ['2017-02-05 00:00:00','2017-02-06 00:00:00','2017-02-08 00:00:00']
bal_fechas5 = bal.loc[bal.index.isin(fechas5)]
# %%
