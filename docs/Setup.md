# Metaflow Bot Setup

The setup follows two parts.

1. Setting up the bot on [Slack to get access tokens](##slack-setup).
2. Running the bot server 
    - [Locally with pip](###running-the-bot-locally-with-pip)
    - [Via a docker image](###running-the-bot-with-docker)
    - On AWS:
        - [CloudFormation](./CF-Deployment.md)
        - [Manual Deployment](./Deployment-Manual.md)
## Slack setup

1. [Create an App on Slack UI](https://api.slack.com/apps) using provided [manifest](../manifest.yml).

    ![](images/slacksetup.png)

2. Install the App
    ![](images/app_install.png)

3. Generate App token : This token allows the bot to make a socket connection to slack
    ![](images/app-token.png)

4. Generate Bot token : This token allows the bot to make web API calls.
    ![](images/bot-token.png)

## Running the Bot

### Running the bot locally with pip

1. Export the tokens as environment variables :
    
    ```sh
    export SLACK_APP_TOKEN=xapp-1-AAAAAAAAAAA-2222222222222-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    export SLACK_BOT_TOKEN=xoxb-2222222222222-2222222222222-AAAAAAAAAAAAAAAAAAAAAAAA
    ```
2. Install `metaflowbot`
    
    ```sh
    pip install metaflowbot
    pip install metaflowbot-actions-jokes # Custom action install
    ```

3. Run the BOT by providing `--admin` argument with admin user's email address; The bot will open a message thread with the admin user where the bot will maintain state related information.
    
    ```sh
    python -m metaflowbot server --admin me@server.com
    ```
### Running the bot with docker

You can run the bot with docker using either environment variables or loading the `~/.metaflowconfig` as a volume.

1. Running docker container using environment variables
```sh
docker run -i -t --rm \
    -e SLACK_BOT_TOKEN=$(echo $SLACK_BOT_TOKEN) \
    -e ADMIN_USER_ADDRESS=admin@server.com \
    -e SLACK_APP_TOKEN=$(echo $SLACK_APP_TOKEN) \
    -e AWS_SECRET_ACCESS_KEY=$(echo $AWS_SECRET_ACCESS_KEY) \
    -e AWS_ACCESS_KEY_ID=$(echo $AWS_ACCESS_KEY_ID) \
    -e USERNAME=$(echo $USERNAME) \
    -e METAFLOW_SERVICE_AUTH_KEY=$(echo $METAFLOW_SERVICE_AUTH_KEY) \
    -e METAFLOW_SERVICE_URL=$(echo $METAFLOW_SERVICE_URL) \
    -e METAFLOW_DATASTORE_SYSROOT_S3=$(echo $METAFLOW_DATASTORE_SYSROOT_S3) \
    -e METAFLOW_DEFAULT_DATASTORE=s3 \
    -e METAFLOW_DEFAULT_METADATA=service \
    outerbounds/metaflowbot
```

2. Running docker container using volume attachment for `~/.metaflowconfig`. 
```sh
docker run -it \
    -v ~/.metaflowconfig:/metaflowconfig --rm \
    -e SLACK_BOT_TOKEN=$(echo $SLACK_BOT_TOKEN) \
    -e ADMIN_USER_ADDRESS=valay@outerbounds.co \
    -e SLACK_APP_TOKEN=$(echo $SLACK_APP_TOKEN) \
    -e AWS_SECRET_ACCESS_KEY=$(echo $AWS_SECRET_ACCESS_KEY) \
    -e AWS_ACCESS_KEY_ID=$(echo $AWS_ACCESS_KEY_ID) \
    -e USERNAME=slackbot \
    -e METAFLOW_HOME=/.metaflowconfig \
    outerbounds/metaflowbot
```