import json


class ResponseAction:
    """
    Abstract class for all response actions
    """
    action = None
    options = {}

    def _snake_case_to_camel(self, name):
        """
        Convert snake_case into camelCase.
        :param name: the option key to be converted
        :rtype: str
        """
        words = name.split('_')
        if words and len(words) > 1:
            return words[0] + ''.join(w.title() for w in words[1:])
        return name.lower()

    def __init__(self, action, **kwargs):
        """
        :param action: name of the action
        """
        self.action = action
        self.add_options(kwargs)

    def add_option(self, name, value):
        """
        Add an option to the current Action.

        :param name: name of the option (must be in snake case format)
        :param value: the value of the option
        """

        # All the key in Nexmo Call Control Objects are in camelCases,
        # but to conform to python variable naming we are using snake_case.
        # This method will convert all property names from snake_case to camelCase
        key = self._snake_case_to_camel(name)
        self.options[key] = value

    def add_options(self, **kwargs):
        """
        Add multiple options to the current Action

        :param kwargs: the list of the options
        """
        for k, v in kwargs.items():
            self.add_option(k, v)

    def clear_options(self):
        """
        Remove all options already added.
        """
        self.options.clear()

    def __dict__(self):
        """
        Get the options dictionary

        :rtype: dict
        """
        options = self.options or {}
        options.update({
            'action': self.action,
        })
        return options


class Talk(object, ResponseAction):
    # region [ Voice Choices ]
    VOICE_CHOICES = (
        ('Salli', 'Salli - en-US female'),
        ('Joey', 'Joey - en-US male'),
        ('Naja', 'Naja - da-DK femaleMads - da-DK male'),
        ('Marlene', 'Marlene - de-DE female'),
        ('Hans', 'Hans - de-DE male'),
        ('Nicole', 'Nicole - en-AU female'),
        ('Russell', 'Russell - en-AU male'),
        ('Amy', 'Amy - en-GB female'),
        ('Brian', 'Brian - en-GB male'),
        ('Emma', 'Emma - en-GB female'),
        ('Gwyneth', 'Gwyneth - en-GB-WLS female'),
        ('Geraint', 'Geraint - en-GB-WLS male'),
        ('Raveena', 'Raveena - en-IN female'),
        ('Chipmunk', 'Chipmunk - en-US male'),
        ('Eric', 'Eric - en-US male'),
        ('Ivy', 'Ivy - en-US female'),
        ('Jennifer', 'Jennifer - en-US female'),
        ('Justin', 'Justin - en-US male'),
        ('Kendra', 'Kendra - en-US female'),
        ('Kimberly', 'Kimberly - en-US female'),
        ('Conchita', 'Conchita - es-ES female'),
        ('Enrique', 'Enrique - es-ES male'),
        ('Penelope', 'Penelope - es-US female'),
        ('Miguel', 'Miguel - es-US male'),
        ('Chantal', 'Chantal - fr-CA female'),
        ('Celine', 'Celine - fr-FR female'),
        ('Mathieu', 'Mathieu - fr-FR male'),
        ('Dora', 'Dora - is-IS female'),
        ('Karl', 'Karl - is-IS male'),
        ('Carla', 'Carla - it-IT female'),
        ('Giorgio', 'Giorgio - it-IT male'),
        ('Liv', 'Liv - nb-NO female'),
        ('Lotte', 'Lotte - nl-NL female'),
        ('Ruben', 'Ruben - nl-NL male'),
        ('Agnieszka', 'Agnieszka - pl-PL female'),
        ('Jacek', 'Jacek - pl-PL male'),
        ('Ewa', 'Ewa - pl-PL female'),
        ('Jan', 'Jan - pl-PL male'),
        ('Maja', 'Maja - pl-PL female'),
        ('Vitoria', 'Vitoria - pt-BR female'),
        ('Ricardo', 'Ricardo - pt-BR male'),
        ('Cristiano', 'Cristiano - pt-PT male'),
        ('Ines', 'Ines - pt-PT female'),
        ('Carmen', 'Carmen - ro-RO female'),
        ('Maxim', 'Maxim - ru-RU male'),
        ('Tatyana', 'Tatyana - ru-RU female'),
        ('Astrid', 'Astrid - sv-SE female'),
        ('Filiz', 'Filiz - tr-TR female'),
    )
    # endregion

    def __init__(self, text, barge_in=False, loop=1, voice_name='Kimberly', **kwargs):
        """
        Text-to-speech action.

        :type text: str
        :param text: the text
        :type barge_in: bool
        :param barge_in: set this to true to interrupt the voice before the talk command is finished.
                            This action must be followed by an input action.
        :type loop: int
        :param loop: The number of times text is repeated before the Call is closed. The default value is 1.
                            Set to 0 to loop infinitely.
        :param voice_name: The name of the voice used to deliver text. See Talk.VOICE_CHOICES for the list of choices.
        :param kwargs: any additional options.
        """
        action = 'talk'
        super(Talk, self).__init__(action)
        if barge_in:
            self.add_options(barge_in=barge_in)
        self.add_options(text=text, loop=loop, voice_name=voice_name, **kwargs)



class Response:
    JSON_MIME = 'application/json'

    actions = None
    pretty = False

    def __init__(self, pretty=False):
        self.actions = []
        self.pretty = pretty

    def add_action(self, action):
        """
        Add an action to this response.

        :type action: ResponseAction
        :param action: the action instance
        """
        self.actions.append(action)

    def get_json_string(self):
        options = {}
        if self.pretty:
            options['indent'] = 4

        response = self.actions
        return json.dumps(response, **options)
