import sys, traceback
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.dom.minidom import Document
import WFConstants
import WFVariables
import re
from WFExceptions import DuplicateNodeError, DuplicateParamError

# Helper functions

# Classes

class Arrow:
    def __init__(self, type="0", delta_x="0", delta_y="0", name=""):
        self.type = type
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.name=name


class Parameter:
    def __init__(self, name, value, is_mandatory=False, type="String"):
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
    def __init__(self, name="", class_name="", parameters=Parameters({})):
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

    def positionToXml(self):
        doc = Document()

        xml_position_node = doc.createElement(WFConstants.TAG_NAME_POSITION)

        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(self.name)
        xml_name_node.appendChild(xml_name_node_content)

        xml_x_node = doc.createElement(WFConstants.TAG_NAME_X)
        xml_x_node_content = doc.createTextNode(self.x)
        xml_x_node.appendChild(xml_x_node_content)

        xml_y_node = doc.createElement(WFConstants.TAG_NAME_Y)
        xml_y_node_content = doc.createTextNode(self.y)
        xml_y_node.appendChild(xml_y_node_content)

        xml_width_node = doc.createElement(WFConstants.TAG_NAME_WIDTH)
        xml_width_node_content = doc.createTextNode(self.width)
        xml_width_node.appendChild(xml_width_node_content)

        xml_height_node = doc.createElement(WFConstants.TAG_NAME_HEIGHT)
        xml_height_node_content = doc.createTextNode(self.height)
        xml_height_node.appendChild(xml_height_node_content)

        xml_position_node.appendChild(xml_name_node)
        xml_position_node.appendChild(xml_x_node)
        xml_position_node.appendChild(xml_y_node)
        xml_position_node.appendChild(xml_width_node)
        xml_position_node.appendChild(xml_height_node)

        return xml_position_node

    def __str__(self):
        return "Node " + self.name + ". Class " + self.class_name + ". Parameters: " + self.parameters.__str__()


