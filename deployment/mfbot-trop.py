
import troposphere
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb
from troposphere import (
    GetAZs,
    Parameter,
    Ref,
    Region,
    Select,
    Split,
    StackName,
    Template,
    Join,
    GetAtt,
)
from troposphere.logs import (
    LogGroup
)
from troposphere.iam import (
    Role,
    PolicyType
    
)
from troposphere.ecs import (
    AwsvpcConfiguration,
    Cluster,
    ContainerDefinition,
    Environment,
    LogConfiguration,
    Secret,
    Service,
    TaskDefinition,
    NetworkConfiguration
)


BotDeploymentTemplate = Template()

BotDeploymentTemplate.set_description(
    """Cloudformation Stack for Deploying Metaflowbot"""
)

METADATA_SERVICE_URL = BotDeploymentTemplate.add_parameter(Parameter("MetadataServiceUrl",Type='String',\
                                        Description="URL of the metadata service"))

ADMIN_USER_ADDRESS = BotDeploymentTemplate.add_parameter(Parameter(\
                                "AdminEmailAddress",
                                Type='String',\
                                Description="Email address of the admin user in the slack workspace"))

# Generate ARN from the s3 url and remove ARN parameter. 
MFS3ROOTPATH = BotDeploymentTemplate.add_parameter(Parameter("MetaflowDatastoreSysrootS3",
                                Type='String',\
                                Description="Amazon S3 URL for Metaflow DataStore "))

MFS3ARN = Join('',['arn:aws:s3:::',Select(1,Split("s3://",Ref(MFS3ROOTPATH))),])
Metaflowbot_SECRETS_ARN = BotDeploymentTemplate.add_parameter(Parameter("MetaflowbotSecretsManagerARN",
                                Type='String',\
                                Description="ARN of the secret holding Metaflowbot credentials in Secrets Manager"))

# These are Parameter Store Secure secret names. 
METADATA_AUTH = BotDeploymentTemplate.add_parameter(Parameter("MetadataServiceAuthParameterKey",
                                Type='String',\
                                Default="METADATASERVICE_AUTH_KEY",\
                                Description="Key for Metadata service auth parameter in Secrets Manager."))
SLACK_APP_TOKEN = BotDeploymentTemplate.add_parameter(Parameter("SlackAppTokenParameterKey",
                                Type='String',\
                                Default="SLACK_APP_TOKEN_KEY",\
                                Description="Key for SLACK_APP_TOKEN parameter in Secrets Manager."))
SLACK_BOT_TOKEN = BotDeploymentTemplate.add_parameter(Parameter("SlackBotTokenParameterKey",
                                Type='String',\
                                Default="SLACK_BOT_TOKEN_KEY",\
                                Description="Key for SLACK_BOT_TOKEN parameter in Secrets Manager."))

cluster = BotDeploymentTemplate.add_resource(Cluster("MetaflowbotCluster"))


ENV_DICT = {
    "ADMIN_USER_ADDRESS":Ref(ADMIN_USER_ADDRESS),
    "USERNAME":"slackbot",    
    "METAFLOW_SERVICE_URL":Ref(METADATA_SERVICE_URL),
    "METAFLOW_DATASTORE_SYSROOT_S3":Ref(MFS3ROOTPATH),
    "METAFLOW_DEFAULT_DATASTORE":"s3",
    "METAFLOW_DEFAULT_METADATA":"service"
}

# best practices from : https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-secrets.html
SECRETS =  [
    Secret(
        Name='METAFLOW_SERVICE_AUTH_KEY',
        ValueFrom=Join("",[Ref(Metaflowbot_SECRETS_ARN),":",Ref(METADATA_AUTH),"::"])
    ),
    Secret(
        Name='SLACK_APP_TOKEN',
        ValueFrom=Join("",[Ref(Metaflowbot_SECRETS_ARN),":",Ref(SLACK_APP_TOKEN),"::"])
    ),Secret(
        Name='SLACK_BOT_TOKEN',
        ValueFrom=Join("",[Ref(Metaflowbot_SECRETS_ARN),":",Ref(SLACK_BOT_TOKEN),"::"])
    )
]

# task role vs execution role : 
# https://selfoverflow.com/questions/48999472/difference-between-aws-elastic-container-services-ecs-executionrole-and-taskr/49947471
# ECS execution role is capabilities of ECS agent
# ECS task role is specific capabilities within the task itself : s3_access_iam_role (capabilities of task)


EcsClusterRole = BotDeploymentTemplate.add_resource(
    Role(
        "EcsClusterRole",
        Path="/",
        ManagedPolicyArns=["arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"],
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Effect": "Allow",
                },
            ],
        },
    )
)

EcsTaskRole = BotDeploymentTemplate.add_resource(
    Role(
        "EcsTaskRole",
        Path="/",
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Effect": "Allow",
                }
            ],
        },
    )
)

PolicyEcr = BotDeploymentTemplate.add_resource(
    PolicyType(
        "PolicyEcr",
        PolicyName="MetaflowbotEcrPolicy",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": ["ecr:GetAuthorizationToken"],
                    "Resource": ["*"],
                    "Effect": "Allow",
                },
                {
                    "Action": [
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage",
                        "ecr:BatchCheckLayerAvailability",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": ["*"],
                    "Effect": "Allow",
                    "Sid": "AllowPull",
                },
            ],
        },
        Roles=[Ref(EcsClusterRole)],
    )
)

