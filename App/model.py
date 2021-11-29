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
from DISClib.DataStructures import mapentry as me, edge as e
from DISClib.ADT import orderedmap as om, queue
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.Algorithms.Graphs import scc,dijsktra, prim, bfs
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
        "MST": {"TotCost":None, "NumNodes":None, "GraphMST":None},
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
    if mp.contains(catalog["Cities"], name):
        lt.addLast(me.getValue(mp.get(catalog["Cities"], name)),city)
    else:
        mp.put(catalog["Cities"], name, lt.newList("ARRAY_LIST"))
        lt.addLast(me.getValue(mp.get(catalog["Cities"], name)),city)

def loadMST(catalog):
    graph = catalog["routesndg"]
    numNodes = lt.size(gph.vertices(graph))
    search = prim.PrimMST(graph)
    totCost = prim.weightMST(graph,search)
    graphMST = gph.newGraph()
    for i in lt.iterator(search["mst"]):
        addToGraph(graphMST,i)

    mst = catalog["MST"]

    mst["TotCost"] = totCost
    mst["NumNodes"] = numNodes
    mst["GraphMST"] = graphMST

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
        indegree = gph.degree(dg, vertex)
        outdegree = gph.outdegree(dg,vertex)
        degree = indegree+outdegree
        if degree > max_dg:
            max_dg = degree
            l_dg = lt.newList(datastructure="ARRAY_LIST")
            lt.addLast(l_dg,vertex)
        elif degree == max_dg:
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



def getFlightTrafficClusters(catalog, IATA1, IATA2):
    kscc = scc.KosarajuSCC(catalog["routesdg"])
    num_clusters = scc.connectedComponents(kscc)
    connected = scc.stronglyConnected(kscc, IATA1, IATA2)
    return num_clusters, connected


def getShortestRoute(catalog, city1, city2):
    #https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance formula grado/km
    
    min_disto,airOrigin = findNearestAirport(catalog,city1)
    min_distd,airDest = findNearestAirport(catalog, city2)

    IATAo = airOrigin["IATA"]
    IATAd = airDest["IATA"]

    route = dijsktra.Dijkstra(catalog["routesdg"],IATAo)


    routePath = dijsktra.pathTo(route,IATAd)
    distancePath = dijsktra.distTo(route,IATAd)

    return airOrigin, airDest, routePath, distancePath,min_disto, min_distd

def getUseFlyerMiles(catalog, city, miles):
    km = miles*1.60
    mst = catalog["MST"]
    numNodes = mst["NumNodes"]
    totCost = mst["TotCost"]
    graphMST = mst["GraphMST"]

    md,airport = findNearestAirport(catalog, city,False)
    IATA = airport["IATA"]

    bfsSearch = BreadhtFisrtSearch(graphMST, IATA)
    maxDist = getLongestBranch(bfsSearch)
    maxVertex = me.getKey(lt.getElement(me.getValue(mp.get(bfsSearch["DisToSource"],maxDist)),1))
    rMaxBranch = bfs.pathTo(bfsSearch,maxVertex)
    
    dest = None
    weight = km
    for i in range(maxDist,0,-1):
        lst = me.getValue(mp.get(bfsSearch["DisToSource"],i))
        for j in lt.iterator(lst):
            weightTo = getWeightTo(me.getValue(j))
            if weightTo <= weight:
                dest = j
                weight = weightTo
    
        if dest is not None:
            break
    
    if dest is not None:
        route = bfs.pathTo(bfsSearch, dest["key"])
        routeList = lt.newList("ARRAY_LIST")
        for air in lt.iterator(route):
            infoair = me.getValue(mp.get(catalog["IATA2name"],air))
            cityr, country = infoair["City"], infoair["Country"]
            lt.addLast(routeList,(cityr,country))
        return (1, numNodes, totCost, rMaxBranch, routeList)
    else:
        return 2, numNodes, totCost, rMaxBranch

