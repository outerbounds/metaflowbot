
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb
from troposphere import (
    GetAZs,
    Parameter,
    Ref,
    Region,
    Select,
    Split,
    Template,
    Join,
    GetAtt,
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
    Service,
    TaskDefinition,
    NetworkConfiguration
)


BotDeploymentTemplate = Template()

BotDeploymentTemplate.set_description(
    """Cloudformation Stack for Deploying Metaflowbot"""
)

METADATA_SERVICE_URL = BotDeploymentTemplate.add_parameter(Parameter("MetadataServiceUrl",Type='String',\
                                        Description="URL to the Metaflow metadata service"))

ADMIN_USER_ADDRESS = BotDeploymentTemplate.add_parameter(Parameter(\
                                "AdminUserAddress",
                                Type='String',\
                                Description="Email address of the admin user in the workspace"))
USERNAME = BotDeploymentTemplate.add_parameter(Parameter("MetaflowUsername",
                                Type='String',\
                                Description="Username for Metaflow"))
MFS3ROOTPATH = BotDeploymentTemplate.add_parameter(Parameter("MetaflowS3Root",
                                Type='String',\
                                Description="S3 Root Path Of Metaflow"))

MFS3ARN = BotDeploymentTemplate.add_parameter(Parameter("MetaflowS3BucketARN",
                                Type='String',\
                                Description="Metaflow S3 Bucket ARN"))


# TODO This need to be done Securely. 
METADATA_AUTH = BotDeploymentTemplate.add_parameter(Parameter("MetadaAuth",
                                Type='String',\
                                Description="Auth header for Metadataservice"))
SLACK_APP_TOKEN = BotDeploymentTemplate.add_parameter(Parameter("SlackAppToken",
                                Type='String',\
                                Description="App Token Created from Slack"))
SLACK_BOT_TOKEN = BotDeploymentTemplate.add_parameter(Parameter("SlackBotToken",
                                Type='String',\
                                Description="Bot Token Created From slack "))

DEPLOYMENT_AZ = BotDeploymentTemplate.add_parameter(
    Parameter(
        "DeploymentAvailablityZone",
        Type="AWS::EC2::AvailabilityZone::Name",
        Description="Availability zone where the bot gets deployed",
    )
)


cluster = BotDeploymentTemplate.add_resource(Cluster("MFBotCluster"))

ENV_DICT = {
    "SLACK_BOT_TOKEN":Ref(SLACK_BOT_TOKEN),
    "ADMIN_USER_ADDRESS":Ref(ADMIN_USER_ADDRESS),
    "SLACK_APP_TOKEN":Ref(SLACK_APP_TOKEN),
    "USERNAME":Ref(USERNAME),
    "METAFLOW_SERVICE_AUTH_KEY":Ref(METADATA_AUTH),
    "METAFLOW_SERVICE_URL":Ref(METADATA_SERVICE_URL),
    "METAFLOW_DATASTORE_SYSROOT_S3":Ref(MFS3ROOTPATH),
    "METAFLOW_DEFAULT_DATASTORE":"s3",
    "METAFLOW_DEFAULT_METADATA":"service"
}

# Todo : create secure ways of making app tokens. 

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
                }
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
        PolicyName="MfbotEcrPolicy",
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
                    ],
                    "Resource": [
                        Join('',[Ref(MFS3ARN),'/*'])
                    ],
                    "Effect": "Allow",
                    "Sid": "S3GetObject",
                },
            ],
        },
        Roles=[Ref(EcsTaskRole)],
    )
)

# logs:CreateLogGroup/

# S3 bucket name from ARN:
# https://stackoverflow.com/questions/63002267/how-to-get-s3-bucket-name-from-s3-arn-using-cloudformation

### Routing and VPC Settings. 
# Create a VPC with Subnet. The VPC should have an IG attached 
# and the 

vpc = BotDeploymentTemplate.add_resource(ec2.VPC('MetaflowbotPublicVpc',CidrBlock="10.0.0.0/16",))

subnet = BotDeploymentTemplate.add_resource(ec2.Subnet(
    "MetaflowbotDeploymentSubnet",
    AvailabilityZone=Ref(DEPLOYMENT_AZ),
    CidrBlock="10.0.0.0/24",
    VpcId=Ref(vpc),
    MapPublicIpOnLaunch=True,
))

internetgateway = BotDeploymentTemplate.add_resource(ec2.InternetGateway("MFBotInternetGateway"))

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
                Image="valaygaurang/metaflowbot:0.9.11",
                Essential=True,
                Environment = [
                    Environment(**dict(Name=k,Value=v)) for k,v in ENV_DICT.items()
                ]
            )
        ],
    )
)


efs_security_group = BotDeploymentTemplate.add_resource(ec2.SecurityGroup(
    "MFBotSecurityGroup",
    # Outbound rules
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html
    SecurityGroupEgress = [
        ec2.SecurityGroupRule(
            "MFBotOutboundRules",
            ToPort=65534,
            FromPort=0,
            IpProtocol="tcp",
            CidrIp="0.0.0.0/0",
        )
    ],
    # inbound rules 
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule-1.html
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            "MFBotInboundRules",
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


