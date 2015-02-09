import WFVariables

#Tag name constants
TAG_NAME_START_NODE = "Start-Node"
TAG_NAME_POSITION = "Position"
TAG_NAME_NAME = "Name"
TAG_NAME_CLASS_NAME = "Class-Name"
TAG_NAME_PROCESS_NODE = "Process-Node"
TAG_NAME_RULE_NODE = "Rule-Node"
TAG_NAME_SWITCH_NODE = "Switch-Node"
TAG_NAME_ACTION = "Action"
TAG_NAME_PARAM = "Param"
TAG_NAME_NEXT_NODE = "Next-Node"
TAG_NAME_NEXT_NODE_TRUE = "True-Next-Node"
TAG_NAME_NEXT_NODE_FALSE = "False-Next-Node"
TAG_NAME_SWITCH = "Switch"
TAG_NAME_DEFAULT = "Default"
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
TAG_NAME_SWITCH_ARROW = "Switch-Arrow"
TAG_NAME_DEFAULT_ARROW = "Default-Arrow"
TAG_NAME_CASE_ARROW = "Case-Arrow"
TAG_NAME_TYPE = "Type"
TAG_NAME_DELTA_X = "DeltaX"
TAG_NAME_DELTA_Y = "DeltaY"
TAG_NAME_END_HANDLER = "End-Handler"

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
CLASS_NAME_MAKE_REST_REQUEST_SWITCH = "ru.deltasolutions.common.activator.mwfm.http.nodes.MakeRestRequestSwitch"
CLASS_NAME_EQUALS = "com.hp.ov.activator.mwfm.component.builtin.Equal"
CLASS_NAME_LOG_HANDLER = "ru.deltasolutions.common.activator.mwfm.log.handlers.LogHandler"
CLASS_NAME_SYNC_HANDLER = "com.hp.ov.activator.mwfm.component.builtin.SyncHandler"
CLASS_NAME_RELEASE_LOCK_HANDLER = "ru.deltasolutions.common.activator.mwfm.lock.handlers.ReleaseLocksHandler"
CLASS_NAME_AUDIT_HANDLER = "ru.deltasolutions.common.activator.mwfm.audit.handlers.AuditHandler"

#Handler names
SYNC_HANDLER_NAME = "SyncHandler"
AUDIT_HANDLER_NAME = "AuditHandler"
LOG_HANDLER = "LogHandler"
RELEASE_LOCK_HANDLER = "ReleaseLocksHandler"

#Handler constants
LOG_HANDLER_PARAMS = {
    "component_name":"variable:WORKFLOW_NAME",
    "log_level":"INFORMATIVE",
    "log_manager":"variable:log_manager",
    "log_message":"TransactionID=%s (JobID=%s), initiator=%s:",
    "param0":"variable:transaction_id",
    "param1":"variable:JOB_ID",
    "param2":"variable:transaction_initiator",
    "param3":"variable:error_code",
    "param4":"variable:error_message"
}
AUDIT_HANDLER_PARAMS = {
    "event_type":"constant:TRANSACTION_END",
    "identifier":"",
    "order_id":"variable:transaction_id",
    "attrib_name0":"response_json",
    "attrib_value0":"variable:response_json"
}
SYNC_HANDLER_PARAMS = {
    "job_id":"parent_job_id",
    "queue":"constant:sync",
    "destination0":"child_error_code",
    "variable0":"variable:error_code",
    "destination1":"child_error_message",
    "variable1":"variable:error_message",
    "destination2":"lock_storage",
    "variable2":"variable:lock_storage"
}
RELEASE_LOCK_HANDLER_PARAMS = {
    "lock_storage":"lock_storage",
    "log_manager":"log_manager"
}

#Log node constants
LOG_ORDINARY_PARAMS = {
    "component_name":"variable:WORKFLOW_NAME",
	"log_level":"constant:DEBUG",
	"log_manager":"variable:log_manager",
	"log_message":"Transaction ID=%s (JobId=%s), initiator=%s: ",
	"param0":"variable:transaction_id",
	"param1":"variable:JOB_ID",
	"param2":"variable:transaction_initiator"
	}
REST_RESULTS_LOG_PARAMS = {
    "component_name":"variable:WORKFLOW_NAME",
    "log_level":"DEBUG",
    "log_manager":"variable:log_manager",
    "log_message":"Transaction ID=%s (JobId=%s), initiator=%s: Rest request: %s. Rest response :%s.",
    "param0":"variable:transaction_id",
    "param1":"variable:JOB_ID",
    "param2":"variable:transaction_initiator",
    "param3":"variable:request_json_log",
    "param4":"variable:response_json_log"
}
LOG_MESSAGE_BEGINING = "Transaction ID=%s (JobId=%s), initiator=%s: "

#Audit node constants
AUDIT_ORDINARY_PARAMS = {
    "event_type":"constant:",
    "order_id":"variable:transaction_id",
    "step_name":"constant:TRANSACTION_START",
    "user":"variable:transaction_initiator",
    "attrib_name0":"variable:request_json",
    "attrib_value0":"variable:request_json"
    }

#Set initial values node constants
SET_INITIAL_VALUE_PARAMS = {
    "error_code":"HPSA_WF-001",
    "error_message":"HPSA internal error",
    "log_manager":"%SOLUTION_NAME%_log_manager",
    "property_module":"%SOLUTION_NAME%_property_module"
}

