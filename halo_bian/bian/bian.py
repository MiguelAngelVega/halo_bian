#!/usr/bin/env python
import logging
from abc import ABCMeta

from halo_flask.classes import AbsBaseClass
from halo_flask.request import HaloRequest
from halo_flask.response import HaloResponse
from halo_flask.settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)


#extension,anlytics,cloud

class BianRequest(HaloRequest):
    action_term = None
    sd_reference_id = None
    cr_reference_id = None
    bq_reference_id = None
    behavior_qualifier = None
    collection_filter = None
    query_params = None
    sub_qualifiers = None
    context = None

    def __init__(self, action_term, request,context, sd_reference_id=None,cr_reference_id=None, bq_reference_id=None, behavior_qualifier=None,collection_filter=None,query_params=None,sub_qualifiers=None):
        self.action_term = action_term
        self.request = request
        self.sd_reference_id = sd_reference_id
        self.cr_reference_id = cr_reference_id
        self.behavior_qualifier = behavior_qualifier
        self.bq_reference_id = bq_reference_id
        self.collection_filter = collection_filter
        self.query_params = query_params
        self.sub_qualifiers = sub_qualifiers
        self.context = context
        self.sub_func = self.get_bq_func_name()

    def get_bq_func_name(self):
        if self.behavior_qualifier:
            name = self.behavior_qualifier.lower()
            if self.sub_qualifiers:
                for item in self.sub_qualifiers.keys():
                    name = name + "_" + item.lower()
            return name
        return None


class BianResponse(HaloResponse):
    request = None

    def __init__(self, bian_request, payload=None, headers=None):
        self.request = bian_request
        self.payload = payload
        self.headers = headers


class ServiceProperties(AbsBaseClass):
    status = "online"
    props = []

    def get_status(self):
        return self.status

    def get_props(self):
        return self.props


class AssetType(AbsBaseClass):
    __metaclass__ = ABCMeta
    ASSET_TYPE = None

    def get_asset_type(self):
        return self.ASSET_TYPE


class GenericArtifact(AbsBaseClass):
    __metaclass__ = ABCMeta
    GENERIC_ARTIFACT_TYPE = None
    behavior_qualifier_type = None

    def __init__(self, behavior_qualifier_type=None):
        self.behavior_qualifier_type = behavior_qualifier_type

    def get_generic_artifact_type(self):
        return self.GENERIC_ARTIFACT_TYPE

class BehaviorQualifier(AbsBaseClass):
    #behavior_qualifier = None
    sub_qualifiers = None
    qualifiers_depth = 1

    def __init__(self, name,sub_qualifiers=None):
        self.name = name
        if sub_qualifiers:
            self.sub_qualifiers = sub_qualifiers
            self.qualifiers_depth = self.get_qualifiers_depth(sub_qualifiers,self.qualifiers_depth)
            logger.debug("in BehaviorQualifier " + str(name) + " qualifiers_depth=" + str(self.qualifiers_depth))

    def get_qualifiers_depth(self,sub_qualifiers,the_depth):
        depth = the_depth + 1
        if sub_qualifiers:
            for key in sub_qualifiers:
                map = sub_qualifiers[key]
                subs = map["subs"]
                if subs:
                    d = self.get_qualifiers_depth(subs,depth)
                    if d > depth:
                        depth = d
        return depth



class BehaviorQualifierType(AbsBaseClass):
    __metaclass__ = ABCMeta
    BEHAVIOR_QUALIFIER_TYPE = None
    dict = {}

    def __init__(self, dict, sub_qualifiers=None):
        for key in dict:
            map = None
            if sub_qualifiers:
                if key in sub_qualifiers:
                    map = sub_qualifiers[key]
            self.dict[key] = BehaviorQualifier(dict[key].strip().replace("-", "_").replace(" ", "_"),map)

    def get_behavior_qualifier_type(self):
        return self.BEHAVIOR_QUALIFIER_TYPE

    def get(self, key):
        return self.dict[key]

    def put(self, key, value):
        self.dict[key] = value

    def keys(self):
        return self.dict.keys()

#Define Business Events for the Service Domains – four established BIAN categories are used to classify the business events:
#a. Origination – results in a new control record instance
#b. Invocation – acts on an active control record instance
#c. Reporting – provides information about one or more active instances
#d. Delegation – results in service calls to other Service Domains

class BianCategory(AbsBaseClass):
    ORIGINATION = "Origination"
    INVOCATION = "Invocation"
    REPORTING = "Reporting"
    DELEGATION = "Delegation"
    SETUP = "Setup"