class ProcessNode(Node):
    def __init__(self, name="", class_name="", parameters=Parameters({}),
                 next_node="", x="0", y="0", width="100", height="48", arrow=Arrow(), **kwargs):

        if 'xml_node' in kwargs:
            xml_node = kwargs.get('xml_node')
            node_name = xml_node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
            node_class_name = xml_node.getElementsByTagName(WFConstants.TAG_NAME_CLASS_NAME)[0].childNodes[0].data
            xml_params = xml_node.getElementsByTagName(WFConstants.TAG_NAME_PARAM)
            param_dict = {}
            for xml_param in xml_params:
                param_dict[xml_param.getAttribute(WFConstants.ATTRIBUTE_NAME_NAME)] = \
                    xml_param.getAttribute(WFConstants.ATTRIBUTE_NAME_VALUE)
            params = Parameters(param_dict)
            node_next_node = xml_node.getElementsByTagName(WFConstants.TAG_NAME_NEXT_NODE)[0].childNodes[0].data
        else:
            node_name = name
            node_class_name = class_name
            params = parameters
            node_next_node = next_node

        if 'xml_position' in kwargs:
            xml_position = kwargs.get('xml_position')
            node_x_pos = xml_position.getElementsByTagName(WFConstants.TAG_NAME_X)[0].childNodes[0].data
            node_y_pos = xml_position.getElementsByTagName(WFConstants.TAG_NAME_Y)[0].childNodes[0].data
            node_width = xml_position.getElementsByTagName(WFConstants.TAG_NAME_WIDTH)[0].childNodes[0].data
            node_height = xml_position.getElementsByTagName(WFConstants.TAG_NAME_HEIGHT)[0].childNodes[0].data
        else:
            node_x_pos = x
            node_y_pos = y
            node_width = width
            node_height = height

        if 'xml_arrows' in kwargs:
            xml_arrows = kwargs.get('xml_arrows')
            xml_true_arrow = xml_arrows.getElementsByTagName(WFConstants.TAG_NAME_TRUE_ARROW)
            node_true_type = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_TYPE)[0].childNodes[0].data
            node_true_delta_x = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_X)[0].childNodes[0].data
            node_true_delta_y = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_Y)[0].childNodes[0].data
            xml_arrow = Arrow(type=str(node_true_type), delta_x=str(node_true_delta_x), delta_y=str(node_true_delta_y))
        else:
            xml_arrow = arrow

        Node.__init__(self, name=node_name, class_name=node_class_name, parameters=params,
                      x=node_x_pos, y=node_y_pos, width=node_width, height=node_height)

        self.arrow = xml_arrow
        self.next_node = node_next_node

    def createXmlNode(self):
        doc = Document()

        xml_node = doc.createElement(WFConstants.TAG_NAME_PROCESS_NODE)

        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(self.name)
        xml_name_node.appendChild(xml_name_node_content)

        xml_action_node = doc.createElement(WFConstants.TAG_NAME_ACTION)

        xml_class_name_node = doc.createElement(WFConstants.TAG_NAME_CLASS_NAME)
        xml_class_name_node_content =  doc.createTextNode(self.class_name)
        xml_class_name_node.appendChild(xml_class_name_node_content)

        xml_action_node.appendChild(xml_class_name_node)

        for parameter in self.parameters:

            xml_param_node = doc.createElement(WFConstants.TAG_NAME_PARAM)
            xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_NAME, parameter.name)
            if not parameter.without_prefix:
                if parameter.is_constant:
                    prefix = "constant:"
                else:
                    prefix = "variable:"
                xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, prefix + parameter.value)
            else:
                xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, parameter.value)
            xml_action_node.appendChild(xml_param_node)


        xml_node.appendChild(xml_name_node)
        xml_node.appendChild(xml_action_node)

        if len(self.next_node) > 0:
            xml_next_node = doc.createElement(WFConstants.TAG_NAME_NEXT_NODE)
            xml_next_node_content =  doc.createTextNode(self.next_node)
            xml_next_node.appendChild(xml_next_node_content)
            xml_node.appendChild(xml_next_node)

        return xml_node


    def arrowsToXml(self):
        doc = Document()

        xml_arrows_node = doc.createElement(WFConstants.TAG_NAME_ARROWS)

        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(self.name)
        xml_name_node.appendChild(xml_name_node_content)

        xml_true_arrow = doc.createElement(WFConstants.TAG_NAME_TRUE_ARROW)

        xml_true_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)

        xml_true_arrow_type_content = doc.createTextNode(self.arrow.type)
        xml_true_arrow_type_delta_x_content = doc.createTextNode(self.arrow.delta_x)
        xml_true_arrow_type_delta_y_content = doc.createTextNode(self.arrow.delta_y)

        xml_true_arrow_type.appendChild(xml_true_arrow_type_content)

        xml_true_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_true_arrow_delta_x.appendChild(xml_true_arrow_type_delta_x_content)

        xml_true_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_true_arrow_delta_y.appendChild(xml_true_arrow_type_delta_y_content)

        xml_false_arrow = doc.createElement(WFConstants.TAG_NAME_FALSE_ARROW)

        xml_false_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)

        xml_false_arrow_type_content = doc.createTextNode(self.arrow.type)
        xml_false_arrow_type_delta_x_content = doc.createTextNode(self.arrow.delta_x)
        xml_false_arrow_type_delta_y_content = doc.createTextNode(self.arrow.delta_y)

        xml_false_arrow_type.appendChild(xml_false_arrow_type_content)

        xml_false_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_false_arrow_delta_x.appendChild(xml_false_arrow_type_delta_x_content)

        xml_false_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_false_arrow_delta_y.appendChild(xml_false_arrow_type_delta_y_content)

        xml_true_arrow.appendChild(xml_true_arrow_type)
        xml_true_arrow.appendChild(xml_true_arrow_delta_x)
        xml_true_arrow.appendChild(xml_true_arrow_delta_y)

        xml_false_arrow.appendChild(xml_false_arrow_type)
        xml_false_arrow.appendChild(xml_false_arrow_delta_x)
        xml_false_arrow.appendChild(xml_false_arrow_delta_y)

        xml_arrows_node.appendChild(xml_name_node)
        xml_arrows_node.appendChild(xml_true_arrow)
        xml_arrows_node.appendChild(xml_false_arrow)

        return xml_arrows_node




