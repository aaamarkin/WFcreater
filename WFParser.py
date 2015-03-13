import WFConstants
import sys, traceback
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.dom.minidom import Document
import WFNodes
from WFNodes import Parameters, Parameter, ProcessNode, RuleNode, SwitchNode, NodeGroup, RestRequestGroup
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
#9 Complete node classes, parse and __init__ to have attributes (persistence and disable)
#10 Modify SwitchNode constructor
#11 Modify RuleNode constructor
#12 Construct more effective tree model from DomTree
#13 Move xml methods to Handlers
#14 Change empty string class fields to None
#15 HasAnyNodes WF method
#16 Check for type field in parameter

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

    def getStartNodeName(self):
        name = None
        start_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_START_NODE)
        if len(start_nodes) > 0:
            name = start_nodes[0].childNodes[0].data
        return name

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

        return self.getNode(node_name) is not None

    def getNode(self, node_name):
        xml_node = None
        if self.getWFName() != node_name:

            process_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_PROCESS_NODE)

            for node in process_nodes:
                exist_node_name = node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
                if exist_node_name == node_name:
                    xml_node = node

                    name_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME)
                    for name_node in name_nodes:
                        if name_node.firstChild.nodeValue == node_name \
                            and name_node.parentNode.nodeName == WFConstants.TAG_NAME_POSITION:
                            xml_position = name_node.parentNode
                        if name_node.firstChild.nodeValue == node_name \
                            and name_node.parentNode.nodeName == WFConstants.TAG_NAME_ARROWS:
                            xml_arrows = name_node.parentNode

                    return ProcessNode(xml_node=xml_node, xml_position=xml_position, xml_arrows=xml_arrows)

            rule_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_RULE_NODE)

            for node in rule_nodes:
                exist_node_name = node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
                if exist_node_name == node_name:
                    xml_node = node

                    name_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME)
                    for name_node in name_nodes:
                        if name_node.firstChild.nodeValue == node_name \
                                and name_node.parentNode.nodeName == WFConstants.TAG_NAME_POSITION:
                            xml_position = name_node.parentNode
                        if name_node.firstChild.nodeValue == node_name \
                                and name_node.parentNode.nodeName == WFConstants.TAG_NAME_ARROWS:
                            xml_arrows = name_node.parentNode

                    return RuleNode(xml_node=xml_node, xml_position=xml_position, xml_arrows=xml_arrows)

            switch_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_SWITCH_NODE)

            for node in switch_nodes:
                exist_node_name = node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
                if exist_node_name == node_name:
                    xml_node = node

                    name_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME)
                    for name_node in name_nodes:
                        if name_node.firstChild.nodeValue == node_name \
                                and name_node.parentNode.nodeName == WFConstants.TAG_NAME_POSITION:
                            xml_position = name_node.parentNode
                        if name_node.firstChild.nodeValue == node_name \
                                and name_node.parentNode.nodeName == WFConstants.TAG_NAME_ARROWS:
                            xml_arrows = name_node.parentNode

                    return SwitchNode(xml_node=xml_node, xml_position=xml_position, xml_arrows=xml_arrows)

        return xml_node

    def getAllNodesNodeGroupTest(self):
        allNodes = NodeGroup()
        node_queue = []
        previous_nodes_queue = [""]
        start_node_name = self.getStartNodeName()
        if start_node_name is None:
            temp = self.collection.getElementsByTagName(WFConstants.TAG_NAME_PROCESS_NODE)
            start_node_name = temp[0].getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data
        node_queue.append(start_node_name)

        while len(node_queue) > 0:

            current_name = node_queue.pop()

            if not allNodes.contains(current_name):
                current_node = self.getNode(current_name)

                allNodes.injectNode(current_node, from_node_name=previous_nodes_queue.pop())
                #current_node.previous_node_names.append(previous_nodes_queue.pop())
                if isinstance(current_node, ProcessNode):
                    if len(current_node.next_node) > 0:
                        node_queue.append(current_node.next_node)
                    previous_nodes_queue.append(current_node.name)
                elif isinstance(current_node, RuleNode):
                    if len(current_node.next_node_false) > 0:
                        node_queue.append(current_node.next_node_false)
                    previous_nodes_queue.append(current_node.name)
                    if len(current_node.next_node_true) > 0:
                        node_queue.append(current_node.next_node_true)
                    previous_nodes_queue.append(current_node.name)

                elif isinstance(current_node, SwitchNode):
                    for case_node_name in current_node.next_node_cases.values():
                        if len(case_node_name) > 0:
                            node_queue.append(case_node_name)
                        previous_nodes_queue.append(current_node.name)
                        if len(current_node.next_node_default) > 0:
                            node_queue.append(current_node.next_node_default)
                        previous_nodes_queue.append(current_node.name)


                self.removeNode(current_name)



    def getAllNodesNodeGroup(self):
        allNodes = NodeGroup()

        process_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_PROCESS_NODE)

        for new_process_node in process_nodes:
            new_process_node_name = new_process_node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data

            name_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME)
            for name_node in name_nodes:
                if name_node.firstChild.nodeValue == new_process_node_name \
                        and name_node.parentNode.nodeName == WFConstants.TAG_NAME_POSITION:
                    xml_position = name_node.parentNode

                elif name_node.firstChild.nodeValue == new_process_node_name \
                        and name_node.parentNode.nodeName == WFConstants.TAG_NAME_ARROWS:
                    xml_arrows = name_node.parentNode

            new_node = ProcessNode(xml_node=new_process_node, xml_position=xml_position, xml_arrows=xml_arrows)
            allNodes.injectNode(new_node, from_node_name="")
            removed = xml_position.parentNode.removeChild(xml_position)
            removed.unlink()
            removed = xml_arrows.parentNode.removeChild(xml_arrows)
            removed.unlink()
            removed = new_process_node.parentNode.removeChild(new_process_node)
            removed.unlink()

        rule_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_RULE_NODE)

        for new_rule_node in rule_nodes:
            new_rule_node_name = new_rule_node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data

            name_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME)
            for name_node in name_nodes:
                if name_node.firstChild.nodeValue == new_rule_node_name \
                        and name_node.parentNode.nodeName == WFConstants.TAG_NAME_POSITION:
                    xml_position = name_node.parentNode

                elif name_node.firstChild.nodeValue == new_rule_node_name \
                        and name_node.parentNode.nodeName == WFConstants.TAG_NAME_ARROWS:
                    xml_arrows = name_node.parentNode

            new_node = RuleNode(xml_node=new_rule_node, xml_position=xml_position, xml_arrows=xml_arrows)
            allNodes.injectNode(new_node, from_node_name="")
            removed = xml_position.parentNode.removeChild(xml_position)
            removed.unlink()
            removed = xml_arrows.parentNode.removeChild(xml_arrows)
            removed.unlink()
            removed = new_rule_node.parentNode.removeChild(new_rule_node)
            removed.unlink()

        switch_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_SWITCH_NODE)

        for new_switch_node in switch_nodes:
            new_switch_node_name = new_switch_node.getElementsByTagName(WFConstants.TAG_NAME_NAME)[0].childNodes[0].data

            name_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NAME)
            for name_node in name_nodes:
                if name_node.firstChild.nodeValue == new_switch_node_name \
                        and name_node.parentNode.nodeName == WFConstants.TAG_NAME_POSITION:
                    xml_position = name_node.parentNode

                elif name_node.firstChild.nodeValue == new_switch_node_name \
                        and name_node.parentNode.nodeName == WFConstants.TAG_NAME_ARROWS:
                    xml_arrows = name_node.parentNode

            new_node = SwitchNode(xml_node=new_switch_node, xml_position=xml_position, xml_arrows=xml_arrows)
            allNodes.injectNode(new_node, from_node_name="")
            removed = xml_position.parentNode.removeChild(xml_position)
            removed.unlink()
            removed = xml_arrows.parentNode.removeChild(xml_arrows)
            removed.unlink()
            removed = new_switch_node.parentNode.removeChild(new_switch_node)
            removed.unlink()

        return allNodes

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
        for node in node_group:
            self.addNode(node)
        for ex_node_group in node_group.node_group_list:
            for node in ex_node_group:
                self.addNode(node)


    def addHandler(self, handler):

        handler_to_add = self.createXmlHandler(handler)

        case_packet = self.collection.getElementsByTagName(WFConstants.TAG_NAME_CASE_PACKET)[0]
        self.collection.insertBefore(handler_to_add, case_packet)

    def addNode(self, node):
        if self.hasNodeName(node.name):
            raise DuplicateNodeError(node.name)
        else:
            all_nodes = self.collection.getElementsByTagName(WFConstants.TAG_NAME_NODES)[0]
            all_nodes.appendChild(node.createXmlNode())

            coordinates = self.collection.getElementsByTagName(WFConstants.TAG_NAME_COORDINATES)[0]

            coordinates.appendChild(node.arrowsToXml())

            arrows = self.collection.getElementsByTagName(WFConstants.TAG_NAME_ARROWS)[0]
            coordinates.insertBefore(node.positionToXml(), arrows)


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

        #dom_manager.addNodeTest(rule_node)
        #dom_manager.addNode(rule_node)
        node_test_group = dom_manager.getAllNodesNodeGroupTest()
        #dom_manager.removeNextNodeReferences('Init params')
        #dom_manager.removeNode('call getCustomerById11')
        #dom_manager.addNode(new_process_node)
        #dom_manager.addNodeGroup(node_test_group)
        for node in node_test_group:
            previousNodes = []
            if node.class_name == WFConstants.CLASS_NAME_MAKE_REST_REQUEST:
                http_false_node_list = []
                sy_false_node_list = []
                nodes_to_delete_list = []
                nodes_to_delete_list.append(node.name)
                rest_previous_nodes = node.previous_node_names
                rest__name = node.name
                rest_url = node.parameters.getValue('request_url')
                rest_request = node.parameters.getValue('request_json')
                rest_response = node.parameters.getValue('response_json')
                http_check_node = node_test_group.getNode(node.next_node)
                nodes_to_delete_list.append(http_check_node.name)
                if not isinstance(http_check_node, RuleNode):
                    print 'Expected http check node'
                http_check_false = node_test_group.getNode(http_check_node.next_node_false)
                http_check_true = node_test_group.getNode(http_check_node.next_node_true)
                http_false_node_list.append(http_check_false.name)
                nodes_to_delete_list.append(http_check_false.name)
                while http_check_false.class_name != WFConstants.CLASS_NAME_VARIABLE_MAPPER:
                    http_check_false = node_test_group.getNode(http_check_false.next_node)
                    http_false_node_list.append(http_check_false.name)
                    nodes_to_delete_list.append(http_check_false.name)
                http_false_node_list.append(http_check_false.name)
                while http_check_true.class_name != WFConstants.CLASS_NAME_JSON_GETTER:
                    if http_check_true.class_name != WFConstants.CLASS_NAME_JSON_GETTER:
                        print "Alarm not getter"
                    http_check_true = node_test_group.getNode(http_check_true.next_node)
                    nodes_to_delete_list.append(http_check_false.name)
                getter_node = http_check_true
                getter_params_dict = {}
                for parameter in getter_node.parameters:
                    if 'path' in parameter.name:
                        if parameter.value == 'errorCode':
                            error_code_var = getter_params.getValue('value' + parameter.name[-1])
                        elif parameter.value == 'errorMessage':
                            error_message_var = getter_params.getValue('value' + parameter.name[-1])
                        else:
                            getter_params_dict[parameter.value] = getter_params.getValue('value' + parameter.name[-1])

                sy_check_node = node_test_group.getNode(getter_node.next_node)
                nodes_to_delete_list.append(sy_check_node.name)
                if not isinstance(sy_check, RuleNode):
                    print 'Expected sy check node'
                sy_check_false = node_test_group.getNode(sy_check_node.next_node_false)
                sy_check_true = node_test_group.getNode(sy_check_node.next_node_true)
                sy_false_node_list.append(sy_check_false.name)
                nodes_to_delete_list.append(sy_check_false.name)
                while sy_check_false.class_name != WFConstants.CLASS_NAME_VARIABLE_MAPPER:
                    sy_check_false = node_test_group.getNode(sy_check_false.next_node)
                    sy_false_node_list.append(sy_check_false.name)
                    nodes_to_delete_list.append(sy_check_false.name)
                sy_false_node_list.append(sy_false_node_list.name)

                if sy_check_true.class_name == WFConstants.CLASS_NAME_LOG:
                    sy_check_true = sy_check_true.next_node

                    if sy_check_true.class_name == WFConstants.CLASS_NAME_JSON_GETTER:








        dom_manager.overwrightOriginalFile()
        try:
            #print node_test
            #dom_manager.addNodeGroup(restGroup)
            #dom_manager.removeNextNodeReferences("logger")
            #dom_manager.removeNode("Default_WF")


            #dom_manager.renameWF("Renamed_WF")

            #dom_manager.overwrightOriginalFile()

        except Exception as e:
            print e



































