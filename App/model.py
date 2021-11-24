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
from DISClib.ADT import orderedmap as om
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.Algorithms.Graphs import scc,dijsktra
import math
from math import radians, cos, sin, asin, sqrt
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
        "TreeAirports" : om.newMap(),
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

    clean = {
        "IATA":airport["IATA"],
        "Latitude":float(airport["Latitude"]),
        "Longitude":float(airport["Longitude"])
    }

    Long = clean["Longitude"]
    Lat = clean["Latitude"]
    if om.contains(catalog["TreeAirports"], Lat):
        arbolLong = me.getValue(om.get(catalog["TreeAirports"], Lat))
        if not om.contains(arbolLong, Long):
            om.put(arbolLong, Long, clean)
        
    else:
        om.put(catalog["TreeAirports"], Lat, om.newMap())
        arbolLong = me.getValue(om.get(catalog["TreeAirports"], Lat))
        if not om.contains(arbolLong, Long):
            om.put(arbolLong, Long, clean)



def add_route(catalog, route):
    departure = route["Departure"]
    destination = route["Destination"]

    dgraph = catalog["routesdg"]
    graph = catalog["routesndg"]

    routeOrder = tuple(sorted((departure, destination)))

    if not mp.contains(catalog["DuplicateRoute"], (departure, destination)):
        if gph.containsVertex(dgraph, departure) and gph.containsVertex(dgraph, destination):
            gph.addEdge(dgraph,departure, destination, float(route["distance_km"]))
        elif not gph.containsVertex(dgraph, departure) and not gph.containsVertex(dgraph, destination):
            gph.insertVertex(dgraph, departure)
            gph.insertVertex(dgraph, destination)
            gph.addEdge(dgraph, departure, destination, float(route["distance_km"]))
        elif not gph.containsVertex(dgraph, departure):
            gph.insertVertex(dgraph, departure)
            gph.addEdge(dgraph, departure, destination, float(route["distance_km"]))
        else:
            gph.insertVertex(dgraph, destination)
            gph.addEdge(dgraph, departure, destination, float(route["distance_km"]))
        
        if catalog["1AirportDG"] is None:
            catalog["1AirportDG"] = departure
        mp.put(catalog["DuplicateRoute"], (departure, destination), None)

    if mp.contains(catalog["DuplicateRoute"], (destination, departure)) and not mp.contains(catalog["DRg"], routeOrder):
        
        if gph.containsVertex(graph, departure) and gph.containsVertex(graph, destination):
            gph.addEdge(graph,departure, destination, float(route["distance_km"]))
        elif not gph.containsVertex(graph, departure) and not gph.containsVertex(graph, destination):
            gph.insertVertex(graph, departure)
            gph.insertVertex(graph, destination)
            gph.addEdge(graph, departure, destination, float(route["distance_km"]))
        elif not gph.containsVertex(graph, departure):
            gph.insertVertex(graph, departure)
            gph.addEdge(graph, departure, destination, float(route["distance_km"]))
        else:
            gph.insertVertex(graph, destination)
            gph.addEdge(graph, departure, destination, float(route["distance_km"]))
        
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

def getMostInterconnections(catalog):
    #Agregar un nuevo arbol donde estan todas las rutas pero es no dirigido, asi calcular degree-outdegree para encontrar indegree con menor O()
    dg = catalog["routesdg"]
    g = catalog["routesndg"]

    l_dg = lt.newList(datastructure="ARRAY_LIST")
    l_g = lt.newList(datastructure="ARRAY_LIST")

    max_dg = 0 

    for vertex in lt.iterator(gph.vertices(dg)):
        indegree = gph.indegree(dg, vertex)
        outdegree = gph.outdegree(dg,vertex)
        if outdegree >= 1:
            if indegree > max_dg:
                max_dg = indegree
                l_dg = lt.newList(datastructure="ARRAY_LIST")
                lt.addLast(l_dg,vertex)
            elif indegree == max_dg:
                lt.addLast(l_dg, vertex)

    max_g = 0
    for vertex in lt.iterator(gph.vertices(g)):
        degree = gph.degree(g, vertex)
        if degree > max_g:
            max_g = degree
            l_g = lt.newList(datastructure="ARRAY_LIST")
            lt.addLast(l_g,vertex)
        elif degree == max_g:
            lt.addLast(l_g, vertex)

    mapIATA = catalog["IATA2name"]
    
    mapFunc(l_dg, lambda x: me.getValue(mp.get(mapIATA,x)))
    mapFunc(l_g, lambda x: me.getValue(mp.get(mapIATA,x)))

    
    
    return (max_dg, l_dg),(max_g, l_g)