class RuleNode(Node):
    def __init__(self, name="", class_name="", parameters=Parameters({}),
                 next_node_true="", next_node_false="", x="0", y="0", width="100", height="24",
                 arrow_true=Arrow(), arrow_false=Arrow(), **kwargs):

        if 'xml_node' in kwargs:
            xml_node = kwargs.get('xml_node')
            node_name = xml_node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
            node_class_name = xml_node.getElementsByTagName(WFConstants.TAG_NAME_CLASS_NAME)[0].childNodes[0].data
            xml_params = xml_node.getElementsByTagName(WFConstants.TAG_NAME_PARAM)
            param_dict = {}
            for xml_param in xml_params:
                param_dict[xml_param.getAttribute(WFConstants.ATTRIBUTE_NAME_NAME)] = \
                    xml_param.getAttribute(WFConstants.ATTRIBUTE_NAME_VALUE)
            params = Parameters(param_dict)
            node_next_true = xml_node.getElementsByTagName(WFConstants.TAG_NAME_NEXT_NODE_TRUE)[0].childNodes[0].data
            node_next_false = xml_node.getElementsByTagName(WFConstants.TAG_NAME_NEXT_NODE_FALSE)[0].childNodes[0].data
        else:
            node_name = name
            node_class_name = class_name
            params = parameters
            node_next_true = next_node_true
            node_next_false = next_node_false

        if 'xml_position' in kwargs:
            xml_position = kwargs.get('xml_position')
            node_x_pos = xml_position.getElementsByTagName(WFConstants.TAG_NAME_X)[0].childNodes[0].data
            node_y_pos = xml_position.getElementsByTagName(WFConstants.TAG_NAME_Y)[0].childNodes[0].data
            node_width = xml_position.getElementsByTagName(WFConstants.TAG_NAME_WIDTH)[0].childNodes[0].data
            node_height = xml_position.getElementsByTagName(WFConstants.TAG_NAME_HEIGHT)[0].childNodes[0].data
        else:
            node_x_pos = x
            node_y_pos = y
            node_width = width
            node_height = height

        if 'xml_arrows' in kwargs:
            xml_arrows = kwargs.get('xml_arrows')
            xml_true_arrow = xml_arrows.getElementsByTagName(WFConstants.TAG_NAME_TRUE_ARROW)
            node_true_type = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_TYPE)[0].childNodes[0].data
            node_true_delta_x = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_X)[0].childNodes[0].data
            node_true_delta_y = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_Y)[0].childNodes[0].data
            xml_false_arrow = xml_arrows.getElementsByTagName(WFConstants.TAG_NAME_FALSE_ARROW)
            node_false_type = xml_false_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_TYPE)[0].childNodes[0].data
            node_false_delta_x = xml_false_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_X)[0].childNodes[0].data
            node_false_delta_y = xml_false_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_Y)[0].childNodes[0].data
            xml_arrow_true = Arrow(type=str(node_true_type), delta_x=str(node_true_delta_x), delta_y=str(node_true_delta_y))
            xml_arrow_false = Arrow(type=str(node_false_type), delta_x=str(node_false_delta_x), delta_y=str(node_false_delta_y))
        else:
            xml_arrow_true = arrow_true
            xml_arrow_false = arrow_false


        Node.__init__(self, name=node_name, class_name=node_class_name, parameters=params,
                      x=node_x_pos, y=node_y_pos, width=node_width, height=node_height)
        self.arrow_true = xml_arrow_true
        self.arrow_false = xml_arrow_false
        self.next_node_true = node_next_true
        self.next_node_false = node_next_false

    def createXmlNode(self):
        doc = Document()

        xml_node = doc.createElement(WFConstants.TAG_NAME_RULE_NODE)

        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(self.name)
        xml_name_node.appendChild(xml_name_node_content)

        xml_action_node = doc.createElement(WFConstants.TAG_NAME_ACTION)

        xml_class_name_node = doc.createElement(WFConstants.TAG_NAME_CLASS_NAME)
        xml_class_name_node_content =  doc.createTextNode(self.class_name)
        xml_class_name_node.appendChild(xml_class_name_node_content)

        xml_action_node.appendChild(xml_class_name_node)

        for parameter in node.parameters:

            xml_param_node = doc.createElement(WFConstants.TAG_NAME_PARAM)
            xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_NAME, parameter.name)
            if not parameter.without_prefix:
                if parameter.is_constant:
                    prefix = "constant:"
                else:
                    prefix = "variable:"
                xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, prefix + parameter.value)
            else:
                xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, parameter.value)
            xml_action_node.appendChild(xml_param_node)


        xml_node.appendChild(xml_name_node)
        xml_node.appendChild(xml_action_node)

        if len(self.next_node_true) > 0:
            xml_next_node = doc.createElement(WFConstants.TAG_NAME_NEXT_NODE_TRUE)
            xml_next_node_content =  doc.createTextNode(self.next_node_true)
            xml_next_node.appendChild(xml_next_node_content)
            xml_node.appendChild(xml_next_node)
        if len(self.next_node_false) > 0:
            xml_next_node = doc.createElement(WFConstants.TAG_NAME_NEXT_NODE_FALSE)
            xml_next_node_content =  doc.createTextNode(self.next_node_false)
            xml_next_node.appendChild(xml_next_node_content)
            xml_node.appendChild(xml_next_node)

        return xml_node

    def arrowsToXml(self):
        doc = Document()

        xml_arrows_node = doc.createElement(WFConstants.TAG_NAME_ARROWS)

        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(self.name)
        xml_name_node.appendChild(xml_name_node_content)

        xml_true_arrow = doc.createElement(WFConstants.TAG_NAME_TRUE_ARROW)

        xml_true_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)

        xml_true_arrow_type_content = doc.createTextNode(self.arrow_true.type)
        xml_true_arrow_type_delta_x_content = doc.createTextNode(self.arrow_true.delta_x)
        xml_true_arrow_type_delta_y_content = doc.createTextNode(self.arrow_true.delta_y)

        xml_true_arrow_type.appendChild(xml_true_arrow_type_content)

        xml_true_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_true_arrow_delta_x.appendChild(xml_true_arrow_type_delta_x_content)

        xml_true_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_true_arrow_delta_y.appendChild(xml_true_arrow_type_delta_y_content)

        xml_false_arrow = doc.createElement(WFConstants.TAG_NAME_FALSE_ARROW)

        xml_false_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)

        xml_false_arrow_type_content = doc.createTextNode(self.arrow_false.type)
        xml_false_arrow_type_delta_x_content = doc.createTextNode(self.arrow_false.delta_x)
        xml_false_arrow_type_delta_y_content = doc.createTextNode(self.arrow_false.delta_y)

        xml_false_arrow_type.appendChild(xml_false_arrow_type_content)

        xml_false_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_false_arrow_delta_x.appendChild(xml_false_arrow_type_delta_x_content)

        xml_false_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_false_arrow_delta_y.appendChild(xml_false_arrow_type_delta_y_content)

        xml_true_arrow.appendChild(xml_true_arrow_type)
        xml_true_arrow.appendChild(xml_true_arrow_delta_x)
        xml_true_arrow.appendChild(xml_true_arrow_delta_y)

        xml_false_arrow.appendChild(xml_false_arrow_type)
        xml_false_arrow.appendChild(xml_false_arrow_delta_x)
        xml_false_arrow.appendChild(xml_false_arrow_delta_y)

        xml_arrows_node.appendChild(xml_name_node)
        xml_arrows_node.appendChild(xml_true_arrow)
        xml_arrows_node.appendChild(xml_false_arrow)

        return xml_arrows_node