class LifeCycleState(AbsBaseClass):
    state = None
    actions = []
    states = None

    def __init__(self, state,states,actions=[]):
        self.state = state
        self.actions = actions
        self.states = states

    def allows(self,action_term):
        if action_term in self.actions:
            return True
        return False

class LifeCycleStates(AbsBaseClass):
    __metaclass__ = ABCMeta

    states = []

    def __init__(self, states):
        self.states = states


class DirectLifeCycleStates(LifeCycleStates):
    #Unassigned Assigned-strategy-pending Strategy-in-force Strategy-under-review Strategy-suspended Strategy-concluded

    def __init__(self, state_name):
        self.Unassigned = LifeCycleState("Unassigned", self)
        self.Assigned_strategy_pending = LifeCycleState("Assigned-strategy-pending",self)
        self.Strategy_in_force = LifeCycleState("Strategy-in-force",self)
        self.Strategy_under_review = LifeCycleState("Strategy-under-review",self)
        self.Strategy_suspended = LifeCycleState("Strategy-suspended",self)
        self.Strategy_concluded = LifeCycleState("Strategy-concluded",self)
        super(DirectLifeCycleStates,self).__init__([self.Unassigned,self.Assigned_strategy_pending,self.Strategy_in_force,self.Strategy_under_review,self.Strategy_suspended,self.Strategy_concluded])

#@todo check control record good - behavior_qualifier_type
class ControlRecord(GenericArtifact):
    __metaclass__ = ABCMeta
    asset_type = None
    life_cycle_state = None

    def __init__1(self, asset_type, generic_artifact, behavior_qualifier_type,life_cycle_state):
        self.asset_type = asset_type
        #self.generic_artifact = generic_artifact
        self.behavior_qualifier_type = behavior_qualifier_type
        self.life_cycle_state = life_cycle_state

    def get_asset_type(self):
        return self.asset_type.get_asset_type()

    def get_generic_artifact_type(self):
        return self.generic_artifact.get_generic_artifact_type()

    def get_behavior_qualifier_type(self):
        self.behavior_qualifier_type.get_behavior_qualifier_type()

    def get_asset_type_obj(self):
        return self.asset_type

    def get_generic_artifact(self):
        return self.generic_artifact

    def get_behavior_qualifier(self):
        self.behavior_qualifier_type

    def get_life_cycle_state(self):
        self.life_cycle_state

    def validate_action(self,action_term):
        if self.life_cycle_state.allows(action_term):
            return True
        return False


class BianServiceInfo(AbsBaseClass):
    # A Service Domain is a combination of a Functional Pattern and an Asset Type

    # The BIAN service domain name
    service_domain = None
    # The BIAN asset type managed by the service
    asset_type = "undefined"
    # The BIAN functional pattern of the service
    functional_pattern = None
    # The BIAN generic artifiact type of the service domain control record
    generic_artifact = "undefined"
    # The BIAN behavior qualifier type for the service
    behavior_qualifier_type = "undefined"
    # The control record name used by the service to track state
    control_record = "undefined"

    def __init__(self, service_domain, asset_type, functional_pattern, generic_artifact, behavior_qualifier_type):
        self.service_domain = service_domain
        self.asset_type = asset_type
        self.functional_pattern = functional_pattern
        self.generic_artifact = generic_artifact
        self.control_record = asset_type + generic_artifact
        self.behavior_qualifier_type = behavior_qualifier_type

    def __init__1(self, service_domain, functional_pattern, control_record_obj):
        self.service_domain = service_domain
        self.functional_pattern = functional_pattern
        if control_record_obj:
            self.asset_type = control_record_obj.get_asset_type()
            self.generic_artifact = control_record_obj.get_generic_artifact()
            self.control_record = self.asset_type + self.generic_artifact
            self.behavior_qualifier_type = control_record_obj.get_behavior_qualifier_type()

    def get_service_domain(self):
        return self.service_domain

    def get_asset_type(self):
        return self.asset_type

    def get_functional_pattern(self):
        return self.functional_pattern

    def get_generic_artifact(self):
        return self.generic_artifact

    def get_behavior_qualifier_type(self):
        return self.behavior_qualifier_type

    def get_control_record(self):
        return self.control_record


