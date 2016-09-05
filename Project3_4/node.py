'''
@author David Glover
CS 4013 - Compiler Construction
Project 3 and 4 - Type and Scope Checking and
                  Memory Address Computations
January 15, 2015
'''

class Node():
	def __init__(self, c, n, t):
		self.color = c
		self.name = n
		self.type = t
		self.children = []
		self.blue_nodes = []

	def __eq__(self, other):
		return self.color == other.color and self.name == other.name and self.type == other.type

class Node_Tree():
	def __init__(self):
		self.root = None

	def insert_node(self, new_node, green_node_stack):
		if len(green_node_stack) == 0:
			self.root = new_node
		else:
			node = self.search(green_node_stack)
			node.children.append(new_node)

	def search(self, green_node_stack):
		target_node = green_node_stack[0]
		curr_node = green_node_stack[len(green_node_stack) - 1]
		if len(green_node_stack) == 1 and curr_node == target_node:
			return curr_node
		else:
			for child in curr_node.children:
				node = self.search(green_node_stack[:len(green_node_stack) - 1])
				if node == child:
					return node
			return node