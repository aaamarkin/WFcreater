import WFConstants
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.dom.minidom import Document
import WFNodes
import re

# Useful functions
def formatXml(file_name):
    myfile = open(file_name, 'r')
    data=myfile.read().replace('\n', '')
    data = re.sub(' +',' ',data)
    data = re.sub('> <','><',data)
    myfile.close()
    return data

      
class DomManager:

    def __init__(self, file_name):
        self.file_name = file_name
        try:
            self.dom_tree = xml.dom.minidom.parseString(formatXml(file_name))
            self.dom_tree_backup = xml.dom.minidom.parseString(formatXml(file_name))
            self.need_backup = True
        except Exception as e:
            self.dom_tree = xml.dom.minidom.parseString \
            (formatXml("/home/andrey/Desktop/WFcreater/Default_WF.xml"))
            self.need_backup = False
        self.collection = self.dom_tree.documentElement
            
    def overwrightOriginalFile(self):
        if self.need_backup:
            backup_file_name = self.file_name + "_backup"
            file_backup = open(backup_file_name, 'w')
            file_backup.write(self.dom_tree_backup.toxml(encoding='utf-8'))
        
        file = open(self.file_name, 'w')
        file.write(self.dom_tree.toprettyxml(encoding='utf-8', indent="   "))
        file.close()
        
    def isDomTreeEmpty(self):
        return self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME).length == 0 or \
            self.collection.getElementsByTagName(WFConstants.TAG_NAME_START_NODE).length == 0
        
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
        
    def addNode(self, node):
        all_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NODES)[0]
        node_to_add = self.createXmlNode(node)
        all_nodes.appendChild(node_to_add)
        
        coordinates = self.collection.getElementsByTagName(WFConstants.TAG_NAME_COORDINATES)[0]
        
        arrows = self.collection.getElementsByTagName(WFConstants.TAG_NAME_ARROWS)[0]
        
        coordinates_and_arrows = self.createXmlPosAndArrows(node)
        coordinates.insertBefore(coordinates_and_arrows[0], arrows)
        coordinates.appendChild(coordinates_and_arrows[1])
        
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

    def createXmlNode(self, node):
        doc = Document()
    
        xml_process_node = doc.createElement(WFConstants.TAG_NAME_PROCESS_NODE)
        
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
        
                
        xml_process_node.appendChild(xml_name_node)
        xml_process_node.appendChild(xml_action_node)
        
        if len(node.next_node) > 0:
            xml_next_node = doc.createElement(WFConstants.TAG_NAME_NEXT_NODE)
            xml_next_node_content =  doc.createTextNode(node.next_node)
            xml_next_node.appendChild(xml_next_node_content)
            xml_process_node.appendChild(xml_next_node)
        
        return xml_process_node
        
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
        xml_true_arrow_type_content =  doc.createTextNode(node.arrow.type)
        xml_true_arrow_type.appendChild(xml_true_arrow_type_content)
        
        xml_true_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_true_arrow_type_delta_x_content =  doc.createTextNode(node.arrow.delta_x)
        xml_true_arrow_delta_x.appendChild(xml_true_arrow_type_delta_x_content)
        
        xml_true_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_true_arrow_type_delta_y_content =  doc.createTextNode(node.arrow.delta_y)
        xml_true_arrow_delta_y.appendChild(xml_true_arrow_type_delta_y_content)
        
        xml_false_arrow = doc.createElement(WFConstants.TAG_NAME_FALSE_ARROW)
        
        xml_false_arrow_type = doc.createElement(WFConstants.TAG_NAME_TYPE)
        xml_false_arrow_type_content =  doc.createTextNode(node.arrow.type)
        xml_false_arrow_type.appendChild(xml_false_arrow_type_content)
        
        xml_false_arrow_delta_x = doc.createElement(WFConstants.TAG_NAME_DELTA_X)
        xml_false_arrow_type_delta_x_content =  doc.createTextNode(node.arrow.delta_x)
        xml_false_arrow_delta_x.appendChild(xml_false_arrow_type_delta_x_content)
        
        xml_false_arrow_delta_y = doc.createElement(WFConstants.TAG_NAME_DELTA_Y)
        xml_false_arrow_type_delta_y_content =  doc.createTextNode(node.arrow.delta_y)
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
        

if __name__ == '__main__':
    if  len(sys.argv) == 1:
        print "Incorrect number of parameters"
        print "Launch like this: python WFParser /pathToFile/filename.xml"
    else:
        file_name = sys.argv[1]
        
        
        dom_manager = DomManager(file_name)
                 
        new_process_node = WFNodes.LogNode(name = "logger", x = "100", y = "100", next_node = "Second json setter")
        second_node = WFNodes.JsonSetterNode(name = "Second json setter", x = "100", y = "200")
        dom_manager.addNode(new_process_node)
        dom_manager.addNode(second_node)
        dom_manager.renameWF("Renamed_WF")
        dom_manager.overwrightOriginalFile()
       
    
                    

        
        
        
        
        
        
        

       
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        