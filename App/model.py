"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import graph as gph
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def create_catalog():
    catalog = {
        "routesdg" : gph.newGraph(directed=True, size=10000),
        "routesndg": gph.newGraph(size=3000),
        # "name2IATA" : mp.newMap(10000,maptype="PROBING"),
        "IATA2name" : mp.newMap(10000,maptype="PROBING"),
        "DuplicateRoute" : mp.newMap(50000,maptype="PROBING"),
        "Cities": mp.newMap(41002,maptype="PROBING"),
        "DRg" : mp.newMap(10000,maptype="PROBING"),
        "1AirportDG" : None,
        "1AirportG" : None,
        "LastCity" : None

    }

    return catalog

# Funciones para agregar informacion al catalogo

def add_airport(catalog, airport):
    table = catalog["IATA2name"]
    IATA = airport["IATA"]
    if not mp.contains(table,IATA):
        mp.put(table, IATA, airport)


def add_route(catalog, route):
    departure = route["Departure"]
    destination = route["Destination"]

    dgraph = catalog["routesdg"]
    graph = catalog["routesndg"]

    routeOrder = tuple(sorted((departure, destination)))

    if not mp.contains(catalog["DuplicateRoute"], (departure, destination)):
        if gph.containsVertex(dgraph, departure) and gph.containsVertex(dgraph, destination):
            gph.addEdge(dgraph,departure, destination, route["distance_km"])
        elif not gph.containsVertex(dgraph, departure) and not gph.containsVertex(dgraph, destination):
            gph.insertVertex(dgraph, departure)
            gph.insertVertex(dgraph, destination)
            gph.addEdge(dgraph, departure, destination, route["distance_km"])
        elif not gph.containsVertex(dgraph, departure):
            gph.insertVertex(dgraph, departure)
            gph.addEdge(dgraph, departure, destination, route["distance_km"])
        else:
            gph.insertVertex(dgraph, destination)
            gph.addEdge(dgraph, departure, destination, route["distance_km"])
        
        if catalog["1AirportDG"] is None:
            catalog["1AirportDG"] = departure
        mp.put(catalog["DuplicateRoute"], (departure, destination), None)

    if mp.contains(catalog["DuplicateRoute"], (destination, departure)) and not mp.contains(catalog["DRg"], routeOrder):
        
        if gph.containsVertex(graph, departure) and gph.containsVertex(graph, destination):
            gph.addEdge(graph,departure, destination, route["distance_km"])
        elif not gph.containsVertex(graph, departure) and not gph.containsVertex(graph, destination):
            gph.insertVertex(graph, departure)
            gph.insertVertex(graph, destination)
            gph.addEdge(graph, departure, destination, route["distance_km"])
        elif not gph.containsVertex(graph, departure):
            gph.insertVertex(graph, departure)
            gph.addEdge(graph, departure, destination, route["distance_km"])
        else:
            gph.insertVertex(graph, destination)
            gph.addEdge(graph, departure, destination, route["distance_km"])
        
        if catalog["1AirportG"] is None:
            catalog["1AirportG"] = departure
        mp.put(catalog["DRg"], routeOrder, None)

def add_city(catalog, city):
    name = city["city_ascii"]
    catalog["LastCity"] = city
    mp.put(catalog["Cities"], name, city)

# Funciones para creacion de datos

# Funciones de consulta
def getLoadingData(catalog):
    data = {
        "#AirDG" : lt.size(gph.vertices(catalog["routesdg"])),
        "#AirG" :  lt.size(gph.vertices(catalog["routesndg"])),
        "#Cities": mp.size(catalog["Cities"]),
        "FirstAirportDG" : None,
        "FirstAirportG": None,
        "LastCity" : catalog["LastCity"]
    }
    data["FirstAirportDG"] = me.getValue(mp.get(catalog["IATA2name"], catalog["1AirportDG"]))
    data["FirstAirportG"] = me.getValue(mp.get(catalog["IATA2name"], catalog["1AirportG"]))

    return data

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento
