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
    	if self.contains(parameter.name):
            raise DuplicateParamError(parameter.name, self.parameters)
        else:
    		self.parameters.append(parameter)


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
        self.index = len(self.parameters)
        return self
    
    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.parameters[self.index]

class Node:

    def __init__(self, name = "", class_name = "", parameters = [],
    x = "0", y = "0", width = "", height = "", previous_node_names = []):
        self.name = name
        self.class_name = class_name
        self.parameters = parameters
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.previous_node_names = previous_node_names

    def __str__(self):
        return "Node " + self.name + ". Class " + self.class_name + ". Parameters: " + self.parameters.__str__()
 
class ProcessNode(Node):

    def __init__(self, name = "", class_name = "", parameters = [],
    next_node = "", x = "0", y = "0", width = "100", height = "48", arrow = Arrow()):
        Node.__init__(self, name = name, class_name = class_name, parameters = parameters,
        x = x, y = y, width = width, height = height)
        self.arrow = arrow
        self.next_node = next_node
        
    
        
class RuleNode(Node):

    def __init__(self, name = "", class_name = "", parameters = [],
    next_node_true = "", next_node_false = "", x = "0", y = "0", width = "100", height = "24",
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
        self.node_group_list = []
        self.index = len(self.node_list)

    def contains(self, node_name):
        return self.getNode(node_name) != None
        
    def getNode(self, node_name):
        for actual_node in self.node_list:
            if actual_node.name == node_name:
                return actual_node
        for actual_group in self.node_group_list:
            for actual_node in actual_group.node_list:
                if actual_node.name == node_name:
                    return actual_node
        return None
                
    def removeNode(self, node_name):
        self.node_list = [actual_node for actual_node in self.node_list if actual_node.name == node_name]
        self.node_group_list = [[actual_node for actual_node in actual_group.node_list if actual_node.name == node_name] for actual_group in self.node_group_list]
                
    def injectNode(self, node, from_node_name = ""):
        node.previous_node_names.append(from_node_name)
        if len(from_node_name) > 0 and self.contains(from_node_name):
            self.getNode(from_node_name).next_node = node.name
        if not self.contains(node.name):
            self.node_list.append(node)

    def connectProcessNodeToNode(self, from_node_name, to_node_name):
        self.getNode(from_node_name).next_node = to_node_name
        self.getNode(to_node_name).previous_node_names.append(to_node_name)
        
    def moveX(self, x):
        for node in self.node_list:
            node.x = node.x + x
            
    def moveY(self, y):
        for node in self.node_list:
            node.y = node.y + y

    def moveXAll(self, x):
        for node in self.node_list:
            node.x = node.x + x
        for node_group in self.node_group_list:
            node_group.moveX(x)

    def moveYAll(self, y):
        for node in self.node_list:
            node.y = node.y + y
        for node_group in self.node_group_list:
            node_group.moveY(y)
            
    def makeVertical(self, initial_y = 0, step = 50):
        for node in self.node_list:
            node.x = "0"
            node.y = str(initial_y)
            initial_y += step

    def makeHorizontal(self, initial_x = 0, step = 150):
        for node in self.node_list:
            node.y = "0"
            node.x = str(initial_x)
            initial_x += step

    def addGroup(self, node_group):
        contains = False
        for node in node_group:
            if self.contains(node.name):
                contains = True
        if not contains:
            self.node_group_list.append(node_group)

    def __iter__(self):
        self.index = len(self.node_list)
        return self
    
    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.node_list[self.index]


class RestRequestGroup(NodeGroup):
    
    START_LOG = ProcessNode(
        parameters = Parameters(WFConstants.LOG_ORDINARY_PARAMS),
        class_name = WFConstants.CLASS_NAME_LOG))

    CREATE_REQUEST = ProcessNode(
        parameters = Parameters(
            {"input_json":"variable:base_request",
            "output_json":""}),
        class_name = WFConstants.CLASS_NAME_JSON_SETTER)

    MAKE_REQUEST = ProcessNode(
        parameters = Parameters(WFConstants.MAKE_REST_REQUEST_PARAMS),
        class_name = WFConstants.CLASS_NAME_MAKE_REST_REQUEST)

    RESULT_LOG = ProcessNode(
        parameters = Parameters(WFConstants.REST_RESULTS_LOG_PARAMS),
        class_name = WFConstants.CLASS_NAME_LOG))

    SETTING_LOG = ProcessNode(
        parameters = Parameters(WFConstants.SET_LOG_PARAMS),
        class_name = WFConstants.CLASS_NAME_VARIABLE_MAPPER)

    HTTP_CHECK = RuleNode(
        parameters = Parameters(WFConstants.EQUALS_PARAMS),
        class_name = WFConstants.CLASS_NAME_EQUALS)

    GET_RESULT = ProcessNode(
        parameters = Parameters(GET_INFO_FROM_RESPONSE_PARAMS),
        class_name = WFConstants.CLASS_NAME_JSON_GETTER)

    SY_CHECK = RuleNode(
        parameters = Parameters(WFConstants.EQUALS_PARAMS),
        class_name = WFConstants.CLASS_NAME_EQUALS)

    def __init__(self, url):
        NodeGroup.__init__(self)


        
        
        
        
    