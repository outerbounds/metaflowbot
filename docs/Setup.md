# Deploying the Metaflowbot

Deploying the Metaflowbot involves -
1. [Setting up the Metaflowbot on Slack](#setting-up-the-metaflowbot-on-slack), and
2. [Running the Metaflowbot server](#running-the-metaflowbot-server)
    - [locally with pip](#locally-with-pip)
    - [via a docker image](#via-a-docker-image)
    - on AWS:
        - [with AWS CloudFormation](./CF-Deployment.md)
        - [manually](./Deployment-Manual.md)

## Setting up the Metaflowbot on Slack

1. [Create an App on Slack UI](https://api.slack.com/apps) using the provided [manifest](../manifest.yml). The default name of the Metaflowbot is `@flowey`. To customize the name of the Metaflowbot, change `display_information.name` and `bot_user.display_name` in the [manifest](../manifest.yml). 

    ![](images/slacksetup.png)

2. Install the App
    ![](images/app_install.png)

3. Generate an App token (`SLACK_APP_TOKEN`): This token allows the Metaflowbot to make a socket connection to Slack and will be used later to configure the bot.
    ![](images/app-token.png)

4. Generate Bot token (`SLACK_BOT_TOKEN`) : This token allows the Metaflowbot to make web API calls and will be used later to configure the bot.
    ![](images/bot-token.png)

## Running the Metaflowbot server

### locally with pip

The Metaflowbot server is available as a [pip package from PyPI](https://pypi.org/project/metaflowbot/) and can be directly invoked.

1. Install `metaflowbot` Python package from PyPI
    
    ```sh
    pip install metaflowbot
    pip install metaflowbot-actions-jokes # Optional dependency
    ```

2. Launch the Metaflowbot server by providing `--admin` argument with the email address of your slack account; Metaflowbot will open a message thread with you to maintain it's state (as a poor man's database). Replace `SLACK_APP_TOKEN` & `SLACK_BOT_TOKEN` with the values obtained while [setting up the Metaflowbot on Slack](#setting-up-the-metaflowbot-on-slack).
    
    ```sh
    SLACK_APP_TOKEN=xapp-foo SLACK_BOT_TOKEN=xoxb-bar python -m metaflowbot server --admin me@server.com
    ```

### via a docker image

The Metaflowbot server is also available as a docker image from [Docker Hub](https://hub.docker.com/repository/docker/outerbounds/metaflowbot). There are multiple ways to configure the image; just ensure that `ADMIN_USER_ADDRESS` environment variable points to your email address in the Slack workspace -

- through environment variables
```sh
docker run -i -t --rm \
    -e SLACK_BOT_TOKEN=$(echo $SLACK_BOT_TOKEN) \
    -e ADMIN_USER_ADDRESS=admin@server.com \
    -e SLACK_APP_TOKEN=$(echo $SLACK_APP_TOKEN) \
    -e AWS_SECRET_ACCESS_KEY=$(echo $AWS_SECRET_ACCESS_KEY) \
    -e AWS_ACCESS_KEY_ID=$(echo $AWS_ACCESS_KEY_ID) \
    -e USERNAME=metaflowbot \
    -e METAFLOW_SERVICE_AUTH_KEY=$(echo $METAFLOW_SERVICE_AUTH_KEY) \
    -e METAFLOW_SERVICE_URL=$(echo $METAFLOW_SERVICE_URL) \
    -e METAFLOW_DATASTORE_SYSROOT_S3=$(echo $METAFLOW_DATASTORE_SYSROOT_S3) \
    -e METAFLOW_DEFAULT_DATASTORE=s3 \
    -e METAFLOW_DEFAULT_METADATA=service \
    outerbounds/metaflowbot
```

- through `~/.metaflowconfig`. 
```sh
docker run -it \
    -v ~/.metaflowconfig:/metaflowconfig --rm \
    -e SLACK_BOT_TOKEN=$(echo $SLACK_BOT_TOKEN) \
    -e ADMIN_USER_ADDRESS=admin@server.com \
    -e SLACK_APP_TOKEN=$(echo $SLACK_APP_TOKEN) \
    -e AWS_SECRET_ACCESS_KEY=$(echo $AWS_SECRET_ACCESS_KEY) \
    -e AWS_ACCESS_KEY_ID=$(echo $AWS_ACCESS_KEY_ID) \
    -e USERNAME=metaflowbot \
    -e METAFLOW_HOME=/.metaflowconfig \
    outerbounds/metaflowbot
```
