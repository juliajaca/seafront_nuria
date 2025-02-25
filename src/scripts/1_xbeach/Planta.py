from enum import Enum
import numpy as np
# https://stackoverflow.com/questions/57171292/is-there-a-way-to-instantiating-a-class-directly-from-an-enum
class Planta(Enum):
#     ['Cymodocea nodosa', 1321.21, 16.935, 0.28]
# ['Halophila decipiens', nan, 1.42, 0.505]
# ['Halophila stipulacea', 2053.3, 4.34, 0.64]
# ['Posidonia oceanica', 337.69, 41.56, 0.93]
# ['Zostera marina', 447.83, 47.4, 0.62]
# ['Zostera noltei', 3699.28, 14.5, 0.13]

    class POSIDONIA_OCEANICA: 
        densidad = 337.69
        altura = 41.56/100
        diametro= 0.93/100

    class CYMODOCEA_NODOSA:
        densidad = 1321.21
        altura = 16.935/100 #Tiene que ser en metros
        diametro = 0.28/100
    
    class ZOSTERA_NOLTII:
        densidad = 3699.28
        altura = 14.5/100
        diametro = 0.13/100

    class HALOPHILA_STIPULACEA:
        densidad = 2053.3
        altura = 4.34/100
        diametro = 0.64/100

    class ZOSTERA_MARINA:
        densidad = 447.83
        altura = 47.4/100
        diametro = 0.62/100


    # class HALOPHILA_DECIPIENS: faltan datos
    #     densidad = np.nan
    #     altura = 1.495/100
    #     diametro = 0.519/100
    
    # class ZOSTERA_NOLTEI: Esto es lo mismo que noltii
    #     densidad = 4791.13
    #     altura = np.nan
    #     diametro = np.nan

    def __call__(self):
        return self.value()    




# planta = Planta.CYMODOCEA_NODOSA()

# print(type(planta).__name__)
