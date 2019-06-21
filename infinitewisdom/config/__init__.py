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


class ConfigEntry:

    def __init__(self, yaml_path: [str], default: any = None, none_allowed: bool = None):
        """
        Creates a config entry
        :param yaml_path: list of strings representing the yaml tree path for this entry
        :param default: the default value
        :param none_allowed: Set to True if a 'None' value may be allowed, False if not,
                             otherwise it will be True if the default value is not None.
        """
        self.yaml_path = yaml_path
        self.env_key = "_".join(yaml_path).upper()

        if none_allowed is None:
            none_allowed = default is None
        self._none_allowed = none_allowed

        self.default = self._parse_value(default)
        self._value = default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = self._parse_value(new_value)

    def _parse_value(self, value: any) -> any:
        """
        Tries to permissively convert the given value to the expected value type.
        :param value: the value to parse
        :return: the parsed value
        """
        if value is None:
            if self._none_allowed:
                return None
            else:
                self._raise_invalid_value(value)

        try:
            return self._value_to_type(value)
        except:
            self._raise_invalid_value(value)

    def _value_to_type(self, value: any) -> any:
        raise NotImplementedError()

    def _raise_invalid_value(self, value: any):
        raise ValueError("Invalid value '{}' for config option {}".format(value, self.env_key))


class StringConfigEntry(ConfigEntry):

    def _value_to_type(self, value: any) -> any:
        s = str(value)
        if self._none_allowed:
            if s.lower() in ['none', 'null', 'nil']:
                return None

        return s


class BoolConfigEntry(ConfigEntry):

    def _value_to_type(self, value: any) -> any:
        if type(value) == bool:
            return value
        else:
            s = str(value).lower()

            if s in ['y', 'yes', 'true', 't', '1']:
                return True
            elif s in ['n', 'no', 'false', 'f', '0']:
                return False
            else:
                self._raise_invalid_value(value)


class IntConfigEntry(ConfigEntry):

    def _value_to_type(self, value: any) -> any:
        return int(value)


class FloatConfigEntry(ConfigEntry):

    def _value_to_type(self, value: any) -> any:
        return float(value)
