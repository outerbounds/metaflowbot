# Deploying the bot on AWS

There are many ways (automated and manual) to deploy, configure, and manage AWS resources depending on your security posture and familiarity with the AWS eco-system. If you cannot use our [AWS CloudFormation template](../deployment/mfbot-cfn-template.yml), this article lists the steps for a rather straightforward deployment of AWS resources for use by Metaflow bot.

Please note that Metaflow bot can re-use existing AWS resources - for example, your existing ECS cluster for container deployment. The instructions listed here will create these resources from scratch. If you have a strong background in administering AWS resources, you will notice that many of the security policies are fairly permissive and are intended to serve as a starting point for more complex deployments. Please reach out to us if you would like to discuss more involved deployments.

## Manually configuring bot

### Slack Access Tokens

1. [Configure the bot on the slack workspace and retrieve the SLACK_BOT_TOKEN and SLACK_APP_TOKEN](./Setup.md#slack-setup)

### VPC 

1. Run the VPC Wizard
    1. Open the [Amazon VPC console](https://console.aws.amazon.com/vpc/) and in the left navigation pane, choose VPC Dashboard.
    2. Choose Launch VPC Wizard, VPC with a Single Public Subnet, Select.
    3. For VPC name, give your VPC a unique name.
    5. Choose Create VPC.
    6. When the wizard is finished, choose OK.

### ECS Execution IAM Role (Optional)

1. Open the [IAM console](https://console.aws.amazon.com/iam/)  and in the navigation pane, choose Roles, _Create role_.
2. For _Select type of trusted entity section_, choose _AWS service_.
3. For _Choose the service that will use this role_, choose _Elastic Container Service_.
4. For _Select your use case_, choose _Elastic Container Service Task_ and choose _Next: Permissions_.
5. Choose _AmazonECSTaskExecutionRolePolicy_.
5. Choose _Next:tags_.
6. For Add tags (optional), enter any metadata tags you want to associate with the IAM role, and  then choose Next: Review.
6. For Role name, enter a name for your role and then choose _Create role_ to finish. Note the ARN of the IAM role you just created.

### ECS Task IAM Role

1. Open the [IAM console](https://console.aws.amazon.com/iam/) and in the navigation pane, choose _Roles, Create role_.
2. For Select _type of trusted entity section_, choose _AWS service._
3. For Choose the service that will use this role, choose Elastic Container Service.
4. For Select your use case, choose _Elastic Container Service Task_ and choose _Next: Permissions._
5. Next, we will create a [policy](https://console.aws.amazon.com/iamv2/home#/policies) for Amazon S3 and attach it to this role:
    1. Amazon S3 for data storage
        1. Choose Create Policy to open a new window.
        2. Use the visual service editor to create the policy
            1. For Service, choose S3.
            2. For Actions, add _GetObject_ and _ListBucket_ as allowed actions
            3. For resources, the bucket name should be the same asmetaflow datastore S3 bucket. For object choose _any_ for object name. Choose Save changes.
            4. Choose Review policy. On the Review policy page, for Name type your own unique name and choose _Create_ policy to finish.
6. Click the refresh button in the original pane (in Step 4.) and choose the policy that you just created (in Step 5.). Choose Next:tags.
7. For _Add tags_ (optional), enter any metadata tags you want to associate with the IAM role, and then choose Next: Review.
8. For _Role name_, enter a name for your role and then choose _Create role_ to finish. 

### ECS Cluster + Fargate Task

1. Open the [ECS console](https://console.aws.amazon.com/ecs) and from the navigation bar, select the region to use.
2. Choose _Create Cluster_ under Clusters.
3. Choose _Networking only_, _Next step_.
4. Pick a name for _Cluster name_. Don't enable Create VPC. We will use the VPC [we have created previously](#vpc). You can choose to check Enable Container Insights. Choose _Create_.
5. Choose _View Cluster_ and choose _Task Definitions_ on the left side pane.
6. Choose _Create new Task Definition_, _Fargate_ and Next step.
    1. Under _Configure task_ and _container definitions_,
        1. Choose a _Task Definition Name_.
        2. Choose the _Task Role_ as the one you [just created above](#ecs-task-iam-role).
    2. Under _Task execution IAM role_, set the _Task execution role_ to _ecsTaskExecutionRole_ or set it to the IAM role created for [ECS execution](#ecs-execution-iam-role). Leave it empty otherwise.
    3. Under _Task size_,
        1. Choose 8 GB for _Task memory (GB)_
        2. Choose 4 vCPU for _Task CPU (vCPU)_.
    4. Under _Container Definitions_, choose Add container
        1. Set _metaflowbot_ as the _Container name_.
        2. Set _outerbounds/metaflowbot_ as the _Image_.
        3. Leave other options as is.
        4. Under _Advanced container configuration_, in _Environment variables_ add the following values
            1. Set _Key_ as ADMIN_USER_ADDRESS and the _Value_ as the email address of the user in the slack workspace with whom the bot will open a message thread to store state related information.
            2. Set _Key_ as METAFLOW_SERVICE_URL and the _Value_ as the URL to the metadata service.
            3. Set _Key_ as METAFLOW_DATASTORE_SYSROOT_S3 and the _Value_ as S3 bucket of S3 datastore.
            4. Set _Key_ as METAFLOW_DEFAULT_DATASTORE and _Value_ as _s3_.
            5. Set _Key_ as METAFLOW_DEFAULT_METADATA and _Value_ as _service_.
            6. Set _Key_ as USERNAME and _Value_ as _slackbot_.
            7. Set _Key_ as SLACK_APP_TOKEN and _Value_ as the SLACK_APP_TOKEN retrieved from [slack](./Setup.md#slack-setup).
            8. Set _Key_ as SLACK_BOT_TOKEN and _Value_ as the SLACK_BOT_TOKEN retrieved from [slack](./Setup.md#slack-setup).
            9. If your metadata service has an authentication key to it then Set _Key_ as METAFLOW_SERVICE_AUTH_KEY and value as the authentication token of the metadata service.
        5. Choose Add.
    5. Choose Create.
7. _Choose_ _Clusters_ in the left side pane and select the cluster you created in Step 4.
8. _Choose_ _Create_ under _Services_,
    1. Choose _Fargate_ as _Lauch type_.
    2. Choose the task definition that you created in Step 6. for _Task Definition_. Pick the latest for _Revision_.
    3. For _Platform version_ choose _Latest_.
    4. Leave the _Cluster_ as is (pointing to the cluster that you are configuring).
    5. Pick a name for _Service name_.
    6. *Set 1* for _Number of tasks_.
    7. Choose _Rolling update_ for _Deployment type_.
9. Choose _Next step_.
10. For _Configure network_, 
    1. For _Cluster VPC_, choose the VPC that you have created [previously](#vpc).
    2. Choose the only public subnet.
11. For _Load balancing_, choose None as Load balancer type.
12. For _Auto-assign public IP_ keep it as _ENABLED_. 
13. Choose _Next step_.
14. Leave options in _Set Auto Scaling (optional)_ to the default : _Do not adjust the service’s desired count_
15. Choose _Next step_ and _Create Service_.
16. Choose _View Service_ and wait for the task to get to the running state.
17. Once the task is running, check if the slack bot is responding to messages in DM's or in a channel it is invited to.