#Get switchyard properties node constants
value_protocol = "variable:" + WFVariables.VARIABLE_NAME_SY_PROTOCOL
value_ip = "variable:" + WFVariables.VARIABLE_NAME_SY_IP
value_port = "variable:" + WFVariables.VARIABLE_NAME_SY_PORT
value_timeout = "variable:" + WFVariables.VARIABLE_NAME_LOCK_TIME
GET_PROPERTIES_PARAMS = {
    "property_module":"variable:property_module",
    "key0":"constant:sy_protocol",
    "value0":value_protocol,
    "key1":"constant:sy_ip_address",
    "value1":value_ip,
    "key2":"constant:sy_port",
    "value2":value_port,
    "key3":"constant:lock_timeout",
    "value3":value_timeout
}

#Create request constants
CREATE_BASE_SY_REQUEST_PARAMS = {
    "output_json":"variable:base_request",
    "path0":"constant:transactionId",
    "value0":"variable:transaction_id",
    "path1":"constant:initiator",
    "value1":"variable:transaction_initiator"
}
CREATE_SY_REQUEST = {
    "input_json":"variable:base_request",
    "output_json":""
}

#Create base response json constants
CREATE_BASE_RESPONSE_JSON_PARAMS = {
    "output_json":"variable:response_json",
    "path0":"constant:errorCode",
    "value0":"variable:error_code",
    "path1":"constant:errorMessage",
    "value1":"variable:error_message"
}

#Get lock constants
GET_LOCK_PARAMS = {
    "lock_storage":"variable:lock_storage",
    "object":"",
    "timeout":""
} 

#Make rest request constants
MAKE_REST_REQUEST_PARAMS = {
    "request_json":"",
    "request_type":"constant:POST",
    "request_url":"",
    "response_code":"variable:http_code",
    "response_json":""
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
    "path0":"constant:errorMessage",
    "value0":"variable:sy_error_message",
    "path1":"constant:errorCode",
    "value1":"variable:sy_error_code"
}
    
#Equals constants
EQUALS_PARAMS = {
    "op1":"",
    "op2":""
}
    
    
    
# Base WF string
BASE_WF = '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE Workflow  SYSTEM "workflow.dtd"><Workflow Init-On-Startup="false" Unique="false" auditEnabled="true" autoAuditEnabled="true" disablePersistence="false" statEnabled="true"><Name>Default_WF</Name><Solution>Default_WF_solution</Solution><Start-Node/><Nodes/><Case-Packet><Variable name="BREAK_POINT" type="String"/><Variable name="DEFAULT_ROLE" type="String"/><Variable name="EMPTY_STRING" type="String"/><Variable name="ETC" type="String"/><Variable name="EX_STEP_NAME" type="String"/><Variable name="FILE_URL_PREFIX" type="String"/><Variable name="HOST_NAME" type="String"/><Variable name="JOB_ID" type="Integer"/><Variable name="KILL_ROLE" type="String"/><Variable name="MASTER_CHILD_JOBS" type="Object"/><Variable name="NULL" type="Object"/><Variable name="PRIORITY" type="Integer"/><Variable name="RESERVATIONS" type="Object"/><Variable name="RET_TEXT" type="String"/><Variable name="RET_VALUE" type="Integer"/><Variable name="RUNTIME" type="Object"/><Variable name="SCHEDULED_INFO" type="Object"/><Variable name="SERVICE_ID" type="String"/><Variable name="SOLUTION_ETC" type="String"/><Variable name="SOLUTION_NAME" type="String"/><Variable name="SOLUTION_VAR" type="String"/><Variable name="START_ROLE" type="String"/><Variable name="START_TIME" type="Integer"/><Variable name="STATUS" type="String"/><Variable name="STEP_NAME" type="String"/><Variable name="SUBSTEP" type="String"/><Variable name="THROW_EXCEP" type="Boolean"/><Variable name="TIMEOUT" type="Boolean"/><Variable name="TRACE_ROLE" type="String"/><Variable name="UNIQUE_WORKFLOW" type="Integer"/><Variable name="VAR" type="String"/><Variable name="WORKFLOW_EXCEPTION" type="Object"/><Variable name="WORKFLOW_EXECUTION_STATUS" type="String"/><Variable name="WORKFLOW_NAME" type="String"/><Variable name="WORKFLOW_ORDER_ID" type="String"/><Variable name="WORKFLOW_STATE" type="String"/><Variable name="WORKFLOW_TYPE" type="String"/><Variable name="WORKFLOW_VERSION" type="Integer"/><Variable name="activation_description" type="String"/><Variable name="activation_major_code" type="Integer"/><Variable name="activation_minor_code" type="Integer"/><Variable name="message_url" type="String"/><Variable name="module_name" type="String"/><Variable name="skip_activation" type="Boolean"/></Case-Packet><Initial-Case-Packet><Variable-Value name="FILE_URL_PREFIX" value="file:///"/><Variable-Value name="SOLUTION_NAME" value="Default_WF_solution"/><Variable-Value name="WORKFLOW_NAME" value="Default_WF"/><Variable-Value name="WORKFLOW_VERSION" value="-1"/></Initial-Case-Packet><Coordinates></Coordinates></Workflow>'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
