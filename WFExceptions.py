import sys, traceback

class DuplicateNodeError(Exception):

	def __init__(self, node_name):
		self.node_name = node_name
	
	def __str__(self):
		return "Node named " + "'" + self.node_name +\
		"'" + " already in WF"

class DuplicateParamError(Exception):

	def __init__(self, param_name, params):
		self.param_name = param_name
		self.params = params
	
	def __str__(self):
		return "Parameter " + "'" + self.param_name +\
		"'" + " already exists in " + repr(self.params)
        
class UnexistingNodeError(Exception):

	def __init__(self, node, node_group):
		self.node = node
        self.node_group = node_group
	
	def __str__(self):
		return "Node " + "'" + self.node.name +\
		"'" + " not found in  " + self.node_group