secrets_access_policy = BotDeploymentTemplate.add_resource(
    PolicyType(
        "MetaflowbotSecretAccess",
        # 
        PolicyName='Metaflowbot',
        PolicyDocument= {
            "Version": "2012-10-17",
            "Statement": [                
                {
                    "Action": [
                       "secretsmanager:GetSecretValue",
                    ],
                    "Resource": [
                        Ref(Metaflowbot_SECRETS_ARN)
                    ],
                    "Effect": "Allow",
                    "Sid": "S3GetObject",
                },
            ]
        },
        Roles=[Ref(EcsClusterRole)],
    )
)

S3AccessPolicy = BotDeploymentTemplate.add_resource(
    PolicyType(
        "S3AccessPolicy",
        PolicyName="MetaflowbotS3AccessPolicy",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [                
                {
                    "Action": [
                       "s3:GetObject",
                       "s3:HeadObject",
                       "s3:ListObjects",
                       "s3:ListObjectsV2",
                    ],
                    "Resource": [
                        Join('',[MFS3ARN,'/*'])
                    ],
                    "Effect": "Allow",
                    "Sid": "S3GetObject",
                },
            ],
        },
        Roles=[Ref(EcsTaskRole)],
    )
)
### Routing and VPC Settings. 
# Create a VPC with Subnet. The VPC should have an IG attached 
# and rule created in it's route table; 

vpc = BotDeploymentTemplate.add_resource(ec2.VPC('MetaflowbotPublicVpc',CidrBlock="10.0.0.0/16",))

subnet = BotDeploymentTemplate.add_resource(ec2.Subnet(
    "MetaflowbotDeploymentSubnet",
    AvailabilityZone=Select(
        0,GetAZs(region=Region)
    ),
    CidrBlock="10.0.0.0/24",
    VpcId=Ref(vpc),
    MapPublicIpOnLaunch=True,
))

internetgateway = BotDeploymentTemplate.add_resource(ec2.InternetGateway("MetaflowbotInternetGateway"))

net_gw_vpc_attachment = BotDeploymentTemplate.add_resource(
    ec2.VPCGatewayAttachment(
        "InternetGatewayAttachment",
        VpcId=Ref(vpc),
        InternetGatewayId=Ref(internetgateway),
    )
)


public_route_table = BotDeploymentTemplate.add_resource(
    ec2.RouteTable(
        "PublicRouteTable",
        VpcId=Ref(vpc),
    )
)

public_route_association = BotDeploymentTemplate.add_resource(
    ec2.SubnetRouteTableAssociation(
        "PublicRouteAssociation",
        SubnetId=Ref(subnet),
        RouteTableId=Ref(public_route_table),
    )
)

default_public_route = BotDeploymentTemplate.add_resource(
    ec2.Route(
        "PublicDefaultRoute",
        RouteTableId=Ref(public_route_table),
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=Ref(internetgateway),
    )
)
LOG_GROUP_STRING = Join("",[
                            '/ecs/',
                            StackName,
                            "-metaflowbot",
                        ])
loggroup= BotDeploymentTemplate.add_resource(
    LogGroup(
        "MetaflowbotLogGroup",
        LogGroupName=LOG_GROUP_STRING
    )
)

task_definition = BotDeploymentTemplate.add_resource(
    TaskDefinition(
        "MetaflowbotTaskDefinition",
        RequiresCompatibilities=["FARGATE"],
        Cpu="4096",
        ExecutionRoleArn=GetAtt(EcsClusterRole,"Arn"),
        TaskRoleArn=GetAtt(EcsTaskRole,"Arn"),
        Memory="8192",
        NetworkMode="awsvpc",
        ContainerDefinitions=[
            ContainerDefinition(
                Name="metaflowbot",
                Image="valaygaurang/metaflowbot",
                Essential=True,
                LogConfiguration=LogConfiguration(
                    LogDriver = "awslogs",
                    Options= {
                        "awslogs-group": LOG_GROUP_STRING,
                        "awslogs-region":Region,
                        "awslogs-stream-prefix": 'ecs'
                    },
                ),
                Environment = [
                    Environment(**dict(Name=k,Value=v)) for k,v in ENV_DICT.items()
                ],
                Secrets=SECRETS
            )
        ],
    )
)


efs_security_group = BotDeploymentTemplate.add_resource(ec2.SecurityGroup(
    "MetaflowbotSecurityGroup",
    # Outbound rules
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html
    SecurityGroupEgress = [
        ec2.SecurityGroupRule(
            "MetaflowbotOutboundRules",
            ToPort=65534,
            FromPort=0,
            IpProtocol="tcp",
            CidrIp="0.0.0.0/0",
        )
    ],
    VpcId=Ref(vpc),
    GroupDescription="Allow All In and outbound traffic",
))

service = BotDeploymentTemplate.add_resource(
    Service(
        "MetaflowbotDeployment",
        Cluster=Ref(cluster),
        DesiredCount=1,
        TaskDefinition=Ref(task_definition),
        LaunchType="FARGATE",
        NetworkConfiguration=NetworkConfiguration(
            AwsvpcConfiguration=AwsvpcConfiguration(
                    Subnets=[Ref(subnet)],
                    AssignPublicIp='ENABLED',
                    SecurityGroups=[Ref(efs_security_group)]
                    )
        ),
    )
)
print(BotDeploymentTemplate.to_yaml())


