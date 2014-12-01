#!/usr/bin/python
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.dom.minidom import Document
import WFNodes

      
class DomManager:

    def __init__(self, dom_tree):
        self.dom_tree = dom_tree
        self.collection = self.dom_tree.documentElement
        
    def get_dom_tree(self):
        return self.dom_tree
        
    def is_dom_tree_empty(self):
        return self.collection.getElementsByTagName("Workflow").length == 0
        
    def find_lowest_position(self):
        positions = self.collection.getElementsByTagName("Position")
        lowest_position = 0
       
        for pos in positions :
            new_pos = pos.getElementsByTagName('Y')[0].childNodes[0].data
            if lowest_position < new_pos:
                lowest_position = new_pos
        return lowest_position
        
    def case_packet_contains(self, var_name):
        
        case_packet = self.collection.getElementsByTagName("Case-Packet")[0]
        case_packet_variables = case_packet.getElementsByTagName("Variable")
        
        for variable in case_packet_variables:
            if variable.getAttribute("name") == var_name:
                return True
        
        return False
        
    def has_node_name(self, node_name):
        process_nodes = self.collection.getElementsByTagName("Process-Node")
                
        for node in process_nodes:
            exist_node_name = node.getElementsByTagName('Name')[0].childNodes[0].data
            if exist_node_name == node_name:
                return True
        
        rule_nodes = self.collection.getElementsByTagName("Rule-Node")
        
        for node in rule_nodes:
            exist_node_name = node.getElementsByTagName('Name')[0].childNodes[0].data
            if exist_node_name == node_name:
                return True
                
        return False
        
    def addNode(self, node):
        all_nodes = self.collection.getElementsByTagName("Nodes")[0]
        node_to_add = self.create_xml_node(node)
        all_nodes.appendChild(node_to_add)
        
        coordinates = self.collection.getElementsByTagName("Coordinates")[0]
        
        arrows = self.collection.getElementsByTagName("Arrows")[0]
        
        coordinates_and_arrows = self.create_xml_pos_and_arrows(node)
        coordinates.insertBefore(coordinates_and_arrows[0], arrows)
        coordinates.appendChild(coordinates_and_arrows[1])
        
    def create_xml_node(self, node):
        doc = Document()
    
        xml_process_node = doc.createElement("Process-Node")
        
        xml_name_node = doc.createElement("Name")
        xml_name_node_content = doc.createTextNode(node.name)
        xml_name_node.appendChild(xml_name_node_content)
        
        xml_action_node = doc.createElement("Action")
        
        xml_class_name_node = doc.createElement("Class-Name")
        xml_class_name_node_content =  doc.createTextNode(node.class_name)
        xml_class_name_node.appendChild(xml_class_name_node_content)
        
        xml_action_node.appendChild(xml_class_name_node)
        
        for parameter in node.parameters:
        
            xml_param_node = doc.createElement("Param")
            xml_param_node.setAttribute("name", parameter.name)
            if not parameter.without_prefix:
                if parameter.is_constant:
                    prefix = "constant:"
                else:
                    prefix = "variable:"
                xml_param_node.setAttribute("value", prefix + parameter.value)
            else:
                xml_param_node.setAttribute("value", parameter.value)
            xml_action_node.appendChild(xml_param_node)
        
                
        xml_process_node.appendChild(xml_name_node)
        xml_process_node.appendChild(xml_action_node)
        
        if len(node.next_node) > 0:
            xml_next_node = doc.createElement("Next-Node")
            xml_next_node_content =  doc.createTextNode(node.next_node)
            xml_next_node.appendChild(xml_next_node_content)
            xml_process_node.appendChild(xml_next_node)
        
        return xml_process_node
        
    def create_xml_pos_and_arrows(self, node):
        doc = Document()
    
        xml_position_node = doc.createElement("Position")
        
        xml_name_node = doc.createElement("Name")
        xml_name_node_content = doc.createTextNode(node.name)
        xml_name_node.appendChild(xml_name_node_content)
        
        xml_x_node = doc.createElement("X")
        xml_x_node_content = doc.createTextNode(node.x)
        xml_x_node.appendChild(xml_x_node_content)
        
        xml_y_node = doc.createElement("Y")
        xml_y_node_content = doc.createTextNode(node.y)
        xml_y_node.appendChild(xml_y_node_content)
        
        xml_width_node = doc.createElement("Width")
        xml_width_node_content = doc.createTextNode(node.width)
        xml_width_node.appendChild(xml_width_node_content)
        
        xml_height_node = doc.createElement("Height")
        xml_height_node_content = doc.createTextNode(node.height)
        xml_height_node.appendChild(xml_height_node_content)
        
           
        xml_position_node.appendChild(xml_name_node)
        xml_position_node.appendChild(xml_x_node)
        xml_position_node.appendChild(xml_y_node)
        xml_position_node.appendChild(xml_width_node)
        xml_position_node.appendChild(xml_height_node)
        
        xml_arrows_node = doc.createElement("Arrows")
        
        xml_name_node = doc.createElement("Name")
        xml_name_node_content = doc.createTextNode(node.name)
        xml_name_node.appendChild(xml_name_node_content)
        
        xml_true_arrow = doc.createElement("True-Arrow")
        
        xml_true_arrow_type = doc.createElement("Type")
        xml_true_arrow_type_content =  doc.createTextNode(node.arrow.type)
        xml_true_arrow_type.appendChild(xml_true_arrow_type_content)
        
        xml_true_arrow_delta_x = doc.createElement("DeltaX")
        xml_true_arrow_type_delta_x_content =  doc.createTextNode(node.arrow.delta_x)
        xml_true_arrow_delta_x.appendChild(xml_true_arrow_type_delta_x_content)
        
        xml_true_arrow_delta_y = doc.createElement("DeltaY")
        xml_true_arrow_type_delta_y_content =  doc.createTextNode(node.arrow.delta_y)
        xml_true_arrow_delta_y.appendChild(xml_true_arrow_type_delta_y_content)
        
        xml_false_arrow = doc.createElement("False-Arrow")
        
        xml_false_arrow_type = doc.createElement("Type")
        xml_false_arrow_type_content =  doc.createTextNode(node.arrow.type)
        xml_false_arrow_type.appendChild(xml_false_arrow_type_content)
        
        xml_false_arrow_delta_x = doc.createElement("DeltaX")
        xml_false_arrow_type_delta_x_content =  doc.createTextNode(node.arrow.delta_x)
        xml_false_arrow_delta_x.appendChild(xml_false_arrow_type_delta_x_content)
        
        xml_false_arrow_delta_y = doc.createElement("DeltaY")
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
        

