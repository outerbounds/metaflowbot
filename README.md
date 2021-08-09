# Metaflowbot - Slack Bot for your Metaflow flows!

The Slack bot for Metaflow makes it fun and easy to monitor your Metaflow runs, past and present. Imagine starting a training run that lasts for hours - you can now monitor it anywhere using Slack on your mobile device! You can converse with the bot over direct messages or or invite the bot to a channel.

The bot is [easy to deploy](./docs/deployment.md): It is just a Python process with few external dependencies - no databases needed. Its [security footprint is small](./docs/slack-scopes.md) as it uses only a tightly scoped set of Slack calls. During development you can run the bot on any workstation, so it is quick to [iterate on custom actions](./docs/creating-custom-actions.md) and extend it to suit your needs. For production deployments the bot ships with a [CloudFormation template](./deployment/mfbot-cfn-template.yml) for automating your deployments to AWS.

## Communicating with the bot

There are two ways interact with the Metaflow bot. You can invite the bot on a `channel` or directly speak to it via `direct message`.

- `@flowey help` : Help

- `@flowey tell me a joke`

- `@flowey how to inspect` : How to inspect

- `@flowey inspect HelloFlow` : Inspect `Run`s of a particular `Flow`

- `@flowey inspect savin's HelloFlow`: Inspect `Run`s of a particular `Flow`

- `@flowey inspect savin's HelloFlow tagged some_tag` : Inspect `Run`s of a particular `Flow`

- `@flowey inspect HelloFlow/12` : Inspect an individual `Run` instance

- `@flowey inspect the latest run of HelloFlow` : Inspect an individual `Run` instance

- `@flowey inspect savin's latest run of HelloFlow` : Inspect an individual `Run` instance


If you require some customization for your deployment or need additional help, please feel free to reach out to us at http://slack.outerbounds.co. We are very happy to help!
