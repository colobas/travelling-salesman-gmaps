import googlemaps
import requests
import collections
import json
from datetime import datetime
import time
import random
import sys
import math
import hashlib

def globals():
 	global returnHome
 	global fixedEnd
 	global fixedOrigin
 	returnHome = False
 	fixedEnd = False
 	fixedOrigin = False

def randomRestart(items):
	shuffled = list(items)
	if(fixedOrigin):
		shuffled = list(shuffled[1:]) # se a origem for fixa nao baralha o primeiro e adiciona no topo
	if(fixedEnd):
	 	shuffled = list(shuffled[:-1]) # se o fim for fixo nao baralha o último e adiciona no fundo

	random.shuffle(shuffled)
    
	if(fixedOrigin):
		shuffled.insert(0,items[0]) # origem fixa -> adiciona no topo o primeiro introduzido pelo user
	if(fixedEnd):
		shuffled.append(items[-1]) # fim fixo -> adiciona no fundo o primeiro introduzido pelo user

	if(returnHome):
		shuffled.append(shuffled[0]) # se voltar a casa, adiciona no fundo o primeiro da lista

	return shuffled

def rad(x):
	return x * math.pi/180


def getDistanceFromAtoB(placeA,placeB):
	url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins='+placeA.replace(' ','+')+'&destinations='+placeB.replace(' ','+')+'&departure_time='+str(int(time.mktime(datetime.now().timetuple())))+'&mode=driving&traffic_model=best_guess&key=AIzaSyBDRaVrNOA74dFlno67A_pEMKNQHA5bPvk'
	r = requests.get(url)
	x = json.loads(r.text)['rows'][0]['elements']#[0]['distance']['value']
	if x[0]['status']=='OK':
		return x[0]['distance']['value']
	if x[0]['status']=='ZERO_RESULTS':
		gmaps = googlemaps.Client(key='AIzaSyBDRaVrNOA74dFlno67A_pEMKNQHA5bPvk')
		A_coord = gmaps.geocode(placeA)[0]['geometry']['location']
		B_coord = gmaps.geocode(placeB)[0]['geometry']['location']
		R = 6378137
		dLat = rad(B_coord['lat'] - A_coord['lat'])
		dLong = rad(B_coord['lng'] - A_coord['lng'])
		a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(rad(A_coord['lat'])) * math.cos(rad(B_coord['lat'])) * math.sin(dLong / 2) * math.sin(dLong / 2);
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
		d = R * c
		return int(d)

	sys.stdout.write("\rERRO:")
	sys.stdout.flush()
	print("\n\n"+r.text+"\n\n")
	raise SystemExit

def getScore(route, edges):
	score = 0
	for i in range(0,len(route)-1):
		score = score + edges[route[i]][route[i+1]]
	return score

def listToString(lista):
	return ''.join(lista)

def hashStr(astring, tablesize):
	return int(hashlib.md5(astring.encode('utf-8')).hexdigest(), 16) % tablesize

def getMaxNeighbour(rota, edges):
	aux = list(rota)	
	aux_score = 0
	best = list(rota)
	best_score = sys.maxsize
	if returnHome or (fixedOrigin and fixedEnd):
		i = 0
		for placeA in aux[1:-1]:
			i=i+1
			j=0
			for placeB in aux[1:-1]:
				j=j+1
				if(placeA==placeB):
					break
				aux[i], aux[j] = aux[j], aux[i]
				if tabu[hashStr(listToString(aux),1000)] == -1:
					aux_score = getScore(aux,edges)
					if aux_score < best_score:
						best_score = aux_score
						best = list(aux)

				aux[i], aux[j] = aux[j], aux[i]
		return best

	if fixedOrigin:
		i = 0
		for placeA in aux[1:]:
			i=i+1
			j=0
			for placeB in aux[1:]:
				j=j+1
				if(placeA==placeB):
					break
				aux[i], aux[j] = aux[j], aux[i]
				if tabu[hashStr(listToString(aux),1000)] == -1:
					aux_score = getScore(aux,edges)				
					if aux_score < best_score:
						best_score = aux_score
						best = list(aux)
				aux[i], aux[j] = aux[j], aux[i]
		return best

	if fixedEnd:
		i=-1
		for placeA in aux[:-1]:
			i=i+1
			j=-1
			for placeB in aux[:-1]:
				j=j+1
				if(placeA==placeB):
					break
				aux[i], aux[j] = aux[j], aux[i]
				if tabu[hashStr(listToString(aux),1000)] == -1:
					aux_score = getScore(aux,edges)
					if aux_score < best_score:
						best_score = aux_score
						best = list(aux)
				
				aux[i], aux[j] = aux[j], aux[i]		

		return best


	i=-1
	for placeA in aux:
			i=i+1
			j=-1
			for placeB in aux:
				j=j+1
				if(placeA==placeB):
					break
				aux[i], aux[j] = aux[j], aux[i]
				if tabu[hashStr(listToString(aux),1000)] == -1:
					aux_score = getScore(aux,edges)
					if aux_score < best_score:
						best_score = aux_score
						best = list(aux)
				aux[i], aux[j] = aux[j], aux[i]	
	return best