def getCalculateClosedAirportEffect(catalog, air):
    dgraph = catalog["routesdg"]
    destiny = lt.newList("ARRAY_LIST")
    origin = lt.newList("ARRAY_LIST")
    for vertex in lt.iterator(gph.vertices(dgraph)):
        if vertex == air:
            adj = gph.adjacents(dgraph, vertex)
            for i in lt.iterator(adj):
                lt.addLast(destiny, i)
        else:
            adj = gph.adjacents(dgraph,vertex)
            if lt.isPresent(adj, air):
                lt.addLast(origin, vertex)

    totAffected = lt.size(destiny)+lt.size(origin)

    return destiny, origin, totAffected

def getShortestRouteAPI(catalog, origen, destino, client):
    clientAM = client


    latO, longO = float(origen["lat"]), float(origen["lng"])
    latD, longD = float(destino["lat"]), float(destino["lng"])

    responseO = clientAM.reference_data.locations.airports.get(latitude=latO, longitude =longO)

    responseD = clientAM.reference_data.locations.airports.get(latitude=latD, longitude =longD)
    dg = catalog["routesdg"]

    if len(responseD.data) > 0 and len(responseO.data) > 0:
        airo = None
        disto = 0
        for i in responseO.data:
            iata = i["iataCode"]
            if gph.containsVertex(dg,iata):
                airo = iata
                disto = i["distance"]["value"]
                break
        aird = None
        distd = 0
        for i in responseD.data:
            iata = i["iataCode"]
            if gph.containsVertex(dg,iata):
                aird = iata
                distd = i["distance"]["value"]
                break
        
        if (airo is not None) and (aird is not None):

            path = dijsktra.Dijkstra(dg, airo)
            if dijsktra.hasPathTo(path, aird):
                route = dijsktra.pathTo(path, aird)
                dist = dijsktra.distTo(path, aird)
                return airo, aird, route, dist, disto, distd
            else:
                return False, 1 , "No hay una ruta entre los dos aeropuertos", airo, aird, disto, distd
        else:
            return False, 2,"No hay información en la base datos sobre alguno o los dos aeropuertos proporcionado por el API"
        
    else:
        return (False, 3, "El API no retorno información sobre alguna de las ciudades")


#Funciones auxiliares
def checkCity(catalog, city):
    if mp.contains(catalog["Cities"], city):
        cities = me.getValue(mp.get(catalog["Cities"],city))
        if lt.size(cities) > 1:
            return 1,cities
        else:
            return 2, lt.getElement(me.getValue(mp.get(catalog["Cities"],city)),1)
    else:
        return False

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

def mapFunc(l, func):
    for i in range(1,lt.size(l)+1):
        lt.changeInfo(l,i, func(lt.getElement(l,i)))

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

def BreadhtFisrtSearch(graph, source):
    """
    Genera un recorrido BFS sobre el grafo graph
    Args:
        graph:  El grafo a recorrer
        source: Vertice de inicio del recorrido.
    Returns:
        Una estructura para determinar los vertices
        conectados a source
    Raises:
        Exception
    """
    
    search = {
              'source': source,
              'visited': None,
              'MaxDist':0,
              "DisToSource": None
              }
    search['visited'] = mp.newMap(numelements=gph.numVertices(graph),
                                   maptype='PROBING',
                                   comparefunction=graph['comparefunction']
                                   )
    search['DisToSource'] = mp.newMap(numelements=gph.numVertices(graph),
                                   maptype='PROBING',
                                   comparefunction=graph['comparefunction']
                                   )
    mp.put(search['visited'], source, {'marked': True,
                                        'edgeTo': None,
                                        'distTo': 0,
                                        "weightTo":0
                                        })
    mp.put(search["DisToSource"], 0, mp.get(search["visited"],source))
    bfsVertex(search, graph, source)
    return search


