﻿"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
import sys
import controller
from DISClib.ADT import list as lt
assert cf


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("Bienvenido")
    print("1- Crear el catálogo")
    print("2- Cargar información en el catálogo")
    print("3- REQ. 1: Encontrar puntos de interconexión aérea")
    print("4- REQ. 2: Encontrar clústeres de tráfico aéreo")
    print("5. REQ. 3: Encontrar la ruta más corta entre ciudades")
    print("6. REQ. 4: Utilizar las millas de viajero")
    print("7. REQ. 5: Cuantificar el efecto de un aeropuerto cerrado")  
    print("8. REQ. 6 (BONO): Comparar con servicio WEB externo")  
    print("9. REQ. 7 (BONO): Visualizar gráficamente los requerimientos") 
    print("0- Salir")

catalog = None

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        print("Cargando información de los archivos ....")

    elif int(inputs[0]) == 2:
        pass

    else:
        sys.exit(0)
sys.exit(0)
