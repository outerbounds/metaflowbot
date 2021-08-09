# Create Your Own Bot Action
The initial version of the bot ships with actions that allow you to monitor the status of Metaflow runs, past and present. Imagine starting a training run that lasts for hours - you can now monitor it anywhere using Slack on your mobile device! You can converse with the bot over direct messages or or invite the bot to a channel.

With the diversity of machine learning and data science use cases, we have wanted to make it easy to extend the bot with new actions. As an example, we ship a [simple jokes command](https://github.com/outerbounds/metaflowbot-jokes-action) :clown_face:. You can use it as a template to create custom actions which can be enabled just by doing a `pip install`. We would love to see people contributing actions of all kinds - please share with us (http://slack.outerbounds.co) if you have any ideas or prototypes!


### How To Create Your Own Bot Action
Create your own custom action by creating a Python package with the following folder structure -

```
your_bot_action/ # the name of this dir doesn't matter
├ setup.py
├ metaflowbot/ # namespace package name
│  └ __init__.py       # special pkgutil namespace __init__.py
│  └ action/      # namespace sub package name
│      ├__init__.py    # special pkgutil namespace __init__.py
│      └ your-special-acton/            # dir name must match the package name in `setup.py`
│        └ __init__.py  # Contains a prespecified code block given below
│        └ rules.yml.   # This mandatory to create rules
│        └ commands.py. # This create main commands from click
.
```

Every module must contain a `rules.yml`, a `__init__.py`, and a module that contains click commands imported from `metaflowbot.cli.actions`. Every rule in the `rules.yml` should follow [this](./architecture.md##Rule) structure

The `__init__.py` inside an installable action must contain the following code to integrate with `metaflowbot`'s actions
```python
import pkgutil

from metaflowbot.rules import MFBRules

data = pkgutil.get_data(__name__, "rules.yml")
RULES = MFBRules.make_subpackage_rules(data)
from . import commands
```

#### Locally Development

Export the slack tokens as environment variables :

```sh
export SLACK_APP_TOKEN=xapp-1-AAAAAAAAAAA-2222222222222-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
export SLACK_BOT_TOKEN=xoxb-2222222222222-2222222222222-AAAAAAAAAAAAAAAAAAAAAAAA
```

- Install `metaflowbot` repository and install your custom development repo; ensure you have set the `PYTHONPATH` correctly so that `metaflowbot` can be resolved. 

```sh
pip install metaflowbot
pip install -e ./<PATH_TO_metaflowbot_action_directory>
```

- If you are running the bot locally with a local metadata provider, then run the above command inside the directory where the `.metaflow` folder is present.
