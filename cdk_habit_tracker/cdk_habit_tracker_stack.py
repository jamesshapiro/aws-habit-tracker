from aws_cdk import (
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
    aws_events as events,
    aws_events_targets as targets,
    aws_cognito as cognito,
    CfnOutput, Duration, Aws
)
from constructs import Construct
import aws_cdk as cdk

class CdkHabitTrackerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        with open('.cdk-params') as f:
            lines = f.read().splitlines()
            # .cdk-params should be of the form:
            # email=john@example.com
            email = [line for line in lines if line.startswith('email')][0].split('=')[1]
            habits_subdomain_name = [line for line in lines if line.startswith('habits_subdomain_name')][0].split('=')[1]
            habits_survey_subdomain_name = [line for line in lines if line.startswith('habits_survey_subdomain_name')][0].split('=')[1]
            hosted_zone_id = [line for line in lines if line.startswith('hosted_zone_id')][0].split('=')[1]
            zone_name = [line for line in lines if line.startswith('zone_name')][0].split('=')[1]
            githabit_domain=[line for line in lines if line.startswith('githabit_domain')][0].split('=')[1]
            githabit_survey_domain=[line for line in lines if line.startswith('githabit_survey_domain')][0].split('=')[1]
            githabit_zone=[line for line in lines if line.startswith('githabit_zone')][0].split('=')[1]
            githabit_zone_id=[line for line in lines if line.startswith('githabit_zone_id')][0].split('=')[1]
        ddb_table = dynamodb.Table(
            self, 'Habits',
            partition_key=dynamodb.Attribute(name='PK1', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='SK1', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute='TTL_EXPIRATION',
            removal_policy=cdk.RemovalPolicy.RETAIN
        )

        user_pool = cognito.UserPool(
            self, 'user-pool',
            self_sign_up_enabled=True,
            user_verification=cognito.UserVerificationConfig(
                email_subject='Verify Your githabit.com Account!',
                email_body='Thanks for signing up for GitHabit! Verify your account by entering in code {####}',
                email_style=cognito.VerificationEmailStyle.CODE
            ),
            sign_in_aliases=cognito.SignInAliases(
                email=True
            ),
            sign_in_case_sensitive=False,
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True,
                    mutable=True
                )
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            password_policy=cognito.PasswordPolicy(
                min_length=6,
                require_lowercase=False,
                require_uppercase=False,
                require_digits=False,
                require_symbols=False,
                temp_password_validity=Duration.days(7)
            )
        )

        auth = apigateway.CognitoUserPoolsAuthorizer(self, "habitsAuthorizer",
            cognito_user_pools=[user_pool]
        )

        client = user_pool.add_client('app-client',
            access_token_validity=Duration.days(1),
            supported_identity_providers=[cognito.UserPoolClientIdentityProvider.COGNITO],
            id_token_validity=Duration.days(1),
            prevent_user_existence_errors=True,
            refresh_token_validity=Duration.days(30)
        )

        CfnOutput(self, f'habits-ddb-table-name', value=ddb_table.table_name)
        scrape_layer = lambda_.LayerVersion(
            self,
            'Scrape39Layer',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            code=lambda_.Code.from_asset('layers/requestsbs4python39.zip'),
            compatible_architectures=[lambda_.Architecture.X86_64]
        )

        email_habit_survey_function_cdk = lambda_.Function(
            self, 'EmailHabitSurveyCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='email_habit_survey.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name,
                'USER_POOL_ID': user_pool.user_pool_id
            },
            timeout=Duration.minutes(15)
        )

        email_habit_survey_policy = iam.Policy(
            self, 'cdk-habits-cognito-list-users',
            statements=[
                iam.PolicyStatement(
                    actions=['cognito-idp:ListUsers'],
                    resources=[user_pool.user_pool_arn]
                ),
                iam.PolicyStatement(
                    actions=['ses:SendEmail','ses:SendRawEmail'],
                    resources=[f'arn:aws:ses:{Aws.REGION}:{Aws.ACCOUNT_ID}:identity/githabitsurvey@gmail.com']
                )
            ]
        )
        email_habit_survey_function_cdk.role.attach_inline_policy(email_habit_survey_policy)

        lambda_target = targets.LambdaFunction(email_habit_survey_function_cdk)
        
        events.Rule(self, "ScheduleRule",
            schedule=events.Schedule.cron(minute="0", hour="4"),
            targets=[lambda_target]
        )

        post_habit_data_function_cdk = lambda_.Function(
            self, 'HabitDataPostCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='habit_data_auth_post.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name
            },
            timeout=Duration.seconds(30)
        )

        fetch_github_data_function_cdk = lambda_.Function(
            self, 'FetchGithubDataCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='fetch_github_data.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name
            },
            timeout=Duration.seconds(45),
            layers=[scrape_layer]
        )

        fetch_github_target = targets.LambdaFunction(
            fetch_github_data_function_cdk,
            # TODO: Parameterize
            event=events.RuleTargetInput.from_object({
                'body': {'habits_user':email, 'github_user': 'jamesshapiro'}
            })
        )
        events.Rule(self, "GitHubFetchScheduleRule",
            schedule=events.Schedule.cron(minute="0", hour="4"),
            targets=[fetch_github_target]
        )

        ddb_table.grant_read_write_data(post_habit_data_function_cdk)
        ddb_table.grant_read_write_data(email_habit_survey_function_cdk)
        ddb_table.grant_write_data(fetch_github_data_function_cdk)

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

        habit_auth_resource = api.root.add_resource(
            'habit-auth',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "POST", "DELETE"]
            )
        )

        habit_auth_data_resource = api.root.add_resource(
            'habit-data-auth',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "POST"]
            )
        )

        habit_survey_resource = api.root.add_resource(
            'habit-survey',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "POST"]
            )
        )

        get_habit_function_cdk = lambda_.Function(
            self, 'GetHabitAuthCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='habit_auth_get.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name
            },
            timeout=Duration.seconds(30),
        )
        ddb_table.grant_read_data(get_habit_function_cdk)

        get_habit_data_auth_function_cdk = lambda_.Function(
            self, 'GetHabitDataAuthCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='habit_data_auth_get.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name
            },
            timeout=Duration.seconds(30),
        )
        ddb_table.grant_read_data(get_habit_data_auth_function_cdk)

        get_habit_survey_function_cdk = lambda_.Function(
            self, 'GetHabitSurveyCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='habit_survey_get.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name
            },
            timeout=Duration.seconds(30),
        )
        ddb_table.grant_read_data(get_habit_survey_function_cdk)

        post_habit_auth_function_cdk = lambda_.Function(
            self, 'PostHabitCDK',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('functions'),
            handler='habit_auth_post.lambda_handler',
            environment={
                'DDB_TABLE': ddb_table.table_name
            },
            timeout=Duration.seconds(30),
        )
        ddb_table.grant_write_data(post_habit_auth_function_cdk)

        # GET HABIT AUTH FUNCTIONS
        get_habit_auth_integration = apigateway.LambdaIntegration(
            get_habit_function_cdk,
            proxy=True
        )
        post_habit_auth_integration = apigateway.LambdaIntegration(
            post_habit_auth_function_cdk,
            proxy=True
        )

        get_habit_data_auth_integration = apigateway.LambdaIntegration(
            get_habit_data_auth_function_cdk,
            proxy=True
        )
        get_habit_survey_integration = apigateway.LambdaIntegration(
            get_habit_survey_function_cdk,
            proxy=True
        )

        habit_auth_resource.add_method(
            'GET',
            get_habit_auth_integration,
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }],
            authorizer=auth,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        habit_auth_data_resource.add_method(
            'GET',
            get_habit_data_auth_integration,
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }],
            authorizer=auth,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        habit_survey_resource.add_method(
            'GET',
            get_habit_survey_integration,
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }]
        )

        #######################################################################

        post_habit_data_integration = apigateway.LambdaIntegration(
            post_habit_data_function_cdk,
            proxy=True
        )

        habit_survey_resource.add_method(
            'POST',
            post_habit_data_integration,
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }]
        )

        habit_auth_resource.add_method(
            'POST',
            post_habit_auth_integration,
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }],
            authorizer=auth,
            authorization_type=apigateway.AuthorizationType.COGNITO
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
        #################################################################
        #githabit_domain
        #githabit_survey_domain
        #githabit_zone
        #githabit_zone_id
        githabit_zone = route53.HostedZone.from_hosted_zone_attributes(self, "GitHabitHostedZone",
            hosted_zone_id=githabit_zone_id,
            zone_name=githabit_zone
        )
        for subdomain in [githabit_domain, githabit_survey_domain]:
            site_bucket = s3.Bucket(
                self, f'{subdomain}-bucket',
            )
            certificate = certificatemanager.DnsValidatedCertificate(
                self, f'{subdomain}-certificate',
                domain_name=subdomain,
                hosted_zone=githabit_zone
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
                zone=githabit_zone,
                target=a_record_target,
                record_name=subdomain
            )
            CfnOutput(self, f'{subdomain}-bucket-name', value=site_bucket.bucket_name)