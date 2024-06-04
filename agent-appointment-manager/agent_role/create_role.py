from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
)
from constructs import Construct

class CreateAgentRole(Stack):

    def __init__(self, scope: Construct, construct_id: str, _account, _region, foundation_model, kb_data, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.kb_service_role = iam.Role(
                self,
                "Kb",
                role_name= f'AmazonBedrockExecutionRoleForAgents_{kb_data[0]["knowledge_base_id"]}',
                assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "aws:SourceAccount": _account
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock:{_region}:{_account}:agent/*"
                    }
                })
            )
        
        self.kb_service_role.add_to_policy(iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                ],
                resources=[
                    f"arn:aws:bedrock:{_region}::foundation-model/{foundation_model}",
                    ]
                )
                )
        

             
        if kb_data:
            resources = []
            for item in kb_data:
                items= f"arn:aws:bedrock:{_region}:{_account}:knowledge-base/{item['knowledge_base_id']}"
                resources.append(items)
       
            self.knowledge_base_policy = iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:Retrieve",
                ],
                resources=resources
                )
            self.kb_service_role.add_to_policy(self.knowledge_base_policy)
            
        
        self.arn = self.kb_service_role.role_arn

        