import urllib.request 
import json
from math import radians, cos, sin, asin, sqrt
import heapq


# quadtree.py
# Implements a Node and QuadTree class that can be used as 
# base classes for more sophisticated implementations.
# Malcolm Kesson Dec 19 2012
class Node:
	ROOT = 0
	BRANCH = 1
	LEAF = 2
	minsize = 1   # Set by QuadTree
	isFilled = False;
	#_______________________________________________________
	# In the case of a root node "parent" will be None. The
	# "rect" lists the minx,minz,maxx,maxz of the rectangle
	# represented by the node.
	def __init__(self, parent, rect, minsize):
		self.minsize = minsize
		self.parent = parent
		self.children = [None,None,None,None]
		if parent == None:
			self.depth = 0
		else:
			self.depth = parent.depth + 1
		self.rect = rect
		x0,z0,x1,z1 = rect
		if self.parent == None:
			self.type = Node.ROOT
		elif (x1 - x0) <= Node.minsize:
			self.type = Node.LEAF
		else:
			self.type = Node.BRANCH
	#_______________________________________________________
	# Recursively subdivides a rectangle. Division occurs 
	# ONLY if the rectangle spans a "feature of interest".
	def subdivide(self):
		if self.type == Node.LEAF:
			return
		x0,z0,x1,z1 = self.rect
		h = (x1 - x0)/2
		rects = []
		rects.append( (x0, z0, x0 + h, z0 + h) )
		rects.append( (x0, z0 + h, x0 + h, z1) )
		rects.append( (x0 + h, z0 + h, x1, z1) )
		rects.append( (x0 + h, z0, x1, z0 + h) )
		for n in range(len(rects)):
			span = self.spans_feature(rects[n])
			if span == True:
				# self.children[n] = self.getinstance(rects[n])
				self.children[n] = Node(self, rects[n], self.minsize)
				self.children[n].subdivide() # << recursion
	#_______________________________________________________
	# A utility proc that returns True if the coordinates of
	# a point are within the bounding box of the node.
	def contains(self, x, z):
		x0,z0,x1,z1 = self.rect
		if x >= x0 and x <= x1 and z >= z0 and z <= z1:
			return True
		return False
	#_______________________________________________________
	# Sub-classes must override these two methods.
	def getinstance(self,rect):
		return Node(self,rect)			
	def spans_feature(self, rect):
		# if rect[2] - rect[0] > 1:
		# 	return True
		return True

#===========================================================			
class QuadTree:
	maxdepth = 1 # the "depth" of the tree
	leaves = []
	allnodes = []
	#_______________________________________________________
	def __init__(self, rootnode, minrect):
		self.root = rootnode
		Node.minsize = minrect
		rootnode.subdivide() # constructs the network of nodes
		self.prune(rootnode)
		self.traverse(rootnode)
	#_______________________________________________________
	# Sets children of 'node' to None if they do not have any
	# LEAF nodes.		
	def prune(self, node):
		if node.type == Node.LEAF:
			return 1
		leafcount = 0
		removals = []
		for child in node.children:
			if child != None:
				leafcount += self.prune(child)
				if leafcount == 0:
					removals.append(child)
		for item in removals:
			n = node.children.index(item)
			node.children[n] = None		
		return leafcount
	#_______________________________________________________
	# Appends all nodes to a "generic" list, but only LEAF 
	# nodes are appended to the list of leaves.
	def traverse(self, node):
		QuadTree.allnodes.append(node)
		if node.type == Node.LEAF:
			QuadTree.leaves.append(node)
			if node.depth > QuadTree.maxdepth:
				QuadTree.maxdepth = node.depth
		for child in node.children:
			if child != None:
				self.traverse(child) # << recursion





class Utils(object):
	
	@staticmethod
	def haversine(lat1, lon1, lat2, lon2):
	    """
	    Calculate the great circle distance between two points 
	    on the earth (specified in decimal degrees)
	    """
	    # convert decimal degrees to radians 
	    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
	    # haversine formula 
	    dlon = lon2 - lon1 
	    dlat = lat2 - lat1 
	    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	    c = 2 * asin(sqrt(a)) 
	    km = 6367 * c
	    return km

	@staticmethod
	def getTopResViaTemp(list):
		top10List = []
		q = []
		
		heapq.heapify(list)

		for _ in range(10):
			top10List.append(heapq.heappop(list))

		return top10List



		

class HotspotManager:

	distributedRegions = []

	def __init__(self):
		pass
		
		
	def getDistributedRegions(self, positionList):
		

		rootrect = [-48, -48, 48, 48]
		reso = 3;
		rootnode = Node(None, rootrect, reso)
		qt = QuadTree(rootnode, reso)

		centralPosX = positionList[0][0]
		centralPosY = positionList[0][1]

		for item in positionList[1:]:
			x = Utils.haversine(centralPosX, centralPosY, item[0], centralPosY)
			y = Utils.haversine(centralPosX, centralPosY, centralPosX, item[1])
			self.checkAndInsert(rootnode, x, y, item[2], item[3])

		return self.distributedRegions;



	def checkAndInsert(self, node, x, y, zipcode, placeName):
		if node.type == Node.LEAF:
			# QuadTree.leaves.append(node)
			if node.depth > QuadTree.maxdepth:
				QuadTree.maxdepth = node.depth
			if node.isFilled == False:
				node.isFilled = True;
				print("\n")
				print("meiyou")

				self.distributedRegions.append((zipcode, placeName))
			else:
				print("youle")

		for child in node.children:
			if (child != None) and (child.contains(x, y)):
				self.checkAndInsert(child, x, y, zipcode, placeName) # << recursion


    	


class HotSpot:

	
	def __init__(self):
		pass

	def getPositions(self, zipcode):
		url = "http://api.geonames.org/findNearbyPostalCodesJSON?postalcode="+ zipcode +"&radius=30&maxRows=500&username=cszongyang"
		response = urllib.request.urlopen(url)
		data = json.loads(response.read().decode("utf8").encode('ascii', 'ignore').decode('ascii'))
		positionList = []
		
		
		for idx, item in enumerate(data['postalCodes']):
			positionList.append([])
			positionList[idx].append(item['lat']);
			positionList[idx].append(item['lng']);
			positionList[idx].append(item['postalCode']);
			positionList[idx].append(item['placeName']);

		return positionList
		


	def getWeatherByZipcode(self, zipcode):
		url = "http://api.openweathermap.org/data/2.5/weather?zip="+ zipcode +",us&APPID=2bc0153f1bd494467c65d52929dcd877"
		response = urllib.request.urlopen(url)
		data = json.loads(response.read().decode("utf8").encode('ascii', 'ignore').decode('ascii'))
		return format(round(data['main']['temp'] - 273.15,2));






def main():

	zipcode = "90007"
	temperatureList = []

	hotSpot = HotSpot()
	manager = HotspotManager()

	# print(hotSpot.getPostalCodes())
	zipcodeList = manager.getDistributedRegions(hotSpot.getPositions(zipcode))

	for item in zipcodeList:
		temp = hotSpot.getWeatherByZipcode(item[0])
		temperatureList.append((float(temp), item[1]))

    

	print(Utils.getTopResViaTemp(temperatureList))





if __name__ == "__main__":
	main()






		