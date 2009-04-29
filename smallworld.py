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
import matplotlib.pyplot as plt



def kleinberg_grid(n, p=1, q=0, r=0,seed=1):
	"""
	Returns a square 2d DiGraph of size n*n
	
	Parameters as folows:
	- n : size of the grid with sides n*n (int)
	- p : number of local contacts each node will have (int)
	- q : number of long range contacts created for each node (float)
	- r : clustering factor (float)
	- seed : seed value for the random method
	
	"""
	
	#starts with a undirected graph
	G = nx.empty_graph()
	#name does not carry over after to_directed() call...
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
							
	#add long distance links
	#convert to a digraph, links will be doubled
	G=G.to_directed()
	
	#no need run longrange algo unless q>0
	if q > 0:
		G=make_long_range(G,q,r)
						
	return G

def kb_trav(G, u, v):
	"""
	input:
		DiGraph G
		Nodes u,v | in the form of a tuple (i,j)
	output:
		traversed edges as int
	algorithm: greedy local information search
		start at u
		calc distance of each in adjacency list of u
		pick smallest dist value
		is found, when dist is 0
		uses neighbors(node) method
	"""
	
	count = 0
	closest_node_dist = -1 
	closest_node = (0,0) 

	while u != v:
		#print u, v, G.number_of_nodes()
		#print G.nodes()
		count += 1
		for n in G.neighbors(u):
				
			if closest_node_dist > dist(v,n) or closest_node_dist == -1:
				#set new closest node to n and dist to this new dist
				closest_node = n
				closest_node_dist = dist(v,n)	
			#after all iterations of the neighbors, move u to the closest
		u = closest_node
		#print "next move to node: " + str(u) + " with neighbors " +str(G.neighbors(u))
		closest_node_dist = -1 #reset
	#loop
	
	return count

def make_long_range(G, q, r):
	import random 
	"""
	input:
		a digraph G and returns a new digraph G with long range
		contacts added based on parameters q and r, assume they are > 0
	note:
		for each node, add edges while q-- is > 1, then one more with pr[q]
		each edge has prob based d[u,v]^-r
		calcs this for each node for each originating node (n^2 operation)
		puts all the d[u,v]^r in a large array, in the form of
		[0,d1,d2+d1...dn+dn-1] and uniformly choose a float in the whole range
	"""
	if q == 0: return G
		#nothing to do
		
	q_whole = int(q)
	q_fract = q-q_whole
	
		
	if r == 0:
		#return a uniform distrubition of long range links
		
		
		for (i, j) in G.nodes(): #each node
			for x in xrange(q_whole):
				G.add_edge((i,j), random.choice(G.nodes()))
			if q_fract > random.random():
				G.add_edge((i,j), random.choice(G.nodes()))
				
		return G
	
	#everything else which q,r > 0
		
	#for each node n, for each other node m, n!=m calc the prob d(u,v)^-r
	#increment the running sum, and update the dict with the node=sum
	#when finished, select a rand[0,running_sum] and find dict entry which
	#is the first one to have a value greater than rand
	

	for u in G.nodes():
		running_sum = 0.0		#clear out the lists! for each u
		prob_node_list = []
		coef_sum = 1.0
		teh_rand = 0.0	
		"""
		for v in G.nodes():
			if u!=v:
				coef_sum += pow(dist(u,v),-r)
		"""
		for v in G.nodes():
			if u!=v:
				#print "heres the running sum" + str(running_sum)
				
				running_sum += pow(dist(u,v),-r) / coef_sum
				prob_node_list.append( (running_sum,v) )
		
		#choose the_one
		#choose q times
		if q_fract > random.random(): q_whole +=1
		for x in xrange(q_whole):
			teh_rand = random.uniform(0,running_sum)
			
			for e in prob_node_list:
				if e[0] > teh_rand:
				#if e[0] > random.uniform(0,running_sum): AH HA!!!!
					the_one = e[1]
					break
			G.add_edge(u, the_one )	
			#print "distance to the_one" + str(dist(u,the_one))
		#repeat if q>1			
	
	
	return G
				
		
def dist(i,j,k,l):
	return (abs(i-k)+abs(j-l))
	
def dist(u,v):
	return (abs(u[0]-v[0])+abs(u[1]-v[1]))

	
def nodes_at_dist(G, i,j, d):
	"""
	input a graph, i,j and lattice distance d
	returns all nodes at the distance d in a list
	4*d nodes will be returned as a List
	
	may be deleted, not used
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

def test(arg_n, arg_p, arg_q, arg_r, step):
	#example run test(100, 1, 15, 0.2)
	n=int(arg_n)
	p=arg_p
	q=arg_q
	r=arg_r*step
	G=kleinberg_grid(n,p,q,r)
	s = 0.0
	for x in xrange(n*10):
		u = rand.choice(G.nodes())
		v = rand.choice(G.nodes())
		while u == v:
			#pint "oops, u==v"
			v = rand.choice(G.nodes())
		s += kb_trav(G,u,v)
		
	print "n"+ " \t" + "p" + "\t" + "q" + "\t" + "r" + "\t" + "Avg Path Len"
	print str(n) + "\t" + str(p)+ "\t" + str(q) + "\t" + str(r)+ "\t" + str(s/(n*10.0))
	
    

	
def grid_layout(G):
	"""
	helper method for show_me() 
	
	builds a position dict for the positioning of nodes on a grid
	eg, node 0,0 is at 0,0 and n,m is at n,m!
	put them in their place!!
	niceeeee
	
	Also added a stager to the nodes to better visualize edges that are 
	across the same row or column, less edge overlap
	
	"""
	import Numeric as N
	pos={}
	for v in G.nodes():
		pos[v]=N.array([v[0]+v[1]%2*0.25,v[1]+v[0]%2*0.25])

	#nx.draw(G, pos)
	#plt.savefig("kleinberg10-2-0.png")
	return pos
def show_me(G):
	"""
	draws the nodes in a grid layout
	
	"""
	
	pos = grid_layout(G)
	nx.draw(G, pos, node_size=78, labels=None)
	plt.show()
	
	
if __name__ == '__main__': 
	import sys
	#kleinberg_grid(int(sys.argv[1]), sys.argv[1] )
	test(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))


