from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

import aws_cdk as cdk

class CdkHabitTrackerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        with open('.cdk-params') as f:
            lines = f.read().splitlines()
            # .cdk-params should be of the form:
            # account_id=12345678901234
            account_id = [line for line in lines if line.startswith('account_id')][0].split('=')[1]
            phone_number = [line for line in lines if line.startswith('NotificationPhone')][0].split('=')[1]
            region = [line for line in lines if line.startswith('region')][0].split('=')[1]
        ddb_table = dynamodb.Table(
            self, "Table",
            partition_key=dynamodb.Attribute(name="PK1", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK1", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        ulid_layer = lambda_.LayerVersion(
            self,
            "Ulid3839Layer",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            code=lambda_.Code.from_asset('layers/ulid-python3839.zip'),
            compatible_architectures=[lambda_.Architecture.X86_64]
        )

        send_habit_query_function_cdk = lambda_.Function(
            self, "SendHabitQueryCDK",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("functions"),
            handler="send_habit_query.lambda_handler",
            environment={
                "DDB_TABLE": ddb_table.table_name
            },
            timeout=cdk.Duration.seconds(30),
            layers=[ulid_layer]
        )

        receive_habit_datapoint_function_cdk = lambda_.Function(
            self, "ReceiveHabitDatapointCDK",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("functions"),
            handler="receive_habit_datapoint.lambda_handler",
            environment={
                "DDB_TABLE": ddb_table.table_name
            },
            timeout=cdk.Duration.seconds(30),
            layers=[ulid_layer]
        )

        ddb_table.grant_write_data(receive_habit_datapoint_function_cdk)
        ddb_table.grant_read_data(send_habit_query_function_cdk)
