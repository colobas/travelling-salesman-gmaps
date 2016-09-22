import googlemaps
import requests
import collections
import json
from datetime import datetime
import time
import random
import sys
import math

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
		shuffled = list(shuffled[1:]) # if origin is fixed, the first element isn't shuffled
	if(fixedEnd):
	 	shuffled = list(shuffled[:-1]) # if destination is fixed, the last element isn't shuffled

	random.shuffle(shuffled)
    
	if(fixedOrigin):
		shuffled.insert(0,items[0]) # fixed origin -> add starting point on top
	if(fixedEnd):
		shuffled.append(items[-1]) # fixed destination -> add destination point on bottom

	if(returnHome):
		shuffled.append(shuffled[0]) # if returning home, add the first element to the bottom of the list

	return shuffled

def rad(x):
	return x * math.pi/180

def getDistanceFromAtoB(placeA,placeB):
	url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins='+placeA.replace(' ','+')+'&destinations='+placeB.replace(' ','+')+'&departure_time='+str(int(time.mktime(datetime.now().timetuple())))+'&mode=driving&traffic_model=best_guess&key=AIzaSyBDRaVrNOA74dFlno67A_pEMKNQHA5bPvk'
	r = requests.get(url)
	x = json.loads(r.text)['rows'][0]['elements']
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
				if listToString(aux) in tabu:
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
				if listToString(aux) in tabu:
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
				if listToString(aux) in tabu:
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
				if listToString(aux) in tabu:
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
		print("-h (or --help) -> print this menu")
		print("-r (or --return-home)")
		print("-fo (or --fixed-origin)")
		print("-fe (or --fixed-end)")
		raise SystemExit


print("Type the places you want to visit, separated by comma+blankspace:")

if(fixedEnd and returnHome):
	print("You picked fixedEnd and returnHome, which isn't feasible. In this case, returnHome will have priority.")
	fixedEnd = False


if(fixedOrigin):
	print("You picked fixedOrigin, which means that the computed path will start on the first place you type.")
else:
	print("You didn't pick fixedOrigin, which means that the computed path might start in any of the places you type.")

if(fixedEnd):
	print("You picked fixedEnd, which means that the computed path will end on the last place you type.")
else:
	print("You didn't pick fixedEnd, which means that the computed path might end in any of the places you type.")


if(returnHome):
	print("You picked returnHome, which means that the computed path will consider that you want to return to the starting point, whichever it may be.")








places = input().split(", ")

#load known edges
known_edges = dict()

with open('edges.map','r') as f:
	lines = f.readlines()
	for line in lines:
		known_edges[line.split(' : ')[0]] = int(line.split(' : ')[1])
f.closed


#compute all the edges (distance of suggested route between placeA and placeB)
edges = collections.defaultdict(dict)

dist = 0

with open('edges.map','a') as f:
	for placeA in places:
		for placeB in places:
			if(placeA==placeB):
				break

			if listToString([placeA, placeB]) in known_edges:
				dist = known_edges[listToString([placeA, placeB])]
			else:
				if listToString([placeB, placeA]) in known_edges:
					dist = known_edges[listToString([placeB, placeA])]
				else:
					dist = getDistanceFromAtoB(placeA,placeB)
					f.write("{0} {1} : {2}\n".format(placeA, placeB, dist))

			edges[placeA][placeB] = dist
			edges[placeB][placeA] = dist
			sys.stdout.flush()

f.closed


rr = 0
tabu = dict()

rota_res = randomRestart(places)
rota_i = list(rota_res)
rota_ii = list(rota_res)

