#Tag name constants
TAG_NAME_START_NODE = "Start-Node"
TAG_NAME_POSITION = "Position"
TAG_NAME_NAME = "Name"
TAG_NAME_CLASS_NAME = "Class-Name"
TAG_NAME_PROCESS_NODE = "Process-Node"
TAG_NAME_RULE_NODE = "Rule-Node"
TAG_NAME_ACTION = "Action"
TAG_NAME_PARAM = "Param"
TAG_NAME_NEXT_NODE = "Next-Node"
TAG_NAME_CASE_PACKET = "Case-Packet"
TAG_NAME_INIT_CASE_PACKET = "Initial-Case-Packet"
TAG_NAME_CASE_PACKET_VAR = "Variable"
TAG_NAME_INIT_CASE_PACKET_VAR = "Variable-Value"
TAG_NAME_NODES = "Nodes"
TAG_NAME_COORDINATES = "Coordinates"
TAG_NAME_X = "X"
TAG_NAME_Y = "Y"
TAG_NAME_WIDTH = "Width"
TAG_NAME_HEIGHT = "Height"
TAG_NAME_ARROWS = "Arrows"
TAG_NAME_TRUE_ARROW = "True-Arrow"
TAG_NAME_FALSE_ARROW = "False-Arrow"
TAG_NAME_TYPE = "Type"
TAG_NAME_DELTA_X = "DeltaX"
TAG_NAME_DELTA_Y = "DeltaY"

#Attribute name constants
ATTRIBUTE_NAME_NAME = "name"
ATTRIBUTE_NAME_TYPE = "type"
ATTRIBUTE_NAME_VALUE = "value"

#Class name constants
CLASS_NAME_LOG = "com.hp.ov.activator.mwfm.component.builtin.Log"
CLASS_NAME_JSON_SETTER = "ru.deltasolutions.common.activator.mwfm.json.nodes.JsonSetter"
CLASS_NAME_JSON_GETTER = "ru.deltasolutions.common.activator.mwfm.json.nodes.JsonGetter"
CLASS_NAME_AUDIT = "com.hp.ov.activator.mwfm.component.builtin.Audit"
CLASS_NAME_VARIABLE_MAPPER = "com.hp.ov.activator.mwfm.component.builtin.VariableMapper"
CLASS_NAME_GET_PROPERTY = "ru.deltasolutions.common.activator.mwfm.property.nodes.GetProperty"
CLASS_NAME_GET_LOCK = "ru.deltasolutions.common.activator.mwfm.lock.nodes.GetLock"
CLASS_NAME_DO_NOTHING = "com.hp.ov.activator.mwfm.component.builtin.DoNothing"
CLASS_NAME_MAKE_REST_REQUEST = "ru.deltasolutions.common.activator.mwfm.http.nodes.MakeRestRequest"

#Log node constants
LOG_ORDINARY_PARAMS = {"component_name":"variable:WORKFLOW_NAME",
	"log_level":"constant:DEBUG",
	"log_manager":"variable:log_manager",
	"log_message":"Transaction ID=%s (JobId=%s), initiator=%s: ",
	"param0":"variable:transaction_id",
	"param1":"variable:JOB_ID",
	"param2":"variable:transaction_initiator"
	}
LOG_MESSAGE_BEGINING = "Transaction ID=%s (JobId=%s), initiator=%s: "

#Audit node constants
AUDIT_ORDINARY_PARAMS = {"event_type":"constant:MOBILE_PROFILE_DELETE",
    "order_id":"transaction_id",
    "step_name":"constant:TRANSACTION_START",
    "user":"transaction_initiator",
    "attrib_name0":"request_json",
    "attrib_value0":"request_json"
    }

#Set initial values node constants
SET_INITIAL_VALUE_PARAMS = {
    "error_code":"HPSA_WF-001",
    "error_message":"HPSA internal error",
    "log_manager":"%SOLUTION_NAME%_log_manager",
    "property_module":"%SOLUTION_NAME%_property_module"
}

#Get switchyard properties node constants
GET_PROPERTIES_PARAMS = {
    "property_module":"property_module",
    "key0":"constant:sy_protocol",
    "value0":"sy_protocol",
    "key1":"constant:sy_ip_address",
    "value1":"sy_ip_address",
    "key2":"constant:sy_port",
    "value2":"sy_port",
    "key3":"constant:lock_timeout",
    "value3":"lock_timeout"
}

#Create request constants
CREATE_BASE_SY_REQUEST_PARAMS = {
    "output_json":"base_request",
    "path0":"constant:transactionId",
    "value0":"transaction_id",
    "path1":"constant:initiator",
    "value1":"transaction_initiator"
}
CREATE_SY_REQUEST = {
    "input_json":"base_request",
    "output_json":""
}

#Create base response json constants
CREATE_BASE_RESPONSE_JSON_PARAMS = {
    "output_json":"response_json",
    "path0":"constant:errorCode",
    "value0":"error_code",
    "path1":"constant:errorMessage",
    "value1":"error_message"
}

#Get lock constants
GET_LOCK_PARAMS = {
    "lock_storage":"lock_storage",
    "object":"",
    "timeout":""
} 

#Make rest request constants
MAKE_REST_REQUEST_PARAMS = {
    "request_json":"",
    "request_type":"POST",
    "request_url":"",
    "response_code":"http_code",
    "response_json":"get_customer_by_id_response_json"
}

#Setting log params constants
SET_LOG_PARAMS = {
    "composite_name_log":"",
    "request_json_log":"",
    "response_json_log":""
}

#Getting info from response constants
GET_INFO_FROM_RESPONSE_PARAMS = {
    "json_document":"",
    "skip_flag":"constant:true",
    "path0":"errorMessage",
    "value0":"sy_error_message",
    "path1":"errorCode",
    "value1":"sy_error_code"
}
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