# Service Operations - action terms v2
class ActionTerms(AbsBaseClass):
    INITIATE = 'INITIATE'
    CREATE = 'CREATE'
    ACTIVATE = 'ACTIVATE'
    CONFIGURE = 'CONFIGURE'
    UPDATE = 'UPDATE'
    REGISTER = 'REGISTER'
    #RECORD = 'RECORD'
    EXECUTE = 'EXECUTE'
    EVALUATE = 'EVALUATE'
    PROVIDE = 'PROVIDE'
    #AUTHORIZE = 'AUTHORIZE'
    REQUEST = 'REQUEST'
    #TERMINATE = 'TERMINATE'
    NOTIFY = 'NOTIFY'
    RETRIEVE = 'RETRIEVE',
    #new
    CAPTURE = 'CAPTURE',
    CONTROL = 'CONTROL',
    EXCHANGE = 'EXCHANGE',
    GRANT = 'GRANT',
    FEEDBACK = 'FEEDBACK'

    ops = [
        INITIATE,
        CREATE,
        ACTIVATE,
        CONFIGURE,
        UPDATE,
        REGISTER,
        #RECORD,
        EXECUTE,
        EVALUATE,
        PROVIDE,
        #AUTHORIZE,
        REQUEST,
        #TERMINATE,
        NOTIFY,
        RETRIEVE,
        CAPTURE,
        CONTROL,
        EXCHANGE,
        GRANT,
        FEEDBACK
    ]
    categories = {

        CREATE: BianCategory.ORIGINATION,
        EVALUATE: BianCategory.ORIGINATION,
        INITIATE: BianCategory.ORIGINATION,
        PROVIDE: BianCategory.ORIGINATION,
        REGISTER: BianCategory.ORIGINATION,

        CAPTURE: BianCategory.INVOCATION,
        CONTROL: BianCategory.INVOCATION,
        EXCHANGE: BianCategory.INVOCATION,
        EXECUTE: BianCategory.INVOCATION,
        GRANT: BianCategory.INVOCATION,
        REQUEST: BianCategory.INVOCATION,
        UPDATE: BianCategory.INVOCATION,

        NOTIFY: BianCategory.REPORTING,
        RETRIEVE: BianCategory.REPORTING,

        ACTIVATE: BianCategory.SETUP,
        CONFIGURE: BianCategory.SETUP,
        FEEDBACK: BianCategory.SETUP

    }


        #RECORD: BianCategory.INVOCATION,
        #AUTHORIZE: BianCategory.INVOCATION,
        #TERMINATE: BianCategory.INVOCATION,

