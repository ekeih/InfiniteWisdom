# InfiniteWisdom
A Telegram bot that sends inspirational quotes of infinite wisdom... 🥠

## Configuration

InfiniteWisdom can be configured either using environment variables
as well as using a yaml file. You can use both methods at the same time, 
however if an option is present in both locations the environment variable
will always override the value provided in the yaml file. 

### Environment variables

| Name                        | Description                              | Type     | Default                                |
|-----------------------------|------------------------------------------|----------|----------------------------------------|
| BOT_TOKEN                   | The bot token used to authenticate the bot with telegram | String | `-` |
| URL_POOL_SIZE               | Maximum number of URLs to keep in the pool | Integer | `10000` |
| IMAGE_POLLING_TIMEOUT       | Timeout in seconds between image api requests | Integer | `1` |
| GREETINGS_MESSAGE           | Specifies the message a new user is greeted with | String| `Send /inspire for more inspiration :) Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.` |

### yaml file

The yaml file can be placed in one of the following directories:

- ./infinitewisdom.yaml
- ~/.config/infinitewisdom.yaml
- ~/infinitewisdom.yaml

and looks like this:

```
InfiniteWisdom:
  bot_token: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
  greetings_message: "Hi there!"
  max_url_pool_size: 10000
  image_polling_timeout: 1
```

## Usage

Create a configuration as described in the section above and start 
the bot using:

```
python ./bot.py
```

## Attributions
Many thanks to the authors of [http://inspirobot.me](http://inspirobot.me)
where all the images from this bot are coming from.

# License

```text
# InfiniteWisdomBot - A Telegram bot that sends inspirational quotes of infinite wisdom...
# Copyright (C) 2019  Max Rosin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
```