class SwitchNode(Node):
    def __init__(self, name="", class_name="", parameters=Parameters({}),
                 next_node_default="", next_node_cases={}, x="0", y="0", width="100", height="24",
                 arrow_default=Arrow(), arrow_cases=[], arrow_true=Arrow(), arrow_false=Arrow()):

        if 'xml_node' in kwargs:
            xml_node = kwargs.get('xml_node')
            node_name = xml_node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
            node_class_name = xml_node.getElementsByTagName(WFConstants.TAG_NAME_CLASS_NAME)[0].childNodes[0].data
            xml_params = xml_node.getElementsByTagName(WFConstants.TAG_NAME_PARAM)
            param_dict = {}
            for xml_param in xml_params:
                param_dict[xml_param.getAttribute(WFConstants.ATTRIBUTE_NAME_NAME)] = \
                    xml_param.getAttribute(WFConstants.ATTRIBUTE_NAME_VALUE)
            params = Parameters(param_dict)
            node_next_default = xml_node.getElementsByTagName(WFConstants.TAG_NAME_DEFAULT)[0].childNodes[0].data
            cases_dict  ={}
            cases = xml_node.getElementsByTagName(WFConstants.TAG_NAME_SWITCH)
            for case in cases:
                cases_dict[case.getAttribute(WFConstants.ATTRIBUTE_NAME_NAME)] = case.data

        else:
            node_name = name
            node_class_name = class_name
            params = parameters
            node_next_default = next_node_default
            cases_dict = next_node_cases

        if 'xml_position' in kwargs:
            xml_position = kwargs.get('xml_position')
            node_x_pos = xml_position.getElementsByTagName(WFConstants.TAG_NAME_X)[0].childNodes[0].data
            node_y_pos = xml_position.getElementsByTagName(WFConstants.TAG_NAME_Y)[0].childNodes[0].data
            node_width = xml_position.getElementsByTagName(WFConstants.TAG_NAME_WIDTH)[0].childNodes[0].data
            node_height = xml_position.getElementsByTagName(WFConstants.TAG_NAME_HEIGHT)[0].childNodes[0].data
        else:
            node_x_pos = x
            node_y_pos = y
            node_width = width
            node_height = height

        if 'xml_arrows' in kwargs:
            xml_arrows = kwargs.get('xml_arrows')
            xml_true_arrow = xml_arrows.getElementsByTagName(WFConstants.TAG_NAME_TRUE_ARROW)
            node_true_type = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_TYPE)[0].childNodes[0].data
            node_true_delta_x = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_X)[0].childNodes[0].data
            node_true_delta_y = xml_true_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_Y)[0].childNodes[0].data
            xml_false_arrow = xml_arrows.getElementsByTagName(WFConstants.TAG_NAME_FALSE_ARROW)
            node_false_type = xml_false_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_TYPE)[0].childNodes[0].data
            node_false_delta_x = xml_false_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_X)[0].childNodes[0].data
            node_false_delta_y = xml_false_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_Y)[0].childNodes[0].data
            xml_default_arrow = xml_arrows.getElementsByTagName(WFConstants.TAG_NAME_DEFAULT_ARROW)
            node_default_type = xml_default_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_TYPE)[0].childNodes[0].data
            node_default_delta_x = xml_default_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_X)[0].childNodes[0].data
            node_default_delta_y = xml_default_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_Y)[0].childNodes[0].data
            xml_case_arrows = xml_node.getElementsByTagName(WFConstants.TAG_NAME_CASE_ARROW)
            xml_arrow_cases = []
            for xml_case_arrow in xml_case_arrows:
                node_case_type = xml_case_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_TYPE)[0].childNodes[0].data
                node_case_delta_x = xml_case_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_X)[0].childNodes[0].data
                node_case_delta_y = xml_case_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_DELTA_Y)[0].childNodes[0].data
                node_case_name = xml_case_arrow[0].getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
                xml_arrow_cases.append(Arrow(type=str(node_case_type), delta_x=str(node_case_delta_x), delta_y=str(node_case_delta_y), name=node_case_name))

            xml_arrow_true = Arrow(type=str(node_true_type), delta_x=str(node_true_delta_x), delta_y=str(node_true_delta_y))
            xml_arrow_false = Arrow(type=str(node_false_type), delta_x=str(node_false_delta_x), delta_y=str(node_false_delta_y))
            xml_arrow_default = Arrow(type=str(node_default_type), delta_x=str(node_default_delta_x), delta_y=str(node_default_delta_y))
        else:
            xml_arrow_true = arrow_true
            xml_arrow_false = arrow_false
            xml_arrow_default = arrow_default
            xml_arrow_cases = arrow_cases


        Node.__init__(self, name=node_name, class_name=node_class_name, parameters=params,
                      x=node_x_pos, y=node_y_pos, width=node_width, height=node_height)
        self.arrow_true = xml_arrow_true
        self.arrow_false = xml_arrow_false
        self.next_node_default = node_next_default
        self.next_node_cases = cases_dict
        self.arrow_default = xml_arrow_default
        self.arrow_cases = xml_arrow_cases

    def createXmlNode(self):
        doc = Document()

        xml_node = doc.createElement(WFConstants.TAG_NAME_SWITCH_NODE)

        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(self.name)
        xml_name_node.appendChild(xml_name_node_content)

        xml_action_node = doc.createElement(WFConstants.TAG_NAME_ACTION)

        xml_class_name_node = doc.createElement(WFConstants.TAG_NAME_CLASS_NAME)
        xml_class_name_node_content =  doc.createTextNode(self.class_name)
        xml_class_name_node.appendChild(xml_class_name_node_content)

        xml_action_node.appendChild(xml_class_name_node)

        for parameter in node.parameters:

            xml_param_node = doc.createElement(WFConstants.TAG_NAME_PARAM)
            xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_NAME, parameter.name)
            if not parameter.without_prefix:
                if parameter.is_constant:
                    prefix = "constant:"
                else:
                    prefix = "variable:"
                xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, prefix + parameter.value)
            else:
                xml_param_node.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, parameter.value)
            xml_action_node.appendChild(xml_param_node)


        xml_node.appendChild(xml_name_node)
        xml_node.appendChild(xml_action_node)

        if len(self.next_node_cases.keys()) > 0:
            for key in next_node_cases.keys():
                xml_case_node = doc.createElement(WFConstants.TAG_NAME_SWITCH)
                xml_case_node.setAttribute(WFConstants.ATTRIBUTE_NAME_NAME, key)
                xml_case_node_content =  doc.createTextNode(next_node_cases[key])
                xml_case_node.appendChild(xml_case_node_content)
                xml_node.appendChild(xml_case_node)

        if len(self.next_node_default) > 0:
            xml_default_node = doc.createElement(WFConstants.TAG_NAME_DEFAULT)
            xml_default_node_content =  doc.createTextNode(self.next_node_default)
            xml_default_node.appendChild(xml_default_node_content)
            xml_node.appendChild(xml_next_node)

        return xml_node

    def arrowsToXml(self):

        xml_arrows_node = doc.createElement(WFConstants.TAG_NAME_ARROWS)

        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(self.name)
        xml_name_node.appendChild(xml_name_node_content)

        xml_true_arrow = doc.createElement(WFConstants.TAG_NAME_TRUE_ARROW)

        xml_true_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)

        xml_true_arrow_type_content = doc.createTextNode(self.arrow_true.type)
        xml_true_arrow_type_delta_x_content = doc.createTextNode(self.arrow_true.delta_x)
        xml_true_arrow_type_delta_y_content = doc.createTextNode(self.arrow_true.delta_y)

        xml_true_arrow_type.appendChild(xml_true_arrow_type_content)

        xml_true_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_true_arrow_delta_x.appendChild(xml_true_arrow_type_delta_x_content)

        xml_true_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_true_arrow_delta_y.appendChild(xml_true_arrow_type_delta_y_content)

        xml_false_arrow = doc.createElement(WFConstants.TAG_NAME_FALSE_ARROW)

        xml_false_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)

        xml_false_arrow_type_content = doc.createTextNode(self.arrow_false.type)
        xml_false_arrow_type_delta_x_content = doc.createTextNode(self.arrow_false.delta_x)
        xml_false_arrow_type_delta_y_content = doc.createTextNode(self.arrow_false.delta_y)

        xml_false_arrow_type.appendChild(xml_false_arrow_type_content)

        xml_false_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_false_arrow_delta_x.appendChild(xml_false_arrow_type_delta_x_content)

        xml_false_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_false_arrow_delta_y.appendChild(xml_false_arrow_type_delta_y_content)

        xml_true_arrow.appendChild(xml_true_arrow_type)
        xml_true_arrow.appendChild(xml_true_arrow_delta_x)
        xml_true_arrow.appendChild(xml_true_arrow_delta_y)

        xml_false_arrow.appendChild(xml_false_arrow_type)
        xml_false_arrow.appendChild(xml_false_arrow_delta_x)
        xml_false_arrow.appendChild(xml_false_arrow_delta_y)


        xml_switch_arrow = doc.createElement(WFConstants.TAG_NAME_SWITCH_ARROW)

        xml_default_arrow = doc.createElement(WFConstants.TAG_NAME_DEFAULT_ARROW)

        xml_default_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)

        xml_default_arrow_type_content = doc.createTextNode(self.arrow_default.type)
        xml_default_arrow_type_delta_x_content = doc.createTextNode(self.arrow_default.delta_x)
        xml_default_arrow_type_delta_y_content = doc.createTextNode(self.arrow_default.delta_y)

        xml_default_arrow_type.appendChild(xml_default_arrow_type_content)

        xml_default_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_default_arrow_delta_x.appendChild(xml_default_arrow_type_delta_x_content)

        xml_default_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_default_arrow_delta_y.appendChild(xml_default_arrow_type_delta_y_content)

        xml_default_arrow.appendChild(xml_default_arrow_type)
        xml_default_arrow.appendChild(xml_default_arrow_delta_x)
        xml_default_arrow.appendChild(xml_default_arrow_delta_y)

        xml_switch_arrow.appendChild(xml_default_arrow)

        if len(self.arrow_cases) > 0:
            for arrow_case in arrow_cases:
                xml_case_arrow = doc.createElement(WFConstants.TAG_NAME_CASE_ARROW)

                xml_case_arrow_name_content = doc.createTextNode(self.arrow_case.name)
                xml_case_arrow_type_content = doc.createTextNode(self.arrow_case.type)
                xml_case_arrow_type_delta_x_content = doc.createTextNode(self.arrow_case.delta_x)
                xml_case_arrow_type_delta_y_content = doc.createTextNode(self.arrow_case.delta_y)

                xml_case_arrow_name = doc.createElement(WFConstants.TAG_NAME_NAME)
                xml_case_arrow_name.appendChild(xml_case_arrow_name_content)

                xml_case_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)
                xml_case_arrow_type.appendChild(xml_case_arrow_type_content)

                xml_case_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
                xml_case_arrow_delta_x.appendChild(xml_case_arrow_type_delta_x_content)

                xml_case_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
                xml_case_arrow_delta_y.appendChild(xml_case_arrow_type_delta_y_content)

                xml_case_arrow.appendChild(xml_case_arrow_name)
                xml_case_arrow.appendChild(xml_case_arrow_type)
                xml_case_arrow.appendChild(xml_case_arrow_delta_x)
                xml_case_arrow.appendChild(xml_case_arrow_delta_y)

                xml_switch_arrow.appendChild(xml_case_arrow)



        xml_arrows_node.appendChild(xml_name_node)
        xml_arrows_node.appendChild(xml_true_arrow)
        xml_arrows_node.appendChild(xml_false_arrow)
        xml_arrows_node.appendChild(xml_switch_arrow)

        return xml_arrows_node


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
            name="Set " + self.request_json,
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
                "composite_name_log": "%" + self.request_url + "%",
                "request_json_log": "%" + self.request_json + "%",
                "response_json_log": "%" + self.response_json + "%"}),
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
                "error_message": "rest query error %http_code%;" + \
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


        # Setting right node sequence
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

        LOG_INFO.parameters.insertUpdateValue("log_level", "INFORMATIVE")
        message = LOG_INFO.parameters.getValue("log_message")
        message = message + " " + wf_name + " started"
        START_LOG.parameters.insertUpdateValue("log_message", message)

        LOG_DEBUG = ProcessNode(
            name="LogDebug: " + wf_name + " started",
            parameters=Parameters(WFConstants.LOG_ORDINARY_PARAMS),
            class_name=WFConstants.CLASS_NAME_LOG)

        LOG_DEBUG.parameters.insertUpdateValue("log_level", "INFORMATIVE")
        message = LOG_DEBUG.parameters.getValue("log_message")
        message = message + " " + wf_name + " started with request json=%s"
        LOG_DEBUG.parameters.insertUpdateValue("log_message", message)
        LOG_DEBUG.parameters.insertUpdateValue("param3", "request_json")

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

        # Setting right node sequence
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


