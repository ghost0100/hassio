from base import Base
from globals import PEOPLE
from globals import HouseModes
import secrets

"""
Class NotificationManager handles sending notifications to a person

Following features are implemented:

- send a notification to a persons device/s
- send a greeting phrase combined with message to a persons device/s

"""
class NotificationManager(Base):

    def initialize(self) -> None:
        """Initialize."""
        super().initialize() # Always call base class
        
    def notify(self, person:str, title:str='', message:str='')->None:
        """Notify using a persons notifiers"""
        for notifier in PEOPLE[person]['notifiers']:
            self.call_service("notify/{}".format(notifier), title=title, message=message)
    
    def greeting(self, person:str, title:str='', message:str='')->None:
        """Adds a greeting phrase to the message before sending it"""
        greeting = "{} {}, {} {}".format(self.__start_greeting(), person, self.__start_inform(), message)
        self.notify(person, title, greeting)

    def __start_greeting(self)->str:
        """Greeting phrase"""
        start_phrase = []
        if self.house_status.current_state == HouseModes.day:
            start_phrase = ['Goddag', 'Hej', 'Hallå' ]              #Good day, hi, hello
        elif self.house_status.current_state == HouseModes.morning:
            start_phrase = ['God morgon', 'Hej', 'Hallå' ]          #Good morning, hi, hello
        elif self.house_status.current_state == HouseModes.evening:
            start_phrase = ['Godkväll', 'Hej', 'Hallå' ]            #Good evening, hi, hello
        elif self.house_status.current_state == HouseModes.night:
            start_phrase = ['Ursäkta jag stör', 'Hej', 'Hallå' ]    #Sorry to bother, hi, hello

        # return random choice from list/array
        return secrets.choice(start_phrase)

    def __start_inform(self)->str:
        return secrets.choice(
            [
                'jag vill bara informera att',  #I want to inform that
                'det är så att',                #The thing is
                'för din information så',       #for your information
                'du ville att jag skulle informera att' #I want to inform that
            ]
        )