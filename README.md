# Metaflow Bot

## Setup 
Setup related docs are present [here](./docs/Setup.md)
## Documentation
Thorough Documentation is present in the [Documentation folder](./docs)
## Bot Commands

- `@flowey help` | `@flowey hi` : Help

- `@flowey tell me a joke`

- `@flowey inspect` | `@flowey how to inspect` : How to inspect

- `@flowey inspect HelloFlow` : Inspect `Run`s of a particular `Flow`

- `@flowey inspect savin's HelloFlow`: Inspect `Run`s of a particular `Flow`

- `@flowey inspect savin's HelloFlow tagged some_tag` : Inspect `Run`s of a particular `Flow`

- `@flowey inspect HelloFlow/12` : Inspect an individual `Run` instance

- `@flowey inspect the latest run of HelloFlow` : Inspect an individual `Run` instance

- `@flowey inspect dberg's latest run of HelloFlow` : Inspect an individual `Run` instance


## Communicating with the bot

There are two ways interact with the Metaflow bot. You can invite the bot on a `channel` or directly speak to it via `direct message`. For either of the two ways, the following is the general behavior of the bot:

> *When a user messages the bot, the bot will open a new message thread and will engage with the user on the same thread. The user can open multiple threads with the bot. Each thread is an independent discussion*

The following are interaction/UX restrictions based on where the user is conversing with the Metaflow bot.
### Communicating with the bot on a channel

The current [manifest.yml](./manifest.yml) only supports `app_mention` and `message.im` events. This means that users need to specifically mention `@flowey` or `@custombotname` before a command when the bot is invited to a channel. This constraint ensures we don't listen to *all* messages on a channel; only the ones where the bot is called.

### Communicating with the bot through direct messages

Users can message the bot without `@` mentions via direct messages. The bot will support the same command list.

## References:

- [Slack Permission Scopes](https://api.slack.com/scopes)
- [Slack Events](https://api.slack.com/events)
- [Slack Socket Mode](https://slack.dev/python-slack-sdk/socket-mode/index.html#socketmodeclient)
- [How to make threads in slack via python API](https://slack.dev/python-slack-sdk/web/index.html)
