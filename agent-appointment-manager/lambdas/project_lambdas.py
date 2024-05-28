import sys

from aws_cdk import aws_lambda, Duration, aws_iam as iam

from constructs import Construct


LAMBDA_TIMEOUT = 900

BASE_LAMBDA_CONFIG = dict(
    timeout=Duration.seconds(LAMBDA_TIMEOUT),
    memory_size=128,
    tracing=aws_lambda.Tracing.ACTIVE,
    architecture=aws_lambda.Architecture.ARM_64
)

PYTHON_LAMBDA_CONFIG = dict(
    runtime=aws_lambda.Runtime.PYTHON_3_11, **BASE_LAMBDA_CONFIG
)

class Lambdas(Construct):
    def __init__(self, scope: Construct, construct_id: str, self_account, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        COMMON_LAMBDA_CONF = dict(environment={}, **PYTHON_LAMBDA_CONFIG)


        self.dynamodb_put_item = aws_lambda.Function(
            self, "DynamoDB_put_item", 
            description ="Put items to DynamoDB" ,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/dynamodb_put_item"),
            **COMMON_LAMBDA_CONF)
        
        self.dynamodb_query = aws_lambda.Function(
            self, "query_dynamodb_passanger", 
            description ="Query DynamoDB" ,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/dynamodb_query"),
            **COMMON_LAMBDA_CONF)
        
        self.ask_date = aws_lambda.Function(
            self, "ask_date", 
            description ="Ask today Date" ,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/ask_date"),
            **COMMON_LAMBDA_CONF)
        
        for f in [self.dynamodb_put_item, self.dynamodb_query,self.ask_date]:
            f.add_permission(
                    f'invoke from account',
                    principal=iam.ServicePrincipal("bedrock.amazonaws.com"),
                    action="lambda:invokeFunction",
                    # source_arn=f"arn:aws:lambda:{self.region}:{self.account}:*")
                    )
