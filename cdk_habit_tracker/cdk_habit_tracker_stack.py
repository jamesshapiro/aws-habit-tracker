from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_iam as iam,
    aws_apigateway as apigateway,
    Aws
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
            phone_number = [line for line in lines if line.startswith('NotificationPhone')][0].split('=')[1]
        ddb_table = dynamodb.Table(
            self, 'Table',
            partition_key=dynamodb.Attribute(name='PK1', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='SK1', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        ulid_layer = lambda_.LayerVersion(
            self,
            'Ulid3839Layer',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            code=lambda_.Code.from_asset('layers/ulid-python3839.zip'),
            compatible_architectures=[lambda_.Architecture.X86_64]
        )

        send_habit_query_function_cdk = lambda_.Function(
            self, 'SendHabitQueryCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='send_habit_query.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name,
                'PHONE_NUMBER': phone_number
            },
            timeout=cdk.Duration.seconds(30),
            layers=[ulid_layer]
        )

        receive_habit_datapoint_function_cdk = lambda_.Function(
            self, 'ReceiveHabitDatapointCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='receive_habit_datapoint.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name
            },
            timeout=cdk.Duration.seconds(30),
            layers=[ulid_layer]
        )

        topic = sns.Topic(self, "HabitCDK")
        topic.add_subscription(subscriptions.LambdaSubscription(receive_habit_datapoint_function_cdk))
        send_habit_query_function_cdk.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess"))

        ddb_table.grant_write_data(receive_habit_datapoint_function_cdk)
        ddb_table.grant_read_data(send_habit_query_function_cdk)

        api = apigateway.RestApi(
            self,
            'cdk-habit-tracker-api',
            description='CDK Lambda Layer Factory.',
            deploy_options=apigateway.StageOptions(
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True
            )
        )

        habit_resource = api.root.add_resource('habit')
        create_habit_credentials_role = iam.Role(
            self, 'cdk-create-habit-apig-ddb-role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
        )
        create_habit_policy = iam.Policy(
            self, 'cdk-create-habit-apig-ddb-policy',
            statements=[iam.PolicyStatement(
                actions=['dynamodb:PutItem'],
                resources=[ddb_table.table_arn]
            )]
        )
        create_habit_credentials_role.attach_inline_policy(create_habit_policy)
        habit_resource.add_method(
            'POST',
            integration=apigateway.AwsIntegration(
                service='dynamodb',
                action='PutItem',
                integration_http_method='POST',
                options=apigateway.IntegrationOptions(
                    credentials_role=create_habit_credentials_role,
                    request_templates={
                        #'application/json': f"""{{"Item": {{"PK1": {{"S": "$input.path('$.PK1')"}},"SK1": {{"S": "$input.path('$.SK1')"}}, "PK2":{{"S": "$input.path('$.PK2')"}}}}, "TableName": "{ddb_table.table_name}"}}"""
                        'application/json': f'{{"Item": $input.body, "TableName": "{ddb_table.table_name}"}}'
                    },
                    integration_responses=[
                        apigateway.IntegrationResponse(status_code='200')
                    ],
                )
            ),
            method_responses=[apigateway.MethodResponse(status_code='200')]
        )


        delete_habit_credentials_role = iam.Role(
            self, 'cdk-delete-habit-apig-ddb-role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
        )
        delete_habit_policy = iam.Policy(
            self, 'cdk-delete-habit-apig-ddb-policy',
            statements=[iam.PolicyStatement(
                actions=['dynamodb:DeleteItem'],
                resources=[ddb_table.table_arn]
            )]
        )
        delete_habit_credentials_role.attach_inline_policy(delete_habit_policy)
        habit_resource.add_method(
            'DELETE',
            integration=apigateway.AwsIntegration(
                service='dynamodb',
                action='DeleteItem',
                integration_http_method='POST',
                options=apigateway.IntegrationOptions(
                    credentials_role=delete_habit_credentials_role,
                    request_templates={
                        'application/json': f'{{"Key": $input.body, "TableName": "{ddb_table.table_name}"}}'
                    },
                    integration_responses=[
                        apigateway.IntegrationResponse(status_code='200')
                    ],
                )
            ),
            method_responses=[apigateway.MethodResponse(status_code='200')]
        )






        update_habit_credentials_role = iam.Role(
            self, 'cdk-update-habit-apig-ddb-role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
        )
        update_habit_policy = iam.Policy(
            self, 'cdk-update-habit-apig-ddb-policy',
            statements=[iam.PolicyStatement(
                actions=['dynamodb:UpdateItem'],
                resources=[ddb_table.table_arn]
            )]
        )
        update_habit_credentials_role.attach_inline_policy(update_habit_policy)
        habit_resource.add_method(
            'PUT',
            integration=apigateway.AwsIntegration(
                service='dynamodb',
                action='UpdateItem',
                integration_http_method='POST',
                options=apigateway.IntegrationOptions(
                    credentials_role=update_habit_credentials_role,
                    request_templates={
                        'application/json': f"""{{"Key": {{"PK1": {{"S": "$input.path('$.PK1.S')"}},"SK1": {{"S": "$input.path('$.SK1.S')"}}}}, "ExpressionAttributeNames":{{"#pk2":"PK2"}},"ExpressionAttributeValues":{{":pk2":{{"S":"$input.path('$.PK2.S')"}}}},"UpdateExpression": "SET #pk2 = :pk2","TableName": "{ddb_table.table_name}"}}"""
                    },
                    integration_responses=[
                        apigateway.IntegrationResponse(status_code='200')
                    ],
                )
            ),
            method_responses=[apigateway.MethodResponse(status_code='200')]
        )




        read_habit_credentials_role = iam.Role(
            self, 'cdk-read-habit-apig-ddb-role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
        )
        read_habit_policy = iam.Policy(
            self, 'cdk-read-habit-apig-ddb-policy',
            statements=[iam.PolicyStatement(
                actions=['dynamodb:GetItem'],
                resources=[ddb_table.table_arn]
            )]
        )
        read_habit_credentials_role.attach_inline_policy(read_habit_policy)
        # curl GET https://[API_PATH].execute-api.us-east-1.amazonaws.com/prod/habit/?PK1=read-a-book-for-10m&SK1=DAILY
        habit_resource.add_method(
            'GET',
            integration=apigateway.AwsIntegration(
                service='dynamodb',
                action='GetItem',
                integration_http_method='POST',
                options=apigateway.IntegrationOptions(
                    credentials_role=read_habit_credentials_role,
                    request_templates={
                        'application/json': f"""{{"Key": {{"PK1":{{"S":"HABIT#$input.params('PK1')"}},"SK1":{{"S":"FREQUENCY#$input.params('SK1')"}}}}, "TableName": "{ddb_table.table_name}"}}"""
                    },
                    integration_responses=[
                        apigateway.IntegrationResponse(status_code='200')
                    ],
                )
            ),
            method_responses=[apigateway.MethodResponse(status_code='200')]
        )