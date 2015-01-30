import WFConstants
import sys, traceback
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.dom.minidom import Document
import WFNodes
from WFNodes import Parameters, Parameter, ProcessNode, RuleNode, NodeGroup, RestRequestGroup
from WFExceptions import DuplicateNodeError, DuplicateParamError
import re

#TODO
#1 Raise exception in nodegroup
#2 Raise exception in Parameter and Parameters classes
#3 Create fields in parameter class indicating whether parameter name is constant or variable
#4 In delete node raise exception is deleted node has the same name as WF name
#5 Move removing node group nodes from WF from addNodeGroup to higher level method
#6 Create method setStartNode
#7 Add raise exception to addHandler method
#8 Modify WFVariables to save typical variable names (error_code, error_message, etc)
#9 Complete getNode method

# Helper functions
def formatXml(file_name):
    myfile = open(file_name, 'r')
    data=myfile.read().replace('\n', '')
    data = re.sub(' +',' ',data)
    data = re.sub('> <','><',data)
    myfile.close()
    return data

def exception(method_to_try):

    def wrapper(self, node):
        if not self.hasNodeName(node.name):
            raise DuplicateNodeError(node.name)
        else:
            return method_to_try(self, node)
    return wrapper


class DomManager:

    def __init__(self, file_name):
        self.file_name = file_name
        try:
            self.dom_tree = xml.dom.minidom.parseString(formatXml(file_name))
            self.dom_tree_backup = xml.dom.minidom.parseString(formatXml(file_name))
            self.need_backup = True
        except Exception as e:
            self.dom_tree = xml.dom.minidom.parseString(WFConstants.BASE_WF)
            self.need_backup = False
        self.collection = self.dom_tree.documentElement
        temp_filename = file_name.split(".xml")[0]
        temp_filename = temp_filename.split("/")[-1]
        self.renameWF(temp_filename)
            
    def overwrightOriginalFile(self):
        if self.need_backup:
            backup_file_name = self.file_name.split(".xml")[0] + "_backup.xml"
            file_backup = open(backup_file_name, 'w')
            file_backup.write(self.dom_tree_backup.toxml(encoding='utf-8'))
        
        file = open(self.file_name, 'w')
        file.write(self.dom_tree.toprettyxml(encoding='utf-8', indent="   "))
        file.close()
        
    def isDomTreeEmpty(self):
        return self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME).length == 0 or \
            self.collection.getElementsByTagName(WFConstants.TAG_NAME_START_NODE).length == 0
        
    def getWFName(self):
        for node in self.collection.childNodes:
            if node.nodeName == WFConstants.TAG_NAME_NAME:
                return node.childNodes[0].nodeValue

    def renameWF(self, new_name):

        for node in self.collection.childNodes:
            if node.nodeName == WFConstants.TAG_NAME_NAME:
                wf_name_node = node
        for text in wf_name_node.childNodes:
            text.data = unicode(new_name)
            
        self.insertUpdateInitialCasePacket("WORKFLOW_NAME", new_name, "String")

    def findLowestPosition(self):
        positions = self.collection.getElementsByTagName(WFConstants.TAG_NAME_POSITION)
        lowest_position = 0
       
        for pos in positions :
            new_pos = pos.getElementsByTagName('Y')[0].childNodes[0].data
            if lowest_position < new_pos:
                lowest_position = new_pos
        return lowest_position
        
    def casePacketContains(self, var_name):
        
        case_packet = self.collection.getElementsByTagName(WFConstants.TAG_NAME_CASE_PACKET)[0]
        case_packet_variables = case_packet.getElementsByTagName(WFConstants.TAG_NAME_CASE_PACKET_VAR)
        
        for variable in case_packet_variables:
            if variable.getAttribute(WFConstants.ATTRIBUTE_NAME_NAME) == var_name:
                return True
        
        return False

    def initialCasePacketContains(self, var_name):
        
        initial_case_packet = self.collection.getElementsByTagName(WFConstants.TAG_NAME_INIT_CASE_PACKET)[0]
        initial_case_packet_variables = initial_case_packet.getElementsByTagName(WFConstants.TAG_NAME_INIT_CASE_PACKET_VAR)
        
        for variable in initial_case_packet_variables:
            if variable.getAttribute(WFConstants.ATTRIBUTE_NAME_NAME) == var_name:
                return True
        
        return False
        
    def hasNodeName(self, node_name):
        process_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_PROCESS_NODE)
                
        for node in process_nodes:
            exist_node_name = node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
            if exist_node_name == node_name:
                return True
        
        rule_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_RULE_NODE)
        
        for node in rule_nodes:
            exist_node_name = node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
            if exist_node_name == node_name:
                return True
                
        return False

    def getNode(self, node_name):
        if self.getWFName() != node_name:
            name_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME)
            for name_node in name_nodes:
                if name_node.firstChild.nodeValue == node_name:
                    xml_node = name_node.parentNode

    def integrateRestGroup(self, node_group):
        self.addNodeGroup(node_group)
        for node in node_group:
            for parameter in node.parameters:
                if not parameter.without_prefix and not parameter.is_constant:
                    self.insertUpdateCasePacket(parameter.value, parameter.type)

        if self.hasNodeName(WFVariables.NODE_NAME_SET_SY_URL):
            set_sy_node = self.getNode(WFVariables.NODE_NAME_SET_SY_URL)
            self.removeNode(self, WFVariables.NODE_NAME_SET_SY_URL)

            set_sy_node.parameters.insertUpdateValue(node_group.request_url,\
                "%" + WFVariables.VARIABLE_NAME_SY_PROTOCOL + "%://%" +\
                WFVariables.VARIABLE_NAME_SY_IP + "%:%" + WFVariables.VARIABLE_NAME_SY_PORT + "%/" + node_group.url)

            self.addNode(set_sy_node)

    def addNodeGroup(self, node_group):
        try:
            for node in node_group:
                self.addNode(node)
            for ex_node_group in node_group.node_group_list:
                for node in ex_node_group:
                    self.addNode(node)
        except Exception as e:
            raise e

    def addHandler(self, handler):

        handler_to_add = self.createXmlHandler(handler)

        case_packet = self.collection.getElementsByTagName(WFConstants.TAG_NAME_CASE_PACKET)[0]
        self.collection.insertBefore(handler_to_add, case_packet)

    def addNode(self, node):
        if self.hasNodeName(node.name):
            raise DuplicateNodeError(node.name)
        else:
            all_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NODES)[0]
            node_to_add = self.createXmlNode(node)
            all_nodes.appendChild(node_to_add)
            
            coordinates = self.collection.getElementsByTagName(WFConstants.TAG_NAME_COORDINATES)[0]

            coordinates_and_arrows = self.createXmlPosAndArrows(node)
            coordinates.appendChild(coordinates_and_arrows[1])
            
            arrows = self.collection.getElementsByTagName(WFConstants.TAG_NAME_ARROWS)[0]
            coordinates.insertBefore(coordinates_and_arrows[0], arrows)


    @exception
    def addNodeTest(self, node):
        
        all_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NODES)[0]
        node_to_add = self.createXmlNode(node)
        all_nodes.appendChild(node_to_add)
          
        coordinates = self.collection.getElementsByTagName("Work")[0]
        coordinates_and_arrows = self.createXmlPosAndArrows(node)
        coordinates.appendChild(coordinates_and_arrows[1])
        
        arrows = self.collection.getElementsByTagName(WFConstants.TAG_NAME_ARROWS)[0]
        coordinates.insertBefore(coordinates_and_arrows[0], arrows)

    def insertUpdateCasePacket(self, var_name, var_type):
        case_packet = self.collection.getElementsByTagName(WFConstants.TAG_NAME_CASE_PACKET)[0]
        
        if not self.casePacketContains(var_name):
            case_packet_var = self.createXmlCasePacketNode(var_name, var_type)
            case_packet.appendChild(case_packet_var)
        else:
            case_packet_variables = case_packet.getElementsByTagName(WFConstants.TAG_NAME_CASE_PACKET_VAR)
            for variable in case_packet_variables:
                if variable.getAttribute(WFConstants.ATTRIBUTE_NAME_NAME) == var_name:
                    variable.removeAttribute(WFConstants.ATTRIBUTE_NAME_TYPE)
                    variable.setAttribute(WFConstants.ATTRIBUTE_NAME_TYPE, var_type)

    def insertUpdateInitialCasePacket(self, var_name, var_value, var_type):
        initial_case_packet = self.collection.getElementsByTagName(WFConstants.TAG_NAME_INIT_CASE_PACKET)[0]

        if not self.initialCasePacketContains(var_name):
            self.insertUpdateCasePacket(var_name, var_type)
            initial_case_packet_var = self.createXmlInitialCasePacketNode(var_name, var_value)
            initial_case_packet.appendChild(initial_case_packet_var)
        else:
            initial_case_packet_variables = initial_case_packet.\
            getElementsByTagName(WFConstants.TAG_NAME_INIT_CASE_PACKET_VAR)
            for variable in initial_case_packet_variables:
                if variable.getAttribute(WFConstants.ATTRIBUTE_NAME_NAME) == var_name:
                    variable.removeAttribute(WFConstants.ATTRIBUTE_NAME_VALUE)
                    variable.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, var_value)

    def createXmlInitialCasePacketNode(self, var_name, var_value):
        doc = Document()

        xml_initial_case_packet_node = doc.createElement(WFConstants.TAG_NAME_INIT_CASE_PACKET_VAR)
        xml_initial_case_packet_node.setAttribute(WFConstants.ATTRIBUTE_NAME_NAME, var_name)
        xml_initial_case_packet_node.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, var_value)

        return xml_initial_case_packet_node

    def createXmlCasePacketNode(self, var_name, var_type):
        doc = Document()

        xml_case_packet_node = doc.createElement(WFConstants.TAG_NAME_CASE_PACKET_VAR)
        xml_case_packet_node.setAttribute(WFConstants.ATTRIBUTE_NAME_NAME, var_name)
        xml_case_packet_node.setAttribute(WFConstants.ATTRIBUTE_NAME_NAME, var_type)

        return xml_case_packet_node

    def createXmlHandler(self, handler):
        doc = Document()

        xml_handler = doc.createElement(WFConstants.TAG_NAME_END_HANDLER)
        xml_name_handler = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_handler_content = doc.createTextNode(handler.name)
        xml_name_handler.appendChild(xml_name_handler_content)

        xml_class_name_handler = doc.createElement(WFConstants.TAG_NAME_CLASS_NAME)
        xml_class_name_handler_content =  doc.createTextNode(handler.class_name)
        xml_class_name_handler.appendChild(xml_class_name_handler_content)

        xml_handler.appendChild(xml_name_handler)
        xml_handler.appendChild(xml_class_name_handler)

        for parameter in node.parameters:

            xml_param_handler = doc.createElement(WFConstants.TAG_NAME_PARAM)
            xml_param_handler.setAttribute(WFConstants.ATTRIBUTE_NAME_NAME, parameter.name)
            if not parameter.without_prefix:
                if parameter.is_constant:
                    prefix = "constant:"
                else:
                    prefix = "variable:"
                xml_param_handler.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, prefix + parameter.value)
            else:
                xml_param_handler.setAttribute(WFConstants.ATTRIBUTE_NAME_VALUE, parameter.value)
            xml_handler.appendChild(xml_param_handler)

        return xml_handler

    def createXmlNode(self, node):
        doc = Document()

        if isinstance(node, ProcessNode):
            xml_node = doc.createElement(WFConstants.TAG_NAME_PROCESS_NODE)
        if isinstance(node, RuleNode):
            xml_node = doc.createElement(WFConstants.TAG_NAME_RULE_NODE)
        
        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(node.name)
        xml_name_node.appendChild(xml_name_node_content)
        
        xml_action_node = doc.createElement(WFConstants.TAG_NAME_ACTION)
        
        xml_class_name_node = doc.createElement(WFConstants.TAG_NAME_CLASS_NAME)
        xml_class_name_node_content =  doc.createTextNode(node.class_name)
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
        
        if isinstance(node, ProcessNode):
            if len(node.next_node) > 0:
                xml_next_node = doc.createElement(WFConstants.TAG_NAME_NEXT_NODE)
                xml_next_node_content =  doc.createTextNode(node.next_node)
                xml_next_node.appendChild(xml_next_node_content)
                xml_node.appendChild(xml_next_node)
        
        if isinstance(node, RuleNode):
            if len(node.next_node_true) > 0:
                xml_next_node = doc.createElement(WFConstants.TAG_NAME_NEXT_NODE_TRUE)
                xml_next_node_content =  doc.createTextNode(node.next_node_true)
                xml_next_node.appendChild(xml_next_node_content)
                xml_node.appendChild(xml_next_node)
            if len(node.next_node_false) > 0:
                xml_next_node = doc.createElement(WFConstants.TAG_NAME_NEXT_NODE_FALSE)
                xml_next_node_content =  doc.createTextNode(node.next_node_false)
                xml_next_node.appendChild(xml_next_node_content)
                xml_node.appendChild(xml_next_node)

        return xml_node
        
    def createXmlPosAndArrows(self, node):
        doc = Document()
    
        xml_position_node = doc.createElement(WFConstants.TAG_NAME_POSITION)
        
        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(node.name)
        xml_name_node.appendChild(xml_name_node_content)
        
        xml_x_node = doc.createElement(WFConstants.TAG_NAME_X)
        xml_x_node_content = doc.createTextNode(node.x)
        xml_x_node.appendChild(xml_x_node_content)
        
        xml_y_node = doc.createElement(WFConstants.TAG_NAME_Y)
        xml_y_node_content = doc.createTextNode(node.y)
        xml_y_node.appendChild(xml_y_node_content)
        
        xml_width_node = doc.createElement(WFConstants.TAG_NAME_WIDTH)
        xml_width_node_content = doc.createTextNode(node.width)
        xml_width_node.appendChild(xml_width_node_content)
        
        xml_height_node = doc.createElement(WFConstants.TAG_NAME_HEIGHT)
        xml_height_node_content = doc.createTextNode(node.height)
        xml_height_node.appendChild(xml_height_node_content)
        
           
        xml_position_node.appendChild(xml_name_node)
        xml_position_node.appendChild(xml_x_node)
        xml_position_node.appendChild(xml_y_node)
        xml_position_node.appendChild(xml_width_node)
        xml_position_node.appendChild(xml_height_node)
        
        xml_arrows_node = doc.createElement(WFConstants.TAG_NAME_ARROWS)
        
        xml_name_node = doc.createElement(WFConstants.TAG_NAME_NAME)
        xml_name_node_content = doc.createTextNode(node.name)
        xml_name_node.appendChild(xml_name_node_content)
        
        xml_true_arrow = doc.createElement(WFConstants.TAG_NAME_TRUE_ARROW)
        
        xml_true_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)
        if isinstance(node, ProcessNode):
            xml_true_arrow_type_content = doc.createTextNode(node.arrow.type)
            xml_true_arrow_type_delta_x_content = doc.createTextNode(node.arrow.delta_x)
            xml_true_arrow_type_delta_y_content = doc.createTextNode(node.arrow.delta_y)
        if isinstance(node, RuleNode):
            xml_true_arrow_type_content =  doc.createTextNode(node.arrow_true.type)
            xml_true_arrow_type_delta_x_content = doc.createTextNode(node.arrow_true.delta_x)
            xml_true_arrow_type_delta_y_content = doc.createTextNode(node.arrow_true.delta_y)
        
        xml_true_arrow_type.appendChild(xml_true_arrow_type_content)
        
        xml_true_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_true_arrow_delta_x.appendChild(xml_true_arrow_type_delta_x_content)
        
        xml_true_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_true_arrow_delta_y.appendChild(xml_true_arrow_type_delta_y_content)
        
        xml_false_arrow = doc.createElement(WFConstants.TAG_NAME_FALSE_ARROW)
        
        xml_false_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)
        if isinstance(node, ProcessNode):
            xml_false_arrow_type_content =  doc.createTextNode(node.arrow.type)
            xml_false_arrow_type_delta_x_content =  doc.createTextNode(node.arrow.delta_x)
            xml_false_arrow_type_delta_y_content =  doc.createTextNode(node.arrow.delta_y)
        if isinstance(node, RuleNode):
            xml_false_arrow_type_content =  doc.createTextNode(node.arrow_false.type)
            xml_false_arrow_type_delta_x_content =  doc.createTextNode(node.arrow_false.delta_x)
            xml_false_arrow_type_delta_y_content =  doc.createTextNode(node.arrow_false.delta_y)

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
        
        
        return (xml_position_node, xml_arrows_node)

    def removeNextNodeReferences(self, node_name):
        process_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_PROCESS_NODE)
        rule_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_RULE_NODE)
        for process_node in process_nodes:
            node = process_node.getElementsByTagName(WFConstants.TAG_NAME_NEXT_NODE)
            if node.length == 1:
                if node[0].firstChild.nodeValue == node_name:
                    removed = process_node.removeChild(node[0])
                    removed.unlink()
        for rule_node in rule_nodes:
            node_true = rule_node.getElementsByTagName(WFConstants.TAG_NAME_NEXT_NODE_TRUE)
            node_false = rule_node.getElementsByTagName(WFConstants.TAG_NAME_NEXT_NODE_FALSE)
            if node_true.length == 1:
                if node_true[0].firstChild.nodeValue == node_name:
                    removed = rule_node.removeChild(node_true[0])
                    removed.unlink()
            if node_false.length == 1:
                if node_false[0].firstChild.nodeValue == node_name:
                    removed = rule_node.removeChild(node_false[0])
                    removed.unlink()

    def removeNode(self, node_name):
        if self.getWFName() != node_name:
            name_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME)
            for name_node in name_nodes:
                if name_node.firstChild.nodeValue == node_name:
                    removed = name_node.parentNode.parentNode.removeChild(name_node.parentNode)
                    removed.unlink()

    def removeNodeGroup(self, node_group):
        for node in node_group:
            self.removeNode(node.name)
            self.removeNextNodeReferences(node.name)
            for ex_node_group in node_group.node_group_list:
                for node in ex_node_group:
                    self.removeNode(node.name)
                    self.removeNextNodeReferences(node.name)
        

