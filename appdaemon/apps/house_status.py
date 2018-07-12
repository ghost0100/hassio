from enum import Enum
from base import App
from typing import Tuple, Union
from globals import GlobalEvents, HouseModes
from scheduler import run_on_days
import datetime


class HouseStatusManager(App):

    
    _offset_sunrise : int = 0
    _offset_sunset : int = 0

    _early_night_time = datetime.datetime.strptime("23:00:00", "%H:%M:%S")
    _late_night_time = datetime.datetime.strptime("00:15:00", "%H:%M:%S")
    _day_time = datetime.datetime.strptime("10:00:00", "%H:%M:%S")

    _current_state:HouseModes = HouseModes.day

    HOUSE_MODE_SELECT = 'input_select.house_mode_select'

    def initialize(self) -> None:
        """Initialize."""
        super().initialize()
        _current_state = HouseModes(self.get_state(self.HOUSE_MODE_SELECT))

        if 'sunrise_offset' in self.properties:
            _offset_sunrise = int(self.properties['sunrise_offset'])*60
 
        if 'sunset_offset' in self.properties:
            _offset_sunset = int(self.properties['sunset_offset'])*60

        if 'early_night_time' in self.properties:
            _early_night_time = datetime.datetime.strptime(self.properties['early_night_time'], "%H:%M:%S")
   
        if 'late_night_time' in self.properties:
            _late_night_time = datetime.datetime.strptime(self.properties['late_night_time'], "%H:%M:%S")

        if 'day_time' in self.properties:
            _day_time = datetime.datetime.strptime(self.properties['day_time'], "%H:%M:%S")

        self._early_nights = self.args.get('early_nights', {})
        self._late_nights = self.args.get('late_nights', {})

        self.listen_state(
            self.__house_mode_change,
            self.HOUSE_MODE_SELECT,
            attribute='all',
            duration=10
        )

        # Set sunrise/sunset events
        self.run_at_sunrise(self.__on_sunrise, offset=_offset_sunrise)
        self.run_at_sunset(self.__on_sunset, offset=_offset_sunset )

        # Set callback when it is nighttime on days when go to bed early
        run_on_days(
            self,
            self.__on_night_time, self._early_nights,
            _early_night_time.time()
            )

        # Set callback when it is nighttime on days when go to bed late
        run_on_days(
            self,
            self.__on_night_time, self._late_nights,
            _late_night_time.time()
            )

        # Set callback when it is nighttime on days when go to bed late
        self.run_daily(
            self.__on_day_time,
            self._day_time.time()
            )

        self.log("Setting early night-mode on {} at {}".format(self._early_nights, _early_night_time.time()))
        self.log("Setting late night-mode on {} at {}".format(self._late_nights, _late_night_time.time()))
        self.log("Setting day time at {}".format(self._day_time.time()))
        self.log("Next sunset is: {}".format(self.sunset()))
        self.log("Next sunrise is: {}".format(self.sunrise()))

    def is_night(self)->bool:
       # if self.get_state(self.HOUSE_MODE_SELECT) == HouseModes.night.value:
        if self._current_state == HouseModes.night:
            return True
        else:
            return False
    
    def __on_day_time(self, kwargs: dict) -> None:
        """Time to set the house mode to day."""
        
        self.log("DAYTIME EVENT")
        self.set_state(self.HOUSE_MODE_SELECT, state=HouseModes.day.value)

    def __on_night_time(self, kwargs: dict) -> None:
        """Time to set the house mode to night."""
        
        self.log("NIGHTTIME EVENT")
        self.set_state(self.HOUSE_MODE_SELECT, state=HouseModes.night.value)

    
    def __house_mode_change(
            self, entity: Union[str, dict], attribute: str, old: dict,
            new: dict, kwargs: dict) -> None:
        """called when house mode changes"""

        new_mode = HouseModes(new['state']).value
        old_mode = HouseModes(old['state']).value
        self._current_state = HouseModes(new_mode)

        self.fire_event(
            GlobalEvents.HOUSE_MODE_CHANGED.value, 
            old=old_mode, 
            new=new_mode)
    
    def __on_sunrise(self, kwargs: dict):
        """called when sunrise plus offset"""
        self.log("SUNRISE EVENT")
        self.set_state(self.HOUSE_MODE_SELECT, state=HouseModes.morning.value)

    def __on_sunset(self, kwargs: dict):
        """called when sunset plus offset"""
        self.log("SUNSET EVENT")
        self.set_state(self.HOUSE_MODE_SELECT, state=HouseModes.evening.value)