# ------------------- END OF DEFINITIONS ----------------



# ---------------------- START OF MAIN ---------------------------

globals()

if len(sys.argv)==1:
	returnHome=False
else:
	if("--return-home" in sys.argv or "-r" in sys.argv):
		returnHome=True
	if("--fixed-origin" in sys.argv or "-fo" in sys.argv):
		fixedOrigin=True
	if("--fixed-end" in sys.argv or "-fe" in sys.argv):
		fixedEnd=True
	if("--help" in sys.argv or "-h" in sys.argv):
		print("Syntax: python maps.py [OPTIONS]")
		print("Options:")
		print("-h (or --help) -> imprime este menu")
		print("-r (or --return-home)")
		print("-fo (or --fixed-origin)")
		print("-fe (or --fixed-end)")
		raise SystemExit


print("Introduza os locais que quer visitar, separados por vírgula+espaço.")

if(fixedEnd and returnHome):
	print("Escolheu as opções fixedEnd e returnHome em simultâneo, o que não é viável. Neste caso, damos prioridade à opção returnHome.")
	fixedEnd = False


if(fixedOrigin):
	print("Escolheu a opção fixedOrigin, o que significa que o caminho calculado terá como ponto de partida a primeira cidade que introduzir.")
else:
	print("Não escolheu a opção fixedOrigin, o que signfica que o caminho calculado poderá ter como ponto de partida qualquer uma das cidades da lista.")

if(fixedEnd):
	print("Escolheu a opção fixedEnd, o que significa que o caminho calculado terá como ponto de chegada a última cidade que introduzir.")
else:
	print("Não escolheu a opção fixedEnd, o que significa que o caminho calculado poderá ter como ponto de chegada qualquer uma das cidades da lista.")


if(returnHome):
	print("Escolheu a opção returnHome, o que significa que o caminho calculado terá em conta que que quer voltar ao sítio onde começar a viagem.")








places = input().split(", ")

#load known edges
known_edges = [-1 for x in range(0,200000)]

with open('edges.map','r') as f:
	lines = f.readlines()
	for line in lines:
		known_edges[hashStr(line.split(' : ')[0], 200000)] = int(line.split(' : ')[1])
f.closed


#compute all the edges (distance of suggested route between placeA and placeB)
edges = collections.defaultdict(dict)
l=0
dist = 0

# numero de pares de cidades = n! / ((n - m)! * m!), com m =2

comb = math.factorial(len(places)) / (math.factorial(len(places)-2) * 2)

with open('edges.map','a') as f:
	for placeA in places:
		for placeB in places:
			if(placeA==placeB):
				break
			l=l+1

			if(known_edges[hashStr(placeA+" "+placeB, 200000)] != -1):
				dist = known_edges[hashStr(placeA+" "+placeB, 200000)]
			else:
				if(known_edges[hashStr(placeB+" "+placeA, 200000)] != -1):
					dist = known_edges[hashStr(placeB+" "+placeA, 200000)]
				else:
					dist = getDistanceFromAtoB(placeA,placeB)
					f.write(placeA+" "+placeB+" : "+str(dist)+"\n")

			edges[placeA][placeB] = dist
			edges[placeB][placeA] = dist
			sys.stdout.write('\rCalculando arestas: %f %%' % (l//comb * 
100))
			sys.stdout.flush()

