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
import logging
import threading

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class RegularIntervalWorker:
    """
    Base class for a worker that executes a specific task in a regular interval.
    """

    def __init__(self, interval: float):
        self._interval = interval
        self._timer = None

    def start(self):
        """
        Starts the worker
        """
        if self._timer is None:
            LOGGER.debug(f"Starting worker: {self.__class__.__name__}")
            self._schedule_next_run()
        else:
            LOGGER.debug("Already running, ignoring start() call")

    def stop(self):
        """
        Stops the worker
        """
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None

    def _schedule_next_run(self):
        """
        Schedules the next run
        """
        if self._timer is not None:
            self._timer.cancel()
        self._timer = threading.Timer(self._interval, self._worker_job)
        self._timer.start()

    def _worker_job(self):
        """
        The regularly executed task. Override this method.
        """
        try:
            self._run()
        except Exception as e:
            LOGGER.error(e, exc_info=True)
        finally:
            self._schedule_next_run()

    def _run(self):
        """
        The regularly executed task. Override this method.
        """
        raise NotImplementedError()
