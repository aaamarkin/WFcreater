import sys, traceback
import WFConstants
import WFVariables
import re
from WFExceptions import DuplicateNodeError, DuplicateParamError

# Helper functions

# Classes

class Arrow:
    def __init__(self, type="0", delta_x="0", delta_y="0"):
        self.type = type
        self.delta_x = delta_x
        self.delta_y = delta_y


class Parameter:
    def __init__(self, name, value, is_mandatory=False, type = "String"):
        self.name = name
        self.setValue(value)
        self.type = type
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

class Handler:
    def __init__(self, name="", class_name="",  parameters=Parameters({})):
        self.name = name
        self.class_name = class_name
        self.parameters = parameters

    def __str__(self):
        return "Handler " + self.name

class Node:
    def __init__(self, name="", class_name="", parameters=Parameters({}),
                 x="0", y="0", width="", height="", previous_node_names=[]):
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
    def __init__(self, name="", class_name="", parameters=Parameters({}),
                 next_node="", x="0", y="0", width="100", height="48", arrow=Arrow()):
        Node.__init__(self, name=name, class_name=class_name, parameters=parameters,
                      x=x, y=y, width=width, height=height)
        self.arrow = arrow
        self.next_node = next_node


class RuleNode(Node):
    def __init__(self, name="", class_name="", parameters=Parameters({}),
                 next_node_true="", next_node_false="", x="0", y="0", width="100", height="24",
                 arrow_true=Arrow(), arrow_false=Arrow()):
        Node.__init__(self, name=name, class_name=class_name, parameters=parameters,
                      x=x, y=y, width=width, height=height)
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
        self.node_group_list = [[actual_node for actual_node in actual_group.node_list if actual_node.name == node_name]
                                for actual_group in self.node_group_list]

    def injectNode(self, node, from_node_name=""):
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
            new_x = int(node.x) + x
            node.x = str(new_x)

    def moveY(self, y):
        for node in self.node_list:
            new_y = int(node.y) + y
            node.y = str(new_y)

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

    def makeVertical(self, initial_y=0, step=50):
        for node in self.node_list:
            node.x = "0"
            node.y = str(initial_y)
            initial_y += step

    def makeHorizontal(self, initial_x=0, step=150):
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

    def __init__(self, url):
        NodeGroup.__init__(self)
        self.url = url
        url_copy = url.split('/')
        if len(url_copy) == 2:
            composite = url[0]
            method = url[1]
        elif len(url_copy) == 3:
            composite = url[0]
            service = url[1]
            method = url[2]

        temp_method = method[0].upper() + method[1:]
        method_upper_case_list = re.findall('[A-Z][^A-Z]*', temp_method)
        base_var_name = ''
        for word in method_upper_case_list:
            base_var_name = base_var_name + word.lower() + '_'

        START_LOG = ProcessNode(
            name="LogDebug: " + method,
            parameters=Parameters(WFConstants.LOG_ORDINARY_PARAMS),
            class_name=WFConstants.CLASS_NAME_LOG)

        message = START_LOG.parameters.getValue("log_message")
        message = message + " started rest request " + method
        START_LOG.parameters.insertUpdateValue("log_message", message)

        self.request_json = base_var_name + "request_json"
        self.response_json = base_var_name + "response_json"
        self.request_url = base_var_name + "url"

        CREATE_REQUEST = ProcessNode(
            name="Set " + request_json,
            parameters=Parameters({
                "input_json": "variable:base_request",
                "output_json": "variable:" + self.request_json}),
            class_name=WFConstants.CLASS_NAME_JSON_SETTER)

        MAKE_REQUEST = ProcessNode(
            name="Call " + method,
            parameters=Parameters(WFConstants.MAKE_REST_REQUEST_PARAMS),
            class_name=WFConstants.CLASS_NAME_MAKE_REST_REQUEST)

        MAKE_REQUEST.parameters.insertUpdateValue("request_json", "variable:" + self.request_json)
        MAKE_REQUEST.parameters.insertUpdateValue("response_json", "variable:" + self.response_json)
        MAKE_REQUEST.parameters.insertUpdateValue("request_url", "variable:" + self.request_url)

        SETTING_LOG = ProcessNode(
            name="Log " + method + " params",
            parameters=Parameters({
                "composite_name_log": "%"+self.request_url+"%",
                "request_json_log": "%"+self.request_json+"%",
                "response_json_log": "%"+self.response_json+"%"}),
            class_name=WFConstants.CLASS_NAME_VARIABLE_MAPPER)

        HTTP_CHECK = RuleNode(
            name="http code == 200?",
            parameters=Parameters({
                "op1": "variable:http_code",
                "op2": "constant:200"}),
            class_name=WFConstants.CLASS_NAME_EQUALS)

        GET_RESULT = ProcessNode(
            name="Parse " + self.response_json,
            parameters=Parameters(WFConstants.GET_INFO_FROM_RESPONSE_PARAMS),
            class_name=WFConstants.CLASS_NAME_JSON_GETTER)

        GET_RESULT.parameters.insertUpdateValue("json_document", "variable:" + self.response_json)

        SY_CHECK = RuleNode(
            name="SY code == OK?",
            parameters=Parameters({
                "op1": "variable:sy_error_code",
                "op2": "constant:OK"}),
            class_name=WFConstants.CLASS_NAME_EQUALS)

        RESULT_LOG = ProcessNode(
            name="LogDebug: " + method + " results",
            parameters=Parameters(WFConstants.REST_RESULTS_LOG_PARAMS),
            class_name=WFConstants.CLASS_NAME_LOG)

        SETTING_REST_ERROR = ProcessNode(
            name="Set " + method + " rest error",
            parameters=Parameters({
                "error_code": "HPSA_WF-001",
                "error_message": "rest query error %http_code%;" +\
                                " query params: request: %request_json_log%, url: %composite_name_log%."}),
            class_name=WFConstants.CLASS_NAME_VARIABLE_MAPPER)

        SETTING_SY_ERROR = ProcessNode(
            name="Set " + method + " sy error",
            parameters=Parameters({
                "error_code": "%sy_error_code%",
                "error_message": "%sy_error_message%",
                "error_comment": "query params: request: %request_json_log%, response: %response_json_log%, url: %composite_name_log%."}),
            class_name=WFConstants.CLASS_NAME_VARIABLE_MAPPER)

        REST_ERROR_LOG = ProcessNode(
            name="LogError: " + method + " rest error",
            parameters=Parameters(WFConstants.REST_RESULTS_LOG_PARAMS),
            class_name=WFConstants.CLASS_NAME_LOG)

        message = REST_ERROR_LOG.parameters.getValue("log_message")
        message = message + " rest query error error_code=%s, error_message=%s"
        REST_ERROR_LOG.parameters.insertUpdateValue("log_message", message)
        REST_ERROR_LOG.parameters.insertUpdateValue("param3", "error_code")
        REST_ERROR_LOG.parameters.insertUpdateValue("param4", "error_message")
        REST_ERROR_LOG.parameters.insertUpdateValue("log_level", "constant:ERROR")

        SY_ERROR_LOG = ProcessNode(
            name="LogError: " + method + " sy error",
            parameters=Parameters(WFConstants.REST_RESULTS_LOG_PARAMS),
            class_name=WFConstants.CLASS_NAME_LOG)

        message = SY_ERROR_LOG.parameters.getValue("log_message")
        message = message + " composite error error_code=%s, error_message=%s, comment=%s"
        SY_ERROR_LOG.parameters.insertUpdateValue("log_message", message)
        SY_ERROR_LOG.parameters.insertUpdateValue("param3", "error_code")
        SY_ERROR_LOG.parameters.insertUpdateValue("param4", "error_message")
        SY_ERROR_LOG.parameters.insertUpdateValue("param5", "error_comment")
        SY_ERROR_LOG.parameters.insertUpdateValue("log_level", "constant:ERROR")


        #Setting right node sequence
        START_LOG.next_node = CREATE_REQUEST.name
        CREATE_REQUEST.next_node = MAKE_REQUEST.name
        MAKE_REQUEST.next_node = SETTING_LOG.name
        SETTING_LOG.next_node = HTTP_CHECK.name

        HTTP_CHECK.next_node_false = SETTING_REST_ERROR.name
        SETTING_REST_ERROR.next_node = REST_ERROR_LOG.name

        HTTP_CHECK.next_node_true = GET_RESULT.name
        GET_RESULT.next_node = SY_CHECK.name

        SY_CHECK.next_node_false = SETTING_SY_ERROR.name
        SETTING_SY_ERROR.next_node = SY_ERROR_LOG.name

        SY_CHECK.next_node_true = RESULT_LOG.name

        NodeGroup.injectNode(self, START_LOG)
        NodeGroup.injectNode(self, CREATE_REQUEST)
        NodeGroup.injectNode(self, MAKE_REQUEST)
        NodeGroup.injectNode(self, SETTING_LOG)
        NodeGroup.injectNode(self, HTTP_CHECK)
        NodeGroup.injectNode(self, SETTING_REST_ERROR)
        NodeGroup.injectNode(self, REST_ERROR_LOG)
        NodeGroup.injectNode(self, GET_RESULT)
        NodeGroup.injectNode(self, SY_CHECK)
        NodeGroup.injectNode(self, SETTING_SY_ERROR)
        NodeGroup.injectNode(self, SY_ERROR_LOG)
        NodeGroup.injectNode(self, RESULT_LOG)


