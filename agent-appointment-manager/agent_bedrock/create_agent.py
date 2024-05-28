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

class CreateAgent(Stack):
    def __init__(self, scope: Construct, construct_id: str,agent_name, description, agent_resource_role_arn, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.cfn_agent = bedrock.CfnAgent(self, "MyCfnAgent",
                    agent_name=agent_name,
                    description=description,
                    auto_prepare = False,
                    idle_session_ttl_in_seconds = 600,
                    skip_resource_in_use_check_on_delete=False,
                    test_alias_tags={
                        "test_alias_tags_key": "testAliasTags"
                    },
                    agent_resource_role_arn = agent_resource_role_arn

                    )
        self.cfn_agent.apply_removal_policy(RemovalPolicy.DESTROY)
        

        

