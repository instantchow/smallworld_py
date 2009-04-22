#!/usr/bin/env python
#
#       smallworld.py
#       
#       Copyright 2009 christopher chow <chow@mail.usf.edu>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import networkx as nx
import random as rand
#import matplotlib.pyplot as plt



def kleinberg_grid(n, p=1, q=0, r=0,seed=1):
	"""
	Returns a square 2d DiGraph of size n*n
	
	Parameters as folows:
	- n : size of the grid with sides n*n
	- p : number of local contacts each node will have
	- q : number of long range contacts created for each node
	- r : clustering factor
	- seed : seed value for the random method
	
	"""
	
	#starts with a undirected graph
	G = nx.empty_graph()
	G.name="kleinberg_grid n=%s p=%s q=%s r=%s seed=%s"%(n,p,q,r,seed)
	
	#make all the nodes
	G.add_nodes_from( (i,j) for i in xrange(n) for j in xrange(n) )
	
	#add local edges
	for (i,j) in G.nodes():
		for k in xrange(i-p,i+p+1):
			for l in xrange(j-p, j+p+1):
				#seach within a square of size p to find lattice dist<p
				if (k >= 0 and k < n and l >= 0 and l < n):
					if( ( abs(i-k)+abs(j-l) )<=p):
						if (i,j) != (k,l):
							G.add_edge( (i,j), (k,l) )
							
	#add long distance links (oh directed!)
	G=G.to_directed()
	#also for each node, q is how many extra links per node
	#r is the distribution
	
	if q > 0:
		make_long_range(G,q,r)
						
	return G

def kb_trav(G, u, v):
	#take DiGraph G, nodes u,v - traverse edges and count number
	#of edges to v, calc distance of each in adjacency list
	#pick smallest dist value
	#is found, when dist is 0
	#use.neighbors(node) to search best route
	count = 0
	closest_node_dist = -1 
	closest_node = (0,0) 

	while u != v:
		#print u, v, G.number_of_nodes()
		#print G.nodes()
		count += 1
		for n in G.neighbors(u):
				
			if closest_node_dist > dist(v[0],v[1],n[0],n[1]) or closest_node_dist == -1:
				#set new closest node to n and dist to this new dist
				closest_node = n
				closest_node_dist = dist(v[0],v[1],n[0],n[1])	
			#after all iterations of the neighbors, move u to the closest
		u = closest_node
		#print "next move to node: " + str(u) + " with neighbors " +str(G.neighbors(u))
		closest_node_dist = -1 #reset
	#loop
	
	return count

def make_long_range(G, q, r):
	import random 
	"""
	input a digraph G and returns a new digraph G with long range
	contacts added based on parameters q and r, assume they are > 0
	
	for each node, add edges while q-- is > 1, then one more if q>rand
	each edge has prob based on number of dist d nodes surrounding it
	calc the range of probs at d1-dn, pick a node at d chosen uniformly
	
	"""
	if q == 0: return G
		#nothing to do
		
	if r == 0:
		q_whole = int(q)
		q_fract = q-q_whole
		
		for (i, j) in G.nodes(): #each node
			for x in xrange(q_whole):
				G.add_edge((i,j), random.choice(G.nodes()))
			if q_fract > random.random():
				G.add_edge((i,j), random.choice(G.nodes()))
				
	return G
				
			
	
	distance_counts = []
	normalizing_cof = 0.0
	prob = 0.0
	
	
	node_list = G.nodes()
	for (i, j) in node_list: #each node
		distance_list = [] #clear the distances list
		
		for d in xrange(1,len(G)): ##will definatly end sooner, itterate all possible distances for u,v
			distance_list.append( len(nodes_at_dist(G, i, j, d)) )
			if distance_list[-1] == 0 : ## theres no more at possible nodes at any d > i
				break
			distance_list.pop() #get rid of the last 0
			
		#sum up all the d^-r for the denominator of this thang
		for n in xrange(len(distance_list)):
			normalizing_co += pow(distance_list[n],-r)*distance_list[n]
		
		for (k,l) in node_list: #make a list of dist to all other nodes
			distance_list.append(dist(i,j,k,l))
			
		distance_list.remove(0)	#get rid of the self dist
		#distance_list.sort()	#sort the list, need the max
		#max_dist = distance_list[-1]
		max_dist = max(distance_list)
		
		for n in xrange(max_dist): #max distance for this u,v		
			distance_counts.append(0) #create an index of all distances
		for d in distance_list:
			distance_counts[d] += 1 # increment indicies
				
		
def dist(i,j,k,l):
	return (abs(i-k)+abs(j-l))
	
def nodes_at_dist(G, i,j, d):
	"""
	input a graph, i,j and lattice distance d
	returns all nodes at the distance d in a list
	4*d nodes will be returned, 
	
	"""
	if d == 0:
		print "nana"
		return []
	
	List = []
	row_cursor = d
			
	while row_cursor > 1:
		row_cursor -= 1
		#check/add nodes rowcur-1 to 0
		if (i + row_cursor, j+(d-row_cursor)) in G.nodes(): #starboard fore
			List.append((i + row_cursor, j+(d-row_cursor)))
		if (i + row_cursor, j-(d-row_cursor)) in G.nodes(): #port fore
			List.append((i + row_cursor, j-(d-row_cursor)))
		if (i - row_cursor, j+(d-row_cursor)) in G.nodes(): #port aft
			List.append((i - row_cursor, j+(d-row_cursor)))
		if (i - row_cursor, j-(d-row_cursor)) in G.nodes(): #port aft
			List.append((i - row_cursor, j-(d-row_cursor)))
			#interesting, int underflowed and caused negative nums! add more parenthesis!
	
	#check the 4 corners around d
	if (i + d, j) in G.nodes(): #top
		List.append((i + d, j))
	if (i - d, j) in G.nodes(): #bottom
		List.append((i - d, j))
	if (i , j+d ) in G.nodes(): #right
		List.append((i , j+d ))
	if (i , j-d ) in G.nodes(): #left
		List.append((i , j-d))
	
	
	return List

def test():
	q=0.0
	for p in xrange(1,5):
		while q <= 5.0:
			g=kleinberg_grid(100,p,q)
			print "g created"
			s = 0.0
			for n in xrange(10000):
				u = rand.choice(g.nodes())
				v = rand.choice(g.nodes())

				while u == v:
					print "rechoise"
					v = rand.choice(g.nodes())
				s += kb_trav(g,u,v)
				
			print "run with 10,000 choices, n=100, p=" + str(p)+ " q=" + str(q) +" Avg edges=" +str(s/10000.0)
			q+=0.2
			
#other functions to write
#average degree of all nodes
#traverse n pairs and return list, or stats, hi lo, avg
#need to parameratize r for the script, and to verify data
	
if __name__ == '__main__': 
	import sys
	import random as rand
	#kleinberg_grid(int(sys.argv[1]), sys.argv[1] )
	test()


