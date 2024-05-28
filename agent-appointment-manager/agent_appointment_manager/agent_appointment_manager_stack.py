import json
import os
from aws_cdk import (
    # Duration,
    Stack,
    aws_dynamodb as ddb,
    RemovalPolicy,
    aws_iam as iam,
    aws_bedrock as bedrock
    
    # aws_sqs as sqs,
)
from constructs import Construct
from agent_bedrock import CreateAgent,CreateAgentWithKB,CreateAgentWithKA,CreateAgentWithAG
from databases import Tables
from lambdas import Lambdas
from agent_role import CreateAgentRole

REMOVAL_POLICY = RemovalPolicy.DESTROY
TABLE_CONFIG = dict (removal_policy=REMOVAL_POLICY, billing_mode= ddb.BillingMode.PAY_PER_REQUEST)

def create_kb_property(kb_data):
        kb_group_properties = []
        for n in kb_data: 
             kb_group_property = bedrock.CfnAgent.AgentKnowledgeBaseProperty(
                    description=n["description_kb"],
                    knowledge_base_id=n["knowledge_base_id"],
        )
        kb_group_properties.append(kb_group_property)
        return kb_group_properties
def agent_action_group_property(ag_data):
    agent_action_group_properties = []
    agent_action_group_property = bedrock.CfnAgent.AgentActionGroupProperty(
                        action_group_name="askinuput",
                        parent_action_group_signature="AMAZON.UserInput",
                        #skip_resource_in_use_check_on_delete=False
                            )
    agent_action_group_properties.append(agent_action_group_property)
    for n in ag_data: 
        parameters = {}
        for p in n["functions"]["parameters"]:
            parameters[p["name"]] = bedrock.CfnAgent.ParameterDetailProperty(
                                            type=p["type"],

                                            # the properties below are optional
                                            description=p["description"],
                                            required=bool(p["required"])
                                        )

        agent_action_group_property = bedrock.CfnAgent.AgentActionGroupProperty(
                                action_group_name=n["action_group_name"],

                                # the properties below are optional
                                action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                                    lambda_=n["lambda_"]
                                    ),
                                
                                action_group_state="ENABLED",
                                #description=n["description"],
                                function_schema=bedrock.CfnAgent.FunctionSchemaProperty(
                                    functions=[bedrock.CfnAgent.FunctionProperty(
                                        name=n["functions"]["name"],
                                        # the properties below are optional
                                        description=n["functions"]["description"],
                                        parameters=parameters
                                    )]
                                ),
                                #parent_action_group_signature="AMAZON.UserInput",
                                skip_resource_in_use_check_on_delete=False
                            )
        agent_action_group_properties.append(agent_action_group_property)
    return agent_action_group_properties

class AgentAppointmentManagerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ENV_KEY_NAME = "date"
        env_key_sec_global = "phone_number"
        file_path_ag_data = './spa_agent/ag_data.json'
        file_path_agent_data = './spa_agent/agent_data.json'
        file_path_kb_data = './spa_agent/kb_data.json'

        REGION = self.region
        ACCOUNT_ID = self.account

        Fn  = Lambdas(self,'Fn',ACCOUNT_ID)
        Tbl = Tables(self, 'Tbl')

        with open(file_path_agent_data, 'r') as file:
            agent_data = json.load(file)

        #ag_data exists
        if  os.path.exists(file_path_ag_data): 
             with open(file_path_ag_data, 'r') as file:
                  ag_data = json.load(file)
            #add lambda arn to ag data
             ag_data[0]["lambda_"] = Fn.dynamodb_put_item.function_arn
             ag_data[1]["lambda_"] = Fn.dynamodb_query.function_arn
             ag_data[2]["lambda_"] = Fn.ask_date.function_arn

        #kb_data exists
        if  os.path.exists(file_path_kb_data): 
             with open(file_path_kb_data, 'r') as file:
                  kb_data = json.load(file)
        else:
             kb_data = None

        Tbl.spa_table.add_global_secondary_index(index_name = 'phoneindex', 
                                                            partition_key = ddb.Attribute(name=env_key_sec_global,type=ddb.AttributeType.STRING), 
                                                            projection_type=ddb.ProjectionType.KEYS_ONLY)

        #Create Amazon S3 Bucke and upload the data into the folder vectordb

        Tbl.spa_table.grant_full_access(Fn.dynamodb_put_item)
        Tbl.spa_table.grant_full_access(Fn.dynamodb_query)
        
        Fn.dynamodb_put_item.add_environment(key='TABLE_NAME', value= Tbl.spa_table.table_name)
        Fn.dynamodb_query.add_environment(key='TABLE_NAME', value= Tbl.spa_table.table_name)
        Fn.dynamodb_query.add_environment(key='ENV_KEY_NAME', value= env_key_sec_global)

        agent_resource_role = CreateAgentRole(self, "role",ACCOUNT_ID,REGION,agent_data["foundation_model"],kb_data)

        #https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_bedrock/CfnAgent.html
        #https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-bedrock-agent-agentactiongroup.html#cfn-bedrock-agent-agentactiongroup-actiongroupstate


        #add knowledge base
        if kb_data and not ag_data:
            agent_name = "spa_agent_withKB"
            print("KB data")
            agent_knowledge_base_property =create_kb_property(kb_data) 

            ag = CreateAgentWithKB(self, "agentwithkb",agent_name, agent_data["foundation_model"],agent_data["agent_instruction"],agent_data["description"],agent_knowledge_base_property, agent_resource_role.arn)
        
        elif ag_data and not kb_data:
            agent_name = "spa_agent_withag"
            print("AG data")
            agent_action_group_properties = agent_action_group_property(ag_data)                              
            ag = CreateAgentWithAG(self, "agentwithag",agent_name, agent_data["foundation_model"],agent_data["agent_instruction"],agent_data["description"],agent_action_group_properties, agent_resource_role.arn)

        elif ag_data and kb_data:
            agent_name = "spa_agent_with_ag_kb"
            print("AG and KB data")
            agent_action_group_properties = agent_action_group_property(ag_data)
            agent_knowledge_base_property =create_kb_property(kb_data) 
            ag = CreateAgentWithKA(self, "agentwithbooth", agent_name, agent_data["foundation_model"], agent_data["agent_instruction"], agent_data["description"], agent_knowledge_base_property, agent_action_group_properties, agent_resource_role.arn)        

        else:
            agent_name = "spa_agent"
            print("No data")
            ag = CreateAgent(self, "agent",agent_name, agent_data["description"], agent_resource_role.arn)
