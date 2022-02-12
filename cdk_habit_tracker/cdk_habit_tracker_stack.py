from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_certificatemanager as certificatemanager,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_cloudfront_origins as origins,
    CfnOutput
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
            phone_number = [line for line in lines if line.startswith('phone_number')][0].split('=')[1]
            email = [line for line in lines if line.startswith('email')][0].split('=')[1]
            habits_subdomain_name = [line for line in lines if line.startswith('habits_subdomain_name')][0].split('=')[1]
            habits_survey_subdomain_name = [line for line in lines if line.startswith('habits_survey_subdomain_name')][0].split('=')[1]
            hosted_zone_id = [line for line in lines if line.startswith('hosted_zone_id')][0].split('=')[1]
            zone_name = [line for line in lines if line.startswith('zone_name')][0].split('=')[1]
        
        # HABIT TRACKER BACK-END
        ddb_table = dynamodb.Table(
            self, 'Table',
            partition_key=dynamodb.Attribute(name='PK1', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='SK1', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        CfnOutput(self, f'habits-ddb-table-name', value=ddb_table.table_name)
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
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            )
        )

        habit_resource = api.root.add_resource('habit',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "POST"]
            )
        )

        create_habit_credentials_role = iam.Role(
            self, 'cdk-create-habit-apig-ddb-role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
        )
        ddb_table.grant_write_data(create_habit_credentials_role)
        habit_resource.add_method(
            'POST',
            integration=apigateway.AwsIntegration(
                service='dynamodb',
                action='PutItem',
                integration_http_method='POST',
                options=apigateway.IntegrationOptions(
                    credentials_role=create_habit_credentials_role,
                    request_templates={
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
        ddb_table.grant_full_access(delete_habit_credentials_role)
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
        ddb_table.grant_write_data(update_habit_credentials_role)
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
        ddb_table.grant_read_data(read_habit_credentials_role)
        habit_resource.add_method(
            'GET',
            integration=apigateway.AwsIntegration(
                service='dynamodb',
                action='Query',
                integration_http_method='POST',
                options=apigateway.IntegrationOptions(
                    credentials_role=read_habit_credentials_role,
                    request_templates={
                        'application/json': f"""{{"KeyConditionExpression":"#pk1=:pk1", "ExpressionAttributeNames":{{"#pk1":"PK1"}}, "ExpressionAttributeValues":{{":pk1":{{"S":"HABIT#HABIT"}}}}, "TableName": "{ddb_table.table_name}"}}"""
                    },
                    integration_responses=[
                        apigateway.IntegrationResponse(
                            status_code='200',
                            response_parameters={'method.response.header.Access-Control-Allow-Origin': "'*'"}
                        )
                    ],
                )
            ),
            method_responses=[apigateway.MethodResponse(
                    status_code='200',
                    response_parameters={'method.response.header.Access-Control-Allow-Origin': True}
                )
            ]
        )

        query_habit_data_credentials_role = iam.Role(
            self, 'cdk-query-habit-data-apig-ddb-role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
        )
        ddb_table.grant_read_data(query_habit_data_credentials_role)

        # Query Habit Data Points for front-end
        habit_data_resource = api.root.add_resource(
            'habit-data',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "POST"]
            )
        )

        habit_data_resource.add_method(
            'GET',
            integration=apigateway.AwsIntegration(
                service='dynamodb',
                action='Query',
                integration_http_method='POST',
                options=apigateway.IntegrationOptions(
                    credentials_role=query_habit_data_credentials_role,
                    request_templates={
                        'application/json': f"""{{"KeyConditionExpression":"#pk1=:pk1", "ExpressionAttributeNames":{{"#pk1":"PK1"}}, "ExpressionAttributeValues":{{":pk1":{{"S":"HABIT#$input.params('PK1')"}}}}, "ExclusiveStartKey":{{"PK1":{{"S":"HABIT#$input.params('PK1')"}},"SK1":{{"S":"DATE#$input.params('startkey')"}}}},"Limit": $input.params('limit'), "ScanIndexForward": false, "TableName": "{ddb_table.table_name}"}}"""
                    },
                    integration_responses=[
                        apigateway.IntegrationResponse(
                            status_code='200',
                            response_parameters={'method.response.header.Access-Control-Allow-Origin': "'*'"}
                        )
                    ],
                )
            ),
            method_responses=[apigateway.MethodResponse(
                    status_code='200',
                    response_parameters={'method.response.header.Access-Control-Allow-Origin': True}
                )
            ]
        )

        # HABIT TRACKER / SURVEY WEBSITES
        zone = route53.HostedZone.from_hosted_zone_attributes(self, "HostedZone",
            hosted_zone_id=hosted_zone_id,
            zone_name=zone_name
        )
        for subdomain in [habits_subdomain_name, habits_survey_subdomain_name]:
            site_bucket = s3.Bucket(
                self, f'{subdomain}-bucket',
            )
            certificate = certificatemanager.DnsValidatedCertificate(
                self, f'{subdomain}-certificate',
                domain_name=subdomain,
                hosted_zone=zone
            )
            distribution = cloudfront.Distribution(
                self, f'{subdomain}-distribution',
                default_behavior=cloudfront.BehaviorOptions(
                    origin=origins.S3Origin(site_bucket),
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                ),
                comment=f'{subdomain} S3 HTTPS',
                default_root_object='index.html',
                domain_names=[subdomain],
                certificate=certificate
            )
            CfnOutput(self, f'{subdomain}-cf-distribution', value=distribution.distribution_id)
            a_record_target = route53.RecordTarget.from_alias(route53_targets.CloudFrontTarget(distribution))
            route53.ARecord(
                self, f'{subdomain}-alias-record',
                zone=zone,
                target=a_record_target,
                record_name=subdomain
            )
            CfnOutput(self, f'{subdomain}-bucket-name', value=site_bucket.bucket_name)