import numpy as np
from pathlib import Path

def write_file(file, string):
    f = open(file, "w")
    f.write(string)
    f.close()

def read_file(file):
    f = open(file, "r")
    print(f.read())
    f.close()

class Modelo:
    folder_path = 'C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/1_xbeach/ficheros/'
    xgrid_file = 'xgrid.grd'
    ygrid_file = 'ygrid.grd'
    bed_file = 'bed.dep'
    params_file = 'params.txt'
    posidoniabed_file = 'posidoniabed.txt'
    jonswap_file = 'jonswap.txt'
    vegetation_file = 'vegetation.txt'

    def __init__(self,  playa, tiempo_ejecucion, parametro_rt):
        self.playa = playa
        self.tiempo_ejecucion = tiempo_ejecucion
        self.parametro_rt = parametro_rt
        # self.diccionario_densidades =  diccionario_densidades
        self.get_diccionario_densidades()
        self.write_bed_file()
        self.write_gridX_file()
        self.write_gridY_file()
        self.write_jonswap_file()
        self.densidades = self.write_posidoniabed_file()
        self.write_params_file()
        print('aqui es lo especual')
        self.manage_density_files()
        self.write_vegetation_file()
    
    def get_diccionario_densidades(self): # 674 - 24.4 * profundidad
        profundidades = np.arange(0, -20, -0.5)
        diccionario_densidades = {
            (inicio, inicio - 0.5): int(round(674 + 24.4 * (inicio - 0.25), 0) )
            for inicio in profundidades}
        
        # diccionario_densidades = {
        #     (inicio, inicio - 0.5): 644
        #     for inicio in profundidades}
        # valores_unicos = {densidad: idx + 1 for idx, densidad in enumerate(diccionario_densidades.values())}
        # print(valores_unicos)
        self.diccionario_densidades = diccionario_densidades
        
    def write_vegetation_file(self):
        string = ''
        print(self.densidades)
        for i in range(len(self.densidades)):
            string += f'densidad{i}.txt\n'
        print('la string del file vegetation.txt es ')
        print(string)
        write_file(self.folder_path+self.vegetation_file, string)
    
    def manage_density_files(self):
        self.delete_density_files()
        self.write_densidad_files()

    def delete_density_files(self):
        direc = Path(self.folder_path)
        for archivo in direc.glob('densidad*.txt'):
            archivo.unlink()
    
    def write_densidad_files(self):
        for i in range(len(self.densidades)):
            print(f'vuelta{i}')
            posidonia_string = self.get_planta_string(self.densidades[i])
            write_file(self.folder_path+f'densidad{i}.txt', posidonia_string)

    def get_planta_string(self, densidad):
        return f'''
nsec = 1
ah = 1
bv = 0.01
N = {densidad}
Cd = 0.2
        '''


    def write_gridX_file(self):
        xs_string = ' '.join(str(x) for x in range(len(self.playa.bed)))
        write_file(self.folder_path+self.xgrid_file, xs_string)

    def write_gridY_file(self):
        ys = [0] * (len(self.playa.bed))
        ys_string = ' '.join(str(x) for x in ys)
        write_file(self.folder_path+self.ygrid_file, ys_string)

    def write_bed_file(self):
        bed_string = '  '.join(str(x) for x in self.playa.bed)
        write_file(self.folder_path+self.bed_file, bed_string)

    def write_params_file(self):
        params_string = self.get_params_string()
        write_file(self.folder_path+self.params_file, params_string)

    def write_jonswap_file(self):
        jonswap_string = self.get_jonswap_string()
        write_file(self.folder_path+self.jonswap_file, jonswap_string)
    


    def write_posidoniabed_file(self):
        posidoniabed_list = np.array([0] * len(self.playa.bed))
        print(self.diccionario_densidades)
        valores_unicos = {densidad: idx + 1 for idx, densidad in enumerate(self.diccionario_densidades.values())}
        print(valores_unicos)
        lista_densidades = []
        orden_densidad =1
        for (inicio, fin), densidad in self.diccionario_densidades.items():
            print(f'el inicnio es {inicio} y el fin es {fin}')
            mascara = (self.playa.bed <= inicio) & ( self.playa.bed >fin ) & (np.array(self.playa.bed) <= self.playa.prof_inicio) & (np.array(self.playa.bed) > self.playa.prof_fin)  # Detectar solapamiento
            print(f'la densidad es {densidad}')
            print(f'hay{np.count_nonzero(mascara)} trues')
            posidoniabed_list[mascara] = valores_unicos[densidad]  # Asignar el valor correspondiente

            if np.count_nonzero(mascara)>0:
                lista_densidades.append(densidad)
                posidoniabed_list[mascara] = orden_densidad 
                orden_densidad += 1

        posidoniabed_string = ' '.join(str(x) for x in posidoniabed_list)
        write_file(self.folder_path+self.posidoniabed_file, posidoniabed_string)
        return lista_densidades

    def get_jonswap_string(self):
        return f'''
Hm0 = {self.playa.h99}
fp = {1/self.playa.t99}
mainang    =     270
gammajsp   =     3.3000
s          =    10.0000
fnyq       =     1.0000
            '''
    
    def get_params_string(self):
        print(f'el nx es {len(self.playa.bed)-1}')
        return f'''
        686*%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% XBeach parameter settings input file                                     %%%
%%%                                                                          %%%
%%% date:     09-Sep-2011 09:45:52                                           %%%
%%% function: xb_write_params                                                %%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% Grid parameters %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

depfile   = bed.dep
posdwn    = 0
nx        = {len(self.playa.bed)-1}
ny        = 0
alfa      = 0
vardx     = 1
xfile     = xgrid.grd
yfile     = ygrid.grd
xori      = 0
yori      = 0
thetamin  = 260
thetamax  = 280
dtheta    = 5
thetanaut = 1
useXBeachGSettings = 0

%%% fricción con fondo %%%%%%%%
bedfriction  = manning
bedfriccoef  = 0.02

%%% ARCHIVOS POSIDONIA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

vegetation    = 1
veggiefile    = vegetation.txt
veggiemapfile = posidoniabed.txt
nveg          = {len(self.densidades)}

%%% Initial conditions %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

zs0       = 0

%%% Model time %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

tstop     = {self.tiempo_ejecucion}

%%% Wave boundary condition parameters %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
nonh      = 1
instat    = jons
random    = 0

%%% Wave-spectrum boundary condition parameters %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

bcfile    = jonswap.txt
rt        = {self.parametro_rt}
dtbc      = 2

%%% Output variables %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

tstart       = 0
tintg        = 1
outputformat = netcdf
nrugauge     = 1
0 0
nglobalvar   = 2
zs
H
        '''