f.closed


rr = 0
tabu = [-1 for x in range(0,1000)]

rota_res = randomRestart(places)
rota_i = list(rota_res)
rota_ii = list(rota_res)

while rr < 1000:
	sys.stdout.write('\rCorrendo o Greedy Climb: %f %%' % (rr//10))
	sys.stdout.flush()
	rota_ii = getMaxNeighbour(rota_i,edges)
		
	if(getScore(rota_i,edges)<=getScore(rota_ii,edges)):
		rota_ii = randomRestart(places)
		rr=rr+1
	if(getScore(rota_ii,edges)<getScore(rota_res,edges)):
		rota_res=rota_ii

	tabu[hashStr(listToString(rota_i),1000)] = 1
	rota_i = rota_ii
print('\n\n')
print('Rota final: '+str(rota_res))
print('Distância total: '+str(getScore(rota_res,edges)/1000))

html = ''
html = html + ' <head>\n'
html = html + '   <meta name="viewport" content="initial-scale=1.0, user-scalable=no">\n'
html = html + '   <meta charset="utf-8">\n'
html = html + '   <title>SUPER TRIP</title>\n'
html = html + '   <style>\n'
html = html + '     html, body {\n'
html = html + '       height: 100%;\n'
html = html + '       margin: 0;\n'
html = html + '       padding: 0;\n'
html = html + '     }\n'
html = html + '     #map {\n'
html = html + '       height: 100%;\n'
html = html + '     }\n'
html = html + '   </style>\n'
html = html + ' </head>\n'
html = html + ' <body>\n'
html = html + '   <div id="map"></div>\n'
html = html + '   <script>\n'
html = html + '		  var flightPlanCoordinates = [];\n'
html = html + '       var renderArray = [];\n'
html = html + '	      var requestArray = [];\n'
html = html + '		  var req;\n'
html = html + '		  var map;\n'
html = html + '		  var directionsService;\n'

html = html + '		function generateRequests() {\n'
while len(rota_res)>1:
	aux=list(rota_res[:2])
	html = html + '					requestArray.push({\n'
	html = html + '							origin: \''+aux[0]+'\',\n'
	html = html + '							destination: \''+aux[-1]+'\',\n'
	html = html + '							travelMode: google.maps.TravelMode.DRIVING\n'
	html = html + '					});\n'					
	rota_res = list(rota_res[1:])
html = html + '				processRequests();'
html = html + '		}\n'
html = html + '		function processRequests(){\n'
html = html + '				var i = 0;\n'
html = html + '   			function submitRequest(){\n'
html = html + '          		directionsService.route(requestArray[i], directionResults);\n'
html = html + '   			}\n'
html = html + '   	  		function directionResults(result, status) {\n'
html = html + '					var geocoder = new google.maps.Geocoder();\n'
html = html + '         		if (status == google.maps.DirectionsStatus.OK) {\n'
html = html + '               		renderArray[i] = new google.maps.DirectionsRenderer();\n'
html = html + '               		renderArray[i].setMap(map);\n'
html = html + '               		renderArray[i].setOptions({\n'
html = html + '                   		preserveViewport: true,\n'
html = html + '                   		suppressInfoWindows: true,\n'
html = html + '                   		polylineOptions: {\n'
html = html + '                       		strokeWeight: 4,\n'
html = html + '                       		strokeOpacity: 0.8,\n'
html = html + '                       		strokeColor: \'red\'\n'
html = html + '                   		},\n'
html = html + '                   		markerOptions:{\n'
html = html + '                       		icon:{\n'
html = html + '                           		path: google.maps.SymbolPath.BACKWARD_OPEN_ARROW,\n'
html = html + '                           		scale: 2,\n'
html = html + '                           		strokeColor: \'blue\'\n'
html = html + '                       		}\n'
html = html + '                   		}\n'
html = html + '               		});\n'
html = html + '               		renderArray[i].setDirections(result);\n'
html = html + '						nextRequest();\n'
html = html + '           		}\n'

html = html + '			 		if(status == google.maps.DirectionsStatus.ZERO_RESULTS){\n'
html = html + ' 					geocoder.geocode( {address:requestArray[i].origin}, geocoderResults1);\n'
html = html + '			 		}\n'
html = html + '       		}\n'
html = html + '	  	  		function geocoderResults1(results,status){\n'
html = html + '						if (status == google.maps.GeocoderStatus.OK) \n'
html = html + '    					{\n'
html = html + '      					flightPlanCoordinates.push(results[0].geometry.location);\n'
html = html + '							new google.maps.Marker({\n'
html = html + '    							position: results[0].geometry.location,\n'
html = html + '    							map: map,\n'
html = html +'								icon:{\n'
html = html + '                         		path: google.maps.SymbolPath.BACKWARD_OPEN_ARROW,\n'
html = html + '                         		scale: 2,\n'
html = html + '                         		strokeColor: \'blue\'\n'
html = html + '                       		}\n'
html = html + '							});\n'
html = html + '						} else {\n'
html = html + '      					alert(\'Geocode was not successful for the following reason: \' + status);\n'
html = html + '   					}\n'
html = html + '						nextGeo();\n'
html = html + '	  	  		}\n'



html = html + ' 			function nextGeo(){\n'
html = html + '					var geocoder2 = new google.maps.Geocoder();\n'
html = html + ' 					geocoder2.geocode( {address:requestArray[i].destination}, geocoderResults2);\n'
html = html + '				}\n'

html = html + '	  	  		function geocoderResults2(results,status){\n'
html = html + '						if (status == google.maps.GeocoderStatus.OK) \n'
html = html + '    					{\n'
html = html + '      					flightPlanCoordinates.push(results[0].geometry.location);\n'
html = html + '							new google.maps.Marker({\n'
html = html + '    							position: results[0].geometry.location,\n'
html = html + '    							map: map,\n'
html = html +'								icon:{\n'
html = html + '                         		path: google.maps.SymbolPath.BACKWARD_OPEN_ARROW,\n'
html = html + '                         		scale: 2,\n'
html = html + '                         		strokeColor: \'blue\'\n'
html = html + '                       		}\n'
html = html + '							});\n'
html = html + '							var flightPath = new google.maps.Polyline({\n'
html = html + '           					path: flightPlanCoordinates,\n'
html = html + '           					geodesic: true,\n'
html = html + '           					strokeColor: \'yellow\',\n'
html = html + '           					strokeOpacity: 1.0,\n'
html = html + '           					strokeWeight: 4\n'
html = html + '         				});\n'
html = html + '							flightPath.setMap(map);\n'
html = html + '							flightPlanCoordinates = [];'
html = html + '							nextRequest();\n'
html = html + '						} else {\n'
html = html + '      					alert(\'Geocode was not successful for the following reason: \' + status);\n'
html = html + '   					}\n'
html = html + '	  	  		}\n'


html = html + '				function nextRequest(){\n'
html = html + '            		i++;\n'
html = html + '            		if(i >= requestArray.length){\n'
html = html + '                		return;'
html = html + '            		}\n'
html = html + '            		submitRequest();\n'
html = html + '        		}\n'
html = html + '        		submitRequest();\n'
html = html + '		}\n'
html = html + '     function initMap() {\n'
html = html + '			directionsService = new google.maps.DirectionsService();\n'
html = html + '			map = new google.maps.Map(document.getElementById(\'map\'), {\n'
html = html + '          	zoom: 2,\n'
gmaps = googlemaps.Client(key='AIzaSyBDRaVrNOA74dFlno67A_pEMKNQHA5bPvk')
html = html + '           	center: '+str(gmaps.geocode(rota_res[0])[0]['geometry']['location'])+'\n'
html = html + '         });\n'
html = html + '			generateRequests();\n'
html = html + '		}\n'
html = html + '   </script>\n'
html = html + '   <script async defer\n'
html = html + '       src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBdJo19l4Np9c_H-JtYN-PeB9o37ZKfrT8&signed_in=true&callback=initMap"></script>\n'
html = html + ' </body>\n'
html = html + '</html>'

filename=input('Nome para o ficheiro de output: ')
filename=filename+'.html'
with open(filename, 'w') as f:
	f.write(html)
f.closed
