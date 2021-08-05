# Metaflow bot docker file
FROM python:3.7.2
ADD . /metaflowbot
RUN pip3 install /metaflowbot/.
RUN pip3 install metaflowbot-actions-jokes
CMD python3 -m metaflowbot --slack-bot-token $(echo $SLACK_BOT_TOKEN) server --admin $(echo $ADMIN_USER_ADDRESS)