def mapFunc(l, func):
    for i in range(1,lt.size(l)+1):
        lt.changeInfo(l,i, func(lt.getElement(l,i)))

def getFlightTrafficClusters(catalog, IATA1, IATA2):
    kscc = scc.KosarajuSCC(catalog["routesdg"])
    num_clusters = scc.connectedComponents(kscc)
    connected = scc.stronglyConnected(kscc, IATA1, IATA2)
    return num_clusters, connected


def getShortestRoute(catalog, city1, city2):
    #https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance formula grado/km
    
    min_disto,airOrigin,min_distd,airDest = findNearestAirports(catalog,city1, city2)

    IATAo = airOrigin["IATA"]
    IATAd = airDest["IATA"]

    route = dijsktra.Dijkstra(catalog["routesdg"],IATAo)


    routePath = dijsktra.pathTo(route,IATAd)
    distancePath = dijsktra.distTo(route,IATAd)

    return airOrigin, airDest, routePath, distancePath,min_disto, min_distd


#Funciones auxiliares
def haversine(lat1, lon1, lat2, lon2):
    #https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    R = 6372.8 # this is in miles.  For Earth radius in kilometers use 6372.8 km
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))
    return R * c

def findNearestAirports(catalog, city1, city2):
    city1 = me.getValue(mp.get(catalog["Cities"], city1))
    city2 = me.getValue(mp.get(catalog["Cities"], city2))

    olat, olong = float(city1["lat"]), float(city1["lng"])
    dlat, dlong = float(city2["lat"]), float(city2["lng"])

    treeLat = catalog["TreeAirports"]

    foundAirport = False
    r = 10

    airOrigin = None
    airDest = None
    min_disto = float("inf")
    min_distd = float("inf")
    while not foundAirport and r <= 1000:
        olatSquare = r//2 * 0.009
        olongSquare = r//2 * (abs(0.009/math.cos(olat*(math.pi/180))))

        dlatSquare = r//2 * 0.009
        dlongSquare = r//2 * (abs(0.009/math.cos(dlat*(math.pi/180))))

        olatmin, olatmax = olat-olatSquare, olat+olatSquare
        dlatmin, dlatmax = dlat-dlatSquare, dlat+dlatSquare

        olongmin, olongmax = olong-olongSquare, olong+olongSquare
        dlongmin, dlongmax = dlong-dlongSquare, dlong+dlongSquare

        
        if airOrigin is None:
            for treeLong in lt.iterator(om.values(treeLat, olatmin, olatmax)):
                for airport in lt.iterator(om.values(treeLong, olongmin, olongmax)):
                    dist = haversine(airport["Latitude"], airport["Longitude"], olat, olong)
                    if dist < min_disto:
                        min_disto = dist
                        airOrigin = airport
        
        if airDest is None:
            for treeLong in lt.iterator(om.values(treeLat, dlatmin, dlatmax)):
                for airport in lt.iterator(om.values(treeLong, dlongmin, dlongmax)):
                    dist = haversine(airport["Latitude"], airport["Longitude"], dlat, dlong)
                    if dist < min_distd:
                        min_distd = dist
                        airDest = airport
        
        if (airOrigin is not None) and (airDest is not None):
            foundAirport = True

        r += 10
    return (min_disto, airOrigin, min_distd, airDest)


# Funciones utilizadas para comparar elementos dentro de una lista



# Funciones de ordenamiento