def test_create():
    #!/usr/bin/env python
    # -*- coding: UTF-8 -*-
    # vim: ai ts=4 sts=4 et sw=4
    
    #create minidom-document
    doc = Document()
    
    # create base element
    base = doc.createElement('Dictionary')
    doc.appendChild(base)
    
    # create an entry element
    entry = doc.createElement('Entry')
    
    # ... and append it to the base element
    base.appendChild(entry)
    
    # create another element 
    german = doc.createElement('German')
    
    # create content
    german_content = doc.createTextNode('Hund')
    
    # append content to element
    german.appendChild(german_content)
    
    # append the german entry to our entry element
    entry.appendChild(german)
    
    # now the same with an english entry
    english = doc.createElement('English')
    english_content = doc.createTextNode('dog')
    english.appendChild(english_content)
    entry.appendChild(english)
    return doc
        

if __name__ == '__main__':
    if  len(sys.argv) == 1:
        print "Incorrect number of parameters"
        print "Launch like this: python WFParser /pathToFile/filename.xml"
    else:
        file_name = sys.argv[1]
        file = open(file_name, 'a+')
        
        
        DOMTree = xml.dom.minidom.parse(file_name)
        #file.write(DOMTree.toxml(encoding='utf-8'))
        #doc = test_create()
        #file.write(doc.toxml(encoding='utf-8'))
        dom_manager = DomManager(DOMTree)
        
        arrow1 = WFNodes.Arrow()
        
        new_process_node = WFNodes.LogNode(name = "logger", x = "100", y = "100", next_node = "Second json setter")
        
        second_node = WFNodes.JsonSetterNode(name = "Second json setter", x = "100", y = "200")
        
        dom_manager.addNode(new_process_node)
        dom_manager.addNode(second_node)
        
        print dom_manager.case_packet_contains("RUNTIME")
        print dom_manager.case_packet_contains("RUNTIME1")
        
        print dom_manager.has_node_name("Getting service instancer from response1")
        print dom_manager.has_node_name("Getting service instancer from response133333")
        print dom_manager.has_node_name("logger")
        
        print dom_manager.is_dom_tree_empty()
        
        dtree = dom_manager.get_dom_tree()
        file.write(dtree.toxml(encoding='utf-8'))
        file.close()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        