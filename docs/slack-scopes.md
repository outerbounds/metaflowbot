# Slack Permission Scopes
Current Permission Scopes in use by Metaflowbot.

| Oauth Permissions | Scope meaning                                                                             | Why Needed                                                                         | Needed | Link                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------- |
| app_mentions:read | View messages that directly mention @your\_slack\_app in conversations that the app is in | Main event that for channel related triggers                                       | Yes    | [https://api.slack.com/scopes/app\_mentions:read](https://api.slack.com/scopes/app_mentions:read) |
| channels:manage   | Manage public channels that your slack app has been added to and create new ones          | For `conversations.open` method for chat responses                                 | Yes    | [https://api.slack.com/scopes/channels:manage](https://api.slack.com/scopes/channels:manage)      |
| channels:read     | View basic information about public channels in a workspace                               | Needed for `conversations.replies`                                                 | Yes    | [https://api.slack.com/scopes/channels:read](https://api.slack.com/scopes/channels:read)          |
| chat:write        | Post messages in approved channels & conversations                                        | Needed For [Post Message Function](https://api.slack.com/methods/chat.postMessage) | Yes    | [https://api.slack.com/scopes/chat:write](https://api.slack.com/scopes/chat:write)                |
| im:read           | View basic information about direct messages that your slack app has been added to        | To Read IMs being sent                                                             | Yes    | [https://api.slack.com/scopes/im:read](https://api.slack.com/scopes/im:read)                      |
| im:write          | Start direct messages with people                                                         | To write to Im channels for admin and others                                       | Yes    | [https://api.slack.com/scopes/im:write](https://api.slack.com/scopes/im:write)                    |
| im:history        | View messages and other content in direct messages that your slack app has been added to  | For state retieval                                                                 | Yes    | [https://api.slack.com/scopes/im:history](https://api.slack.com/scopes/im:history)                |
| users:read.email  | View email addresses of people in a workspace                                             | For Reading admin user's email for DM's                                            | Yes    | [https://api.slack.com/scopes/users:read.email](https://api.slack.com/scopes/users:read.email)    |
| users:read        | View people in a workspace                                                                | Needed with `users.reademail` scope                                                | Yes    | [https://api.slack.com/scopes/users:read](https://api.slack.com/scopes/users:read)                |

# Slack Event Subsciptions

1. [`app_metion`](https://api.slack.com/events/app_mention) : To get events when `@` mentioned on channel.  
2. [`message.im`](https://api.slack.com/events/message.im) : To get direct message events 

# Slack API Rate Limits



| Where is it Needed                                                          | API Call              | Links                                               | Rate Limt Tier               |
|:--------------------------------------------------------------------------- |:--------------------- |:--------------------------------------------------- |:---------------------------- |
| To send messages via Slack client                                           | chat_postMessage      | https://api.slack.com/methods/chat.postMessage      | 1 message/per channel/second |
| To read messages from Slack admin channel (Figure sec around this)          | conversations_history | https://api.slack.com/methods/conversations.history | 50 Req/min                   |
| To read the Slack admin channel thread for the bot (Figure sec around this) | conversations_replies | https://api.slack.com/methods/conversations.replies | 50 Req/min                   |
| To create threads with the bot                                                  | conversations_open    | https://api.slack.com/methods/conversations.open    | 50 Req/min                   |
