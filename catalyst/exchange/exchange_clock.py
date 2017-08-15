#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from time import sleep

from logbook import Logger
import pandas as pd

from catalyst.gens.sim_engine import (
    BAR,
    SESSION_START,
    SESSION_END,
    MINUTE_END,
    BEFORE_TRADING_START_BAR
)

log = Logger('ExchangeClock')


class ExchangeClock(object):
    """Realtime clock for live trading.

    This class is a drop-in replacement for
    :class:`zipline.gens.sim_engine.MinuteSimulationClock`.

    This is a stripped down version because crypto exchanges run around the clock.

    The :param:`time_skew` parameter represents the time difference between
    the Broker and the live trading machine's clock.
    """

    def __init__(self,
                 sessions=None,
                 execution_opens=None,
                 execution_closes=None,
                 before_trading_start_minutes=None,
                 minute_emission=False,
                 time_skew=pd.Timedelta("0s")):

        self.sessions = sessions
        self.execution_opens = execution_opens
        self.execution_closes = execution_closes
        self.before_trading_start_minutes = before_trading_start_minutes
        self.minute_emission = minute_emission
        self.time_skew = time_skew
        self._last_emit = None
        self._before_trading_start_bar_yielded = True

    def __iter__(self):
        yield pd.Timestamp.utcnow(), SESSION_START

        while True:
            current_time = pd.Timestamp.utcnow()
            server_time = current_time.floor('1 min')

            if self._last_emit is None or server_time > self._last_emit:

                print 'emitting bar %s' % server_time
                self._last_emit = server_time
                yield server_time, BAR

                if self.minute_emission:
                    yield server_time, MINUTE_END

            else:
                sleep(1)