def bfsVertex(search, graph, source):
    """
    Funcion auxiliar para calcular un recorrido BFS
    Args:
        search: Estructura para almacenar el recorrido
        vertex: Vertice de inicio del recorrido.
    Returns:
        Una estructura para determinar los vertices
        conectados a source
    Raises:
        Exception
    """
    
    adjsqueue = queue.newQueue()
    queue.enqueue(adjsqueue, source)
    while not (queue.isEmpty(adjsqueue)):
        vertex = queue.dequeue(adjsqueue)
        visited_v = mp.get(search['visited'], vertex)['value']
        adjslst = gph.adjacents(graph, vertex)
        for w in lt.iterator(adjslst):
            visited_w = mp.get(search['visited'], w)
            if visited_w is None:
                dist_to_w = visited_v['distTo'] + 1
                if dist_to_w > search["MaxDist"]:
                    search["MaxDist"] = dist_to_w
                weight_to_w = visited_v["weightTo"] + e.weight(gph.getEdge(graph, vertex, w))
                visited_w = {'marked': True,
                             'edgeTo': vertex,
                             "distTo": dist_to_w,
                             "weightTo": weight_to_w
                             }
                mp.put(search['visited'], w, visited_w)
                if mp.contains(search["DisToSource"], dist_to_w):
                    lt.addLast(me.getValue(mp.get(search["DisToSource"],dist_to_w)),me.newMapEntry(w, visited_w))
                else:
                    mp.put(search["DisToSource"],dist_to_w, lt.newList("ARRAY_LIST"))
                    lt.addLast(me.getValue(mp.get(search["DisToSource"],dist_to_w)),me.newMapEntry(w,visited_w))
                
                queue.enqueue(adjsqueue, w)
    return search

def getLongestBranch(search):
    return search["MaxDist"]

def getWeightTo(visited):
    return visited["weightTo"]


def addToGraph(graph, edge):
    vertexA = edge["vertexA"]
    vertexB = edge["vertexB"]
    weight = edge["weight"]

    if gph.containsVertex(graph,vertexA) and gph.containsVertex(graph,vertexB):
        gph.addEdge(graph,vertexA,vertexB, weight)
    elif not gph.containsVertex(graph,vertexA) and not gph.containsVertex(graph,vertexB):
        gph.insertVertex(graph,vertexA)
        gph.insertVertex(graph,vertexB)
        gph.addEdge(graph,vertexA,vertexB,weight)
    elif not gph.containsVertex(graph,vertexA):
        gph.insertVertex(graph,vertexA)
        gph.addEdge(graph,vertexA,vertexB,weight)
    else:
        gph.insertVertex(graph,vertexB)
        gph.addEdge(graph,vertexA,vertexB,weight)

def findNearestAirport(catalog, city1, typeG = True):
    # city1 = me.getValue(mp.get(catalog["Cities"], city1))


    olat, olong = float(city1["lat"]), float(city1["lng"])

    treeLat = catalog["TreeAirports"]

    foundAirport = False
    r = 10
    typeGraph = "routesdg" if typeG else "routesndg"

    airOrigin = None
    min_disto = float("inf")
    while not foundAirport and r <= 1000:
        olatSquare = r//2 * 0.009
        olongSquare = r//2 * (abs(0.009/math.cos(olat*(math.pi/180))))


        olatmin, olatmax = olat-olatSquare, olat+olatSquare
        olongmin, olongmax = olong-olongSquare, olong+olongSquare

        if airOrigin is None:
            for treeLong in lt.iterator(om.values(treeLat, olatmin, olatmax)):
                for airport in lt.iterator(om.values(treeLong, olongmin, olongmax)):
                    dist = haversine(airport["Latitude"], airport["Longitude"], olat, olong)
                    if gph.containsVertex(catalog[typeGraph], airport["IATA"]):
                        if dist < min_disto:
                            min_disto = dist
                            airOrigin = airport
            
        
        if (airOrigin is not None):
            foundAirport = True

        r += 10
    return min_disto, airOrigin
# Funciones utilizadas para comparar elementos dentro de una lista



# Funciones de ordenamiento