# BehaviorQualifiers v2
class Aspect(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Aspect"


class Algorithm(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Algorithm"


class Assignment(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Assignment"


class Clause(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Clause"


class Deliverable(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Deliverable"


class Duty(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Duty"


class Event(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Event"


class Feature(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Feature"


class Function(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Function"


class Goal(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Goal"


class Property(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Property"


class Routine(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Routine"


class Signal(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Signal"


class Step(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Step"


class Task(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Task"


class Term(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Term"


class Test(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Test"


class Workstep(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Workstep"


class Advise(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Advise"


# Generic Artifacts v2
class AdministrativePlan(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "AdministrativePlan"


class Allocation(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Allocation"


class Agreement(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Agreement"


class Analysis(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Analysis"


class Assessment(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Assessment"


class DevelopmentProject(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "DevelopmentProject"


class Directory(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Directory"


class FulfillmentArrangement(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "FulfillmentArrangement"


class Log(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Log"


class MaintenanceAgreement(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "MaintenanceAgreement"


class ManagementPlan(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "ManagementPlan"


class Measurement(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Measurement"


class Membership(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Membership"


class OperatingSession(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "OperatingSession"


class Procedure(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Procedure"


class Specification(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Specification"


class Strategy(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Strategy"


class Transaction(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Transaction"


class Advice(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Advice"


# Functional Patterns v2
class FunctionalPatterns(AbsBaseClass):
    #create
    ADMINISTER = 'Administer'
    DIRECT = 'Direct'
    MANAGE = 'Manage'
    DESIGN = 'Design'
    DEVELOP = 'Develop'
    #initiate
    PROCESS = 'Process'
    OPERATE = 'Operate'
    MAINTAIN = 'Maintain'
    FULFILL = 'Fulfill'
    TRANSACT = 'Transact'
    ADVISE = 'Advise',
    TRACK = 'Track'
    MONITOR = 'Monitor'
    #register
    ENROLL = 'Enroll'
    CATALOG = 'Catalog'
    #evaluate
    AGREETERMS = 'Agree Terms'
    ANALYZE = 'Analyze'
    ASSESS = 'Assess'
    #provide
    ALLOCATE = 'Allocate'

    # Functional Pattern ==> Generic Artifact Type ==> Behavior Qualifier
    # pattern : [Generic Artifact,Behavior Qualifier Type]
    patterns = {
        ADMINISTER: ['AdministrativePlan', 'Routine'],#
        AGREETERMS: ['Agreement', 'Term'],#
        ALLOCATE: ['Allocation', 'Criteria'],#
        ANALYZE: ['Analysis', 'Algorithm'],#
        ASSESS: ['Assessment', 'Test'],#
        DESIGN: ['Specification', 'Aspect'],#
        DEVELOP: ['DevelopmentProject', 'Deliverable'],#
        DIRECT: ['Strategy', 'Goal'],#
        MAINTAIN: ['MaintenanceAgreement', 'Task'],#
        MANAGE: ['ManagementPlan', 'Duty'],#
        CATALOG: ['DirectoryEntry', 'Property'],#
        TRACK: ['Log', 'Event'],#
        MONITOR: ['State', 'Measure'],#
        OPERATE: ['OperatingSession', 'Function'],#
        FULFILL: ['FulfillmentArrangement', 'Feature'],#
        TRANSACT: ['Transaction', 'Step'],
        ENROLL: ['Membership', 'Clause'],#
        PROCESS: ['Procedure', 'Workstep'],#
        ADVISE: ['Advice', 'Topic'],#
    }

    # action terms allowed for functional pattern
    # pattern : [action terms]
    operations = {
        ADMINISTER: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.CONTROL,ActionTerms.GRANT,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        AGREETERMS: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.GRANT,ActionTerms.EVALUATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        ALLOCATE: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.CAPTURE,ActionTerms.PROVIDE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE],#
        ANALYZE: [ActionTerms.EVALUATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.EXECUTE,ActionTerms.REQUEST],#
        ASSESS: [ActionTerms.EXCHANGE, ActionTerms.GRANT,ActionTerms.EVALUATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.EXECUTE,ActionTerms.REQUEST],#
        DESIGN: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.CONTROL,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        DEVELOP: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.CONTROL,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        DIRECT: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.GRANT,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.REQUEST],#
        MAINTAIN: [ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        MANAGE: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.CONTROL,ActionTerms.GRANT,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        CATALOG: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.REGISTER,ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        TRACK: [ActionTerms.CAPTURE,ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE],#
        MONITOR: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.CAPTURE,ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        OPERATE: [ActionTerms.EXCHANGE, ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        FULFILL: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        TRANSACT: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        ENROLL: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.GRANT,ActionTerms.REGISTER,ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        PROCESS: [ActionTerms.EXCHANGE, ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        ADVISE: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
    }

    # Functional Pattern main Service Domain states
    # pattern : [life cycle states]
    #@todo finish life cycle mapping and check if state should be checked in pre and post validate for each operation
    states = {
        ADMINISTER: [],
        AGREETERMS: [],
        ALLOCATE: [],
        ANALYZE: [],
        ASSESS: [],
        DESIGN: [],
        DEVELOP: [],
        DIRECT: DirectLifeCycleStates,
        MAINTAIN: [],
        MANAGE: [],
        CATALOG: [],
        TRACK: [],
        MONITOR: [],
        OPERATE: [],
        FULFILL: [],
        TRANSACT: [],
        ENROLL: [],
        PROCESS: [],
        ADVISE: []
    }



#Capture service operation connections – The service operation connections for each business event

# Finance Context - Multi 10
#@todo finish context items
class BianContext(AbsBaseClass):
    COMPANY = "Company"
    OPERATIONAL_ENTITY = "Operational Entity"
    BRAND = "Brand"
    CHANNEL = "Channel"
    ENVIRONMENT = "Environment"
    COUNTRY = "Country"
    TIME_ZONE = "Time Zone"
    LANGUAGE = "Language"
    BRANCH = "Branch"
    DPARTY = "Dev Party"
    CONSUMER = "Consumer"

    items = {
        COMPANY:"x-bian-company",
        OPERATIONAL_ENTITY: "x-bian-op-entity",
        BRAND: "x-bian-brand",
        CHANNEL: "x-bian-channel",
        ENVIRONMENT: "x-bian-env",
        COUNTRY: "x-bian-country",
        TIME_ZONE: "x-bian-tz",
        LANGUAGE: "x-bian-language",
        BRANCH: "x-bian-branch",
        DPARTY: "x-bian-devparty",
        CONSUMER: "x-bian-consumer"
    }

    dict = {}

    def __init__(self, request):
        for key in self.items:
            flag = self.items[key]
            if flag in request.headers:
                self.dict[key] = request.headers[flag]

    def get(self, key):
        return self.dict[key]

    def put(self, key, value):
        self.dict[key] = value

    def keys(self):
        return self.dict.keys()

    def size(self):
        return len(self.dict)