if __name__ == '__main__':

    if  len(sys.argv) == 1:
        print "Incorrect arguments number"
        print "Usage: python %s /pathToFile/filename.xml" %sys.argv[0]
    else:
        file_name = sys.argv[1]
        
        dom_manager = DomManager(file_name)
                 
        new_process_node = ProcessNode(name = "logger",
        parameters = Parameters(WFConstants.LOG_ORDINARY_PARAMS),
        class_name = WFConstants.CLASS_NAME_LOG,
        x = "100", y = "100", next_node = "Second json setter")

        second_node = ProcessNode(name = "Second json setter",
        parameters = Parameters({"output_json":"request_json"}),
        class_name = WFConstants.CLASS_NAME_JSON_SETTER,
        x = "100", y = "200")

        rule_node = RuleNode(name = "Equals?",
        parameters = Parameters(WFConstants.EQUALS_PARAMS),
        class_name = WFConstants.CLASS_NAME_EQUALS,
        next_node_true = "Equals?122",
        next_node_false = "logger",
        x = "100", y = "300")

        rule_node_2 = RuleNode(name = "Equals?122",
        parameters = Parameters(WFConstants.EQUALS_PARAMS),
        class_name = WFConstants.CLASS_NAME_EQUALS,
        next_node_true = "logger",
        next_node_false = "Second json setter",
        x = "300", y = "200")

        group = NodeGroup()
        group.injectNode(new_process_node)
        group.injectNode(second_node)
        group.injectNode(rule_node)

        group2 = NodeGroup() 
        group2.injectNode(rule_node_2)
        group.addGroup(group2)

        restGroup = RestRequestGroup('solution-composite-name/service-name/getMyDataByIdentifier')

        restGroup.makeVertical(initial_y=500, step=100)
        restGroup.moveX(500)
        #dom_manager.addNodeTest(rule_node)
        #dom_manager.addNode(rule_node)

        try:
            dom_manager.addNodeGroup(restGroup)
            #dom_manager.removeNextNodeReferences("logger")
            #dom_manager.removeNode("Default_WF")
            #dom_manager.addNode(rule_node)

            #dom_manager.renameWF("Renamed_WF")

            dom_manager.overwrightOriginalFile()

        except Exception as e:
            print e
        
    
                    

        
        
        
        
        
        
        

       
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        