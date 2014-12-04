import sys, traceback
import WFConstants
from WFExceptions import DuplicateNodeError, DuplicateParamError
# Classes

class Arrow:

    def __init__(self, type = "0", delta_x = "0", delta_y = "0"):
        self.type = type
        self.delta_x = delta_x
        self.delta_y = delta_y
        
class Parameter:
    
    def __init__(self, name, value, is_mandatory = False):
        self.name = name
        self.setValue(value)
        self.is_mandatory = is_mandatory
        
    def setValue(self, value):
    	if "constant:" in value:
    		self.value = value.split(":")[1]
    		self.is_constant = True
    		self.without_prefix = False
    	elif "variable:" in value:
    		self.value = value.split(":")[1]
    		self.is_constant = False
    		self.without_prefix = False
    	else:
    		self.value = value
    		self.is_constant = False
    		self.without_prefix = True

    def __repr__(self):
    	return self.name + " : " + self.value + ", "

    def __str__(self):
        return self.name + " : " + self.value + ", "
        

class Parameters:
    
    def __init__(self, param_dict):
    	self.parameters = []
    	for key in param_dict.keys():
   			parameter = Parameter(key, param_dict[key])
   			self.addParameter(parameter)
        self.index = len(self.parameters)

    def contains(self, param_name):
        return self.getValue(param_name) != None

    def getValue(self, param_name):
    		for parameter in self.parameters:
    			if parameter.name == param_name:
    				return parameter.value
    		return None

    def insertUpdateValue(self, param_name, param_value):
    	if self.contains(param_name):
    		for parameter in self.parameters:
    			if parameter.name == param_name:
    				parameter.setValue(param_value)
    	else:
    		parameter = Parameter(param_name, param_value)
    		self.addParameter(parameter)

    def addParameter(self, parameter):
    	self.tracebackWrapper(lambda: self.addParameterExcept(parameter))

    def addParameterExcept(self, parameter):
    	if self.contains(parameter.name):
            raise DuplicateParamError(parameter.name, self.parameters)
        else:
    		self.parameters.append(parameter)


    def tracebackWrapper(self, method_name):
        try:
            method_name()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=200, file=sys.stdout)

    def __repr__(self):
    	string_to_return = ""
    	for param in self.parameters:
    		string_to_return = string_to_return + repr(param)
    	return string_to_return

    def __str__(self):
    	string_to_return = "{ "
    	for param in self.parameters:
    		string_to_return = string_to_return + str(param)
    	string_to_return = string_to_return + " }"
    	return string_to_return

    def __iter__(self):
        return self
    
    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.parameters[self.index]

class Node:

    def __init__(self, name = "", class_name = "", parameters = [],
    x = "", y = "", width = "", height = ""):
        self.name = name
        self.class_name = class_name
        self.parameters = parameters
        self.x = x
        self.y = y
        self.width = width
        self.height = height
 
class ProcessNode(Node):

    def __init__(self, name = "", class_name = "", parameters = [],
    next_node = "", x = "", y = "", width = "100", height = "48", arrow = Arrow()):
        Node.__init__(self, name = name, class_name = class_name, parameters = parameters,
        x = x, y = y, width = width, height = height)
        self.arrow = arrow
        self.next_node = next_node
        
    def __str__(self):
        return "Node " + self.name + ". Class " + self.class_name + ". Parameters: " + self.parameters.__str__()
        
class RuleNode(Node):

    def __init__(self, name = "", class_name = "", parameters = [],
    next_node_true = "", next_node_false = "", x = "", y = "", width = "100", height = "24",
    arrow_true = Arrow(), arrow_false = Arrow()):
        Node.__init__(self, name = name, class_name = class_name, parameters = parameters,
        x = x, y = y, width = width, height = height)
        self.arrow_true = arrow_true
        self.arrow_false = arrow_false
        self.next_node_true = next_node_true
        self.next_node_false = next_node_false
          
class NodeGroup():

    def __init__(self):
        self.node_list = []

    def contains(self, node_name):
        return self.getNode(node_name) != None
        
    def  getNode(self, node_name):
        for actual_node in self.node_list:
            if actual_node.name == node_name:
                return actual_node
        return None
                
    def removeNode(self, node_name):
        self.node_list = [actual_node for actual_node in self.node_list if actual_node.name == node_name]
                
    def addNode(self, node):
        self.node_list.append(node)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        