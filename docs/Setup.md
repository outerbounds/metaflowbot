# Metaflow Bot Setup

The setup follows two parts.
1. The first part is setting up the bot on Slack to get access tokens.
2. The second part is running the Bot server manually or via a docker image or [AWS ECS](./Deployment.md).
## Slack Setup

1. [Create an App on Slack UI](https://api.slack.com/apps) using provided [manifest](../manifest.yml).

    ![](images/slacksetup.png)

2. Install the App
    ![](images/app_install.png)

3. Generate App token : This token allows the bot to make a socket connection to slack
    ![](images/app-token.png)

4. Generate Bot token : This token allows the bot to make web API calls.
    ![](images/bot-token.png)

## Running the Bot


### From pip

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
    ``sh
    python -m metaflowbot server --admin me@server.com
    ```
### Running Via Docker Image

Use the below command for running the bot container instance on local. You can shed some metaflow variables and load a volume to the `~./metaflowconfig` to set Metaflow config related variables.

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
        outerbounds/metaflowbot
    ```