class SetInitialParamsGroup(NodeGroup):

    def __init__(self, wf_name):
        NodeGroup.__init__(self)

        AUDIT = ProcessNode(
            name="Audit " + wf_name,
            parameters=Parameters(WFConstants.AUDIT_ORDINARY_PARAMS),
            class_name=WFConstants.CLASS_NAME_AUDIT)

        SET_INITIAL_PARAMS = ProcessNode(
            name=WFVariables.NODE_NAME_SET_INITIAL_PARAM,
            parameters=Parameters(WFConstants.SET_INITIAL_VALUE_PARAMS),
            class_name=WFConstants.CLASS_NAME_VARIABLE_MAPPER)

        LOG_INFO = ProcessNode(
            name="LogInfo: " + wf_name + " started",
            parameters=Parameters(WFConstants.LOG_ORDINARY_PARAMS),
            class_name=WFConstants.CLASS_NAME_LOG)

        LOG_INFO.parameters.insertUpdateValue("log_level","INFORMATIVE")
        message = LOG_INFO.parameters.getValue("log_message")
        message = message + " " + wf_name + " started"
        START_LOG.parameters.insertUpdateValue("log_message", message)

        LOG_DEBUG = ProcessNode(
            name="LogDebug: " + wf_name + " started",
            parameters=Parameters(WFConstants.LOG_ORDINARY_PARAMS),
            class_name=WFConstants.CLASS_NAME_LOG)

        LOG_DEBUG.parameters.insertUpdateValue("log_level","INFORMATIVE")
        message = LOG_DEBUG.parameters.getValue("log_message")
        message = message + " " + wf_name + " started with request json=%s"
        LOG_DEBUG.parameters.insertUpdateValue("log_message", message)
        LOG_DEBUG.parameters.insertUpdateValue("param3","request_json")

        GET_PROPERTIES = ProcessNode(
            name=WFVariables.NODE_NAME_GET_PROPERTIES,
            parameters=Parameters(WFConstants.GET_PROPERTIES_PARAMS),
            class_name=WFConstants.CLASS_NAME_GET_PROPERTY)

        SET_SY_URL = ProcessNode(
            name=WFVariables.NODE_NAME_SET_SY_URL,
            class_name=WFConstants.CLASS_NAME_VARIABLE_MAPPER)

        CREATE_BASE_REQUEST = ProcessNode(
            name="Create base SY request",
            parameters=Parameters(WFConstants.CREATE_BASE_SY_REQUEST_PARAMS),
            class_name=WFConstants.CLASS_NAME_JSON_SETTER)

        #Setting right node sequence
        AUDIT.next_node = SET_INITIAL_PARAMS.name
        SET_INITIAL_PARAMS.next_node = LOG_INFO.name
        LOG_INFO.next_node = LOG_DEBUG.name
        LOG_DEBUG.next_node = GET_PROPERTIES.name
        GET_PROPERTIES.next_node = SET_SY_URL.name
        SET_SY_URL.next_node = CREATE_BASE_REQUEST.name

        NodeGroup.injectNode(self, AUDIT)
        NodeGroup.injectNode(self, SET_INITIAL_PARAMS)
        NodeGroup.injectNode(self, LOG_INFO)
        NodeGroup.injectNode(self, LOG_DEBUG)
        NodeGroup.injectNode(self, GET_PROPERTIES)
        NodeGroup.injectNode(self, SET_SY_URL)