
import WFConstants

# Classes

class Arrow:

    def __init__(self, type = "0", delta_x = "0", delta_y = "0"):
        self.type = type
        self.delta_x = delta_x
        self.delta_y = delta_y
        
class Parameter:
    
    def __init__(self, name, value, is_value_constant, without_prefix, is_mandatory):
        self.name = name
        self.value = value
        self.is_constant = is_value_constant
        self.without_prefix = without_prefix
        self.is_mandatory = is_mandatory
        
    def __str__(self):
        return self.name + ": " + self.value + "; "
        

class Parameters():
    
    def __init__(self):
        self.parameters = []
        self.index = len(self.parameters)
        
    def __iter__(self):
        return self
    
    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.parameters[self.index]
    
    

class LogParameters(Parameters):
    
    def __init__(self, message = "", log_level = "DEBUG"):
        self.parameters = [Parameter("component_name", "WORKFLOW_NAME", False, False, True),
        Parameter("log_level", log_level, True, False, True),
        Parameter("log_manager", "log_manager", False, False, True),
        Parameter("log_message", WFConstants.LOG_MESSAGE_BEGINING + message, False, True, True),
        Parameter("param0", "transaction_id", False, False, True),
        Parameter("param1", "JOB_ID", False, False, True),
        Parameter("param2", "transaction_initiator", False, False, True),
        ]
        self.index = len(self.parameters)
        
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
    next_node = "", x = "", y = "", width = "", height = "48", arrow = Arrow()):
        Node.__init__(self, name = name, class_name = class_name, parameters = parameters,
        x = x, y = y, width = width, height = height)
        self.arrow = arrow
        self.next_node = next_node
        
    def __str__(self):
        return "Node " + self.name + ". Class " + self.class_name + ". Parameters: " + self.parameters.__str__()
        
class RuleNode(Node):

    def __init__(self, name = "", class_name = "", parameters = [],
    next_node_true = "", next_node_false = "", x = "", y = "", width = "", height = "24",
    arrow_true = Arrow(), arrow_false = Arrow()):
        Node.__init__(self, name = name, class_name = class_name, parameters = parameters,
        x = x, y = y, width = width, height = height)
        self.arrow_true = arrow_true
        self.arrow_false = arrow_false
        self.next_node_true = next_node_true
        self.next_node_false = next_node_false
        
class LogNode(ProcessNode):
    
    def __init__(self, name = "",  parameters = LogParameters(),
    next_node = "", x = "", y = "", width = "10", height = "48", arrow = Arrow()):
        ProcessNode.__init__(self, name = name, class_name = WFConstants.CLASS_NAME_LOG,
        parameters = parameters, next_node = next_node, x = x, y = y, width = width, height = height)
        
    def __str__(self):
        #to_print = [parameter in self.parameters.parameters if parameter.name == "log_message"]
        return "Log: " #+ to_print[0]
        
class JsonSetterNode(ProcessNode):

    def __init__(self, name = "",  parameters = [Parameter("output_json", "", False, False, True) ],
    next_node = "", x = "", y = "", width = "10", height = "48", arrow = Arrow()):
        ProcessNode.__init__(self, name = name, class_name = WFConstants.CLASS_NAME_JSON_SETTER,
        parameters = parameters, next_node = next_node, x = x, y = y, width = width, height = height)    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        