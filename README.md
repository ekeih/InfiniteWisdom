# InfiniteWisdom
A Telegram bot that sends inspirational quotes of infinite wisdom... 🥠

<img src="phone_screenshot.jpg" width="480">

## Configuration

InfiniteWisdom can be configured either using environment variables
as well as using a yaml file. You can use both methods at the same time, 
however if an option is present in both locations the environment variable
will always override the value provided in the yaml file. 

### Environment variables

| Name                                                  | Description                              | Type     | Default                                |
|-------------------------------------------------------|------------------------------------------|----------|----------------------------------------|
| INFINITEWISDOM_TELEGRAM_BOT_TOKEN                     | The bot token used to authenticate the bot with telegram | `str` | `-` |
| INFINITEWISDOM_TELEGRAM_GREETING_MESSAGE              | Specifies the message a new user is greeted with | `str` | `Send /inspire for more inspiration :) Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.` |
| INFINITEWISDOM_TELEGRAM_INLINE_BADGE_SIZE             | Number of items to return in a single inline request badge | `int` | `16` |
| INFINITEWISDOM_CRAWLER_INTERVAL                       | Interval in seconds for image api requests | `float` | `1` |
| INFINITEWISDOM_PERSISTENCE_TYPE                       | Type of persistence to use | `str` | `sql` |
| INFINITEWISDOM_PERSISTENCE_PATH                       | pickle persistence file path | `str` | `/tmp/infinitewisdom.pickle` |
| INFINITEWISDOM_PERSISTENCE_URL                        | SQLAlchemy connection URL | `str` | `sqlite:////tmp/infinitewisdom.db` |
| INFINITEWISDOM_IMAGE_ANALYSIS_INTERVAL                | Interval in seconds for image analysis | `float` | `1` |
| INFINITEWISDOM_IMAGE_ANALYSIS_TESSERACT_ENABLED       | Enable/Disable the Tesseract image analyser | `bool` | `False` |
| INFINITEWISDOM_IMAGE_ANALYSIS_GOOGLE_VISION_ENABLED   | Enable/Disable the Google Vision image analyser | `bool` | `False` |
| INFINITEWISDOM_IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE | Path of Google Vision auth file | `str` | `None` |
| INFINITEWISDOM_IMAGE_ANALYSIS_GOOGLE_VISION_CAPACITY_PER_MONTH | Maximum amount of images to analyse using Google Vision in a month | `str` | `1000` |

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
    interval: 1
  persistence:
    type: "sql"
    url: "sqlite:///infinitewisdom.db"
  image_analysis:
    interval: 1
    tesseract:
      enabled: True
    google_vision:
      enabled: False
      auth_file: "./my-auth-file.json"
      capacity_per_month: 1000
```

### Crawler

The crawler queries the image api source ([http://inspirobot.me](http://inspirobot.me))
for random images and adds them to the persistence if they don't exist yet.
To not overwhelm the api it is queried in a specific interval so there 
is a slight delay between each request.

```
InfiniteWisdom:
  [...]
  crawler:
    interval: 1
```

### Persistence

The persistence is used to store image url's, image analysis data
and other meta data related to images. 
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
    url: "sqlite:///infinitewisdom.db"
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