while rr < 1000:
	sys.stdout.write('\rRunning Greedy Hill-Climb: %f %%' % (rr//10))
	sys.stdout.flush()
	rota_ii = getMaxNeighbour(rota_i,edges)
		
	if(getScore(rota_i,edges)<=getScore(rota_ii,edges)):
		rota_ii = randomRestart(places)
		rr=rr+1
	if(getScore(rota_ii,edges)<getScore(rota_res,edges)):
		rota_res=rota_ii

	tabu[listToString(rota_i)] = 1
	rota_i = rota_ii
print('\n\n')
print('Final path: {0}'.format(rota_res))
print('Total distance: {0}'.format(getScore(rota_res,edges)/1000))

gmaps = googlemaps.Client(key='AIzaSyBDRaVrNOA74dFlno67A_pEMKNQHA5bPvk')

html = """
<html>

<head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <style>
        html,
        body {
            height: 100%;
            margin: 0;
            padding: 0;
        }
        
        #map {
            height: 100%;
        }
    </style>
</head>

<body>
    <div id="map"></div>
    <script>
        var flightPlanCoordinates = [];
        var renderArray = [];
        var requestArray = [];
        var req;
        var map;
        var directionsService;

        function generateRequests() {
"""
while len(rota_res) > 1:
	aux=list(rota_res[:2])
	rota_res = list(rota_res[1:])
	html += """
			requestArray.push({
			    origin: '%s',
			    destination: '%s',
			    travelMode: google.maps.TravelMode.DRIVING
			});				
""" % (aux[0], aux[-1])

html += """				
			processRequests();
		}
		function processRequests(){
			var i = 0;
				function submitRequest(){
      			directionsService.route(requestArray[i], directionResults);
				}
	  			function directionResults(result, status) {
				var geocoder = new google.maps.Geocoder();
     			if (status == google.maps.DirectionsStatus.OK) {
           			renderArray[i] = new google.maps.DirectionsRenderer();
           			renderArray[i].setMap(map);
           			renderArray[i].setOptions({
               			preserveViewport: true,
               			suppressInfoWindows: true,
               			polylineOptions: {
                   			strokeWeight: 4,
                   			strokeOpacity: 0.8,
                   			strokeColor: 'red'
               			},
               			markerOptions:{
                   			icon:{
                       			path: google.maps.SymbolPath.BACKWARD_OPEN_ARROW,
                       			scale: 2,
                       			strokeColor: 'blue'
                   			}
               			}
           			});
           			renderArray[i].setDirections(result);
						nextRequest();
       			}

		 		if(status == google.maps.DirectionsStatus.ZERO_RESULTS){
						geocoder.geocode( {address:requestArray[i].origin}, geocoderResults1);
		 		}
   			}
  	  		function geocoderResults1(results,status){
					if (status == google.maps.GeocoderStatus.OK){
  						flightPlanCoordinates.push(results[0].geometry.location);
						new google.maps.Marker({
							position: results[0].geometry.location,
							map: map,
							icon:{
                     			path: google.maps.SymbolPath.BACKWARD_OPEN_ARROW,
                     			scale: 2,
                     			strokeColor: 'blue'
                   			}
						});
					} 
					else{
  						alert('Geocode was not successful for the following reason: ' + status);
						}
					nextGeo();
  	  		}
				function nextGeo(){
				var geocoder2 = new google.maps.Geocoder();
					geocoder2.geocode( {address:requestArray[i].destination}, geocoderResults2);
			}

  	  		function geocoderResults2(results,status){
					if (status == google.maps.GeocoderStatus.OK){
  						flightPlanCoordinates.push(results[0].geometry.location);
						new google.maps.Marker({
							position: results[0].geometry.location,
							map: map,
							icon:{
                     			path: google.maps.SymbolPath.BACKWARD_OPEN_ARROW,
                     			scale: 2,
                     			strokeColor: 'blue'
                   			}
						});
						var flightPath = new google.maps.Polyline({
       						path: flightPlanCoordinates,
       						geodesic: true,
       						strokeColor: 'yellow',
       						strokeOpacity: 1.0,
       						strokeWeight: 4
     					});
						flightPath.setMap(map);
						flightPlanCoordinates = [];
						nextRequest();
					} 
					else {
  						alert('Geocode was not successful for the following reason: ' + status);
						}
  	  		}

			function nextRequest(){
        		i++;
        		if(i >= requestArray.length){
            		return;
        		}
        		submitRequest();
    		}
    		submitRequest();
		}
    	function initMap() {
			directionsService = new google.maps.DirectionsService();
			map = new google.maps.Map(document.getElementById('map'), {
          		zoom: 2,
           		center: 
"""
html += str(gmaps.geocode(rota_res[0])[0]['geometry']['location'])
html += """
         	});
			generateRequests();
		}
   </script>
   <script async defer
       src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBdJo19l4Np9c_H-JtYN-PeB9o37ZKfrT8&signed_in=true&callback=initMap"></script>
</body>
</html>
"""

filename=input('Output file name: ')
filename=filename+'.html'
with open(filename, 'w') as f:
	f.write(html)
f.closed
