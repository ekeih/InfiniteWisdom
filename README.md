# InfiniteWisdom
A Telegram bot that sends inspirational quotes of infinite wisdom... 🥠

## Configuration

InfiniteWisdom can be configured either using environment variables
as well as using a yaml file. You can use both methods at the same time, 
however if an option is present in both locations the environment variable
will always override the value provided in the yaml file. 

### Environment variables

| Name                                                  | Description                              | Type     | Default                                |
|-------------------------------------------------------|------------------------------------------|----------|----------------------------------------|
| INFINITEWISDOM_TELEGRAM_BOT_TOKEN                     | The bot token used to authenticate the bot with telegram | String | `-` |
| INFINITEWISDOM_TELEGRAM_GREETING_MESSAGE              | Specifies the message a new user is greeted with | String | `Send /inspire for more inspiration :) Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.` |
| INFINITEWISDOM_TELEGRAM_INLINE_BADGE_SIZE             | Number of items to return in a single inline request badge | Integer | `16` |
| INFINITEWISDOM_CRAWLER_TIMEOUT                        | Timeout in seconds between image api requests | Integer | `1` |
| INFINITEWISDOM_PERSISTENCE_TYPE                       | Type of persistence to use | String | `local` |
| INFINITEWISDOM_PERSISTENCE_PATH                       | pickle persistence file path | String | `/tmp/infinitewisdom.pickle` |
| INFINITEWISDOM_PERSISTENCE_URL                        | SQLAlchemy connection URL | String | `sqlite:////tmp/infinitewisdom.db` |
| INFINITEWISDOM_IMAGE_ANALYSIS_TESSERACT_ENABLED       | Enable/Disable the Tesseract image analyser | Boolean | `False` |
| INFINITEWISDOM_IMAGE_ANALYSIS_GOOGLE_VISION_ENABLED   | Enable/Disable the Google Vision image analyser | Boolean | `False` |
| INFINITEWISDOM_IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE | Path of Google Vision auth file | String | `None` |

### yaml file

The yaml file can be placed in one of the following directories:

- ./infinitewisdom.yaml
- ~/.config/infinitewisdom.yaml
- ~/infinitewisdom.yaml

and looks like this:

```yaml
InfiniteWisdom:
  telegram:
    bot_token: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    greeting_message: "Hi there!"
    inline_badge_size: 16
  crawler:
    timeout: 1
  persistence:
    type: "sql"
    url: "sqlite:////tmp/infinitewisdom.db"
    path: "/home/markus/downloads/dev.pickle"
  image_analysis:
    tesseract:
      enabled: True
    google_vision:
      enabled: False
      auth_file: "./my-auth-file.json"
```

### Persistence

`InfiniteWisdom` supports multiple persistence backends.

#### pickle

```
InfiniteWisdom:
  [...]
  persistence:
    type: "pickle"
    url: "/tmp/infinitewisdom.pickle"
```

#### SQLAlchemy

```
InfiniteWisdom:
  [...]
  persistence:
    type: "sql"
    url: "sqlite:////tmp/infinitewisdom.db"
```

### Image analysis

`InfiniteWisdom` runs basic image analysis on every image available.
This is done to provide search based on the text in the image.

#### Tesseract

You need to make sure that required `tesseract` packages are installed 
on your system to make it work. Have a look at their [documentation](https://github.com/tesseract-ocr/tesseract/wiki).
After all is set configure `InfiniteWisdom` like this:

```
InfiniteWisdom:
  [...]
  image_analysis:
    tesseract:
      enabled: True
```

It should be noted though that the quality of `tesseract` is not very good given
the kind of images that are analysed. Current statistics show that only 
in around2/3 of all images a text is detected and even then it sometimes
is just complete garbage. Better than nothing though!

#### Google Vision

Google Vision has a much higher success rate (no statistics about that yet)
but comes with a price (literally). To use the Google Vision API you
have to create an authentication token for `InfiniteWisdom` to use.
Have a look at the official documentation on how to retrieve that and
then specify it's path in the `InfiniteWisdom` configuration:

```
InfiniteWisdom:
  [...]
  image_analysis:
    google_vision:
      enabled: True
      auth_file: "./googlevision_auth_token.json"
      capacity_per_month: 1000
```

#### Microsoft Computer Vision

Coming...

#### Amazon Rekognition

Coming...

#### Combining Analysers

It's also possible to use multiple analysers at the same time. This
allows you to use the costly Google Vision API for only a specific amount
of images a month and use the free tesseract for the rest. To do that 
simply specify all analysers you want to use next to each other so 
it looks like this:

```
InfiniteWisdom:
  [...]
  image_analysis:
    tesseract:
      enabled: True
    google_vision:
      enabled: True
      auth_file: "./googlevision_auth_token.json"
      capacity_per_month: 1000
    [...]
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