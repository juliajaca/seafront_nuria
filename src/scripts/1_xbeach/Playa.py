import numpy as np

class Playa:


    lista_profundidades =  np.arange (-0,300000,1 )
    # el rango  tiene que pasar por el 0 y no funciona con valores muy negativos
    # lista_x= [*range(-5,15000,1)]
    # lista_x = np.arange (0,600,2 ) 

    def __init__(self, h,t, h99, t99, d50, prof_inicio, prof_fin = -9999):
        self.h = h
        self.h99 = h99
        self.t99 = t99 
        self.t = t
        self.d50=d50
        self.dean = self.calcular_dean()
        self.prof_inicio = prof_inicio
        self.prof_fin = prof_fin
        self.calcular_bed_berbabeu()
        print(f' el dean es {self.dean}')
        print(f'self bed es {self.bed}')
    
    def calcular_dean(self):
        w = 273* self.d50 **1.1
        print('el w es ')
        print(w)
        return self.h/(w*self.t)

    def calcular_bed_berbabeu(self):
        hr = 1.1 * self.h
        print(f'la hr es {hr}')
        ha = 20 # tiene que llegar a 20 m de profundidad
        print(type(self.dean))
        A = 0.15-0.009*self.dean
        C = 0.03+0.03*self.dean
        depth= 0
        contador = 0
        lista_breaking = list()
        lista_positivos = [] 
        valor = 0
        contador_positivo= 1
        while valor < 5:
            valor = A * abs(self.lista_profundidades[contador_positivo])**(2/3)
            contador_positivo +=1
            lista_positivos.append(valor)
            # print(f'depth en {self.lista_profundidades[contador]} positivo es  {valor}')

        # lista_positivos.pop(0) #quitamos el primer 0. Si empiezo el contador positivo en 1 no se crea el valor 0 y nohay que quitar nada

        while ((depth < hr) ): # hr es 0.74
            # print(lista_x[contador])
            # print(contador)
            depth = A * abs(self.lista_profundidades[contador])**(2/3)
            # print(f'depth en {self.lista_profundidades[contador]} es  {depth}')
            contador += 1   
            lista_breaking.append( depth)

        # print(f'nos ehmos quedado en el contador {contador}')
        lista_breaking.pop()

        contador -=1
        ultimo_numero = lista_breaking[-1]
        primer_numero = C * (self.lista_profundidades[contador-1])**(2/3)

        lista_shoaling = list()
        print(depth)
        print(ha)
        while ((depth < ha) ):  
            # print(ha)
            depth= C * (self.lista_profundidades[contador])**(2/3)
            contador +=1
            depth = depth-primer_numero + ultimo_numero
            # print('zambio de zona')
            # print(f'depth en {self.lista_profundidades[contador]} es  {depth}')
            lista_shoaling.append(depth)
        
        todo = lista_breaking + lista_shoaling
        todo = [-todo[i] if i> todo.index(0) else todo[i] for i in range(len(todo))][::-1] # la X = 0 es la profundidad más grande, por eso doy la vuelta a bed
        todo =  todo + lista_positivos
        self.bed = todo
        # print(self.bed)
    
