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
| INFINITEWISDOM_BOT_TOKEN                   | The bot token used to authenticate the bot with telegram | String | `-` |
| INFINITEWISDOM_MAX_URL_POOL_SIZE           | Maximum number of URLs to keep in the pool | Integer | `10000` |
| INFINITEWISDOM_IMAGE_POLLING_TIMEOUT       | Timeout in seconds between image api requests | Integer | `1` |
| INFINITEWISDOM_GREETING_MESSAGE            | Specifies the message a new user is greeted with | String | `Send /inspire for more inspiration :) Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.` |
| INFINITEWISDOM_INLINE_BADGE_SIZE           | Number of items to return in a single inline request badge | Integer | `16` |
| INFINITEWISDOM_PERSISTENCE_TYPE            | Type of persistence to use | String | `local` |
| INFINITEWISDOM_PERSISTENCE_PATH            | Path of local persistence | String | `/tmp` |
| INFINITEWISDOM_IMAGE_ANALYSIS_TYPE         | Type of image analysis to use | String | `None` |

### yaml file

The yaml file can be placed in one of the following directories:

- ./infinitewisdom.yaml
- ~/.config/infinitewisdom.yaml
- ~/infinitewisdom.yaml

and looks like this:

```yaml
InfiniteWisdom:
  greeting_message: "Hi there!"
  max_url_pool_size: 10000
  image_polling_timeout: 1
  inline_badge_size: 16
  bot_token: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
  persistence:
    type: "local"
    path: "/tmp"
  image_analysis:
    type: "tesseract"
```

## Usage

Create a configuration as described in the section above and start 
the bot using:

```shell
python ./infinitewisdom/bot.py
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