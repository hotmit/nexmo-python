import json
import warnings

try:
    from django.http import HttpResponse
except Exception as ex:
    HttpResponse = None


class RequestAction(object):
    """
    Abstract class for all request actions
    """
    action = None
    options = None


    def _snake_case_to_camel(self, name):
        """
        Convert snake_case into camelCase.

        :param name: The option key to be converted
        :rtype: str
        """
        words = name.split('_')
        if words and len(words) > 1:
            return words[0] + ''.join(w.title() for w in words[1:])
        return name.lower()

    def __init__(self, action, **kwargs):
        """
        :param action: Name of the action
        """
        self.action = action
        self.options = {}
        self.add_options(skip_none_value=False, **kwargs)

    def add_lists(self, sub_type=None, skip_none_value=True, **kwargs):
        """
        Add a list as an option.

        :param skip_none_value: If value is None, don't add to the options
        :param kwargs: The name=list pairs
        """
        for name, the_list in kwargs.items():
            if skip_none_value and the_list is None:
                continue
            if sub_type is not None:
                if filter(lambda itm: not isinstance(itm, sub_type), the_list):
                    raise ValueError('"{name}" is must be a list of "{type}"'
                                 .format(name=name, type=sub_type))

            if the_list and not isinstance(the_list, list):
                raise ValueError('"{name}" is must be a list, but got "{type}" instead.'
                                 .format(name=name, type=type(the_list)))
            self.add_option(name, the_list)

    def add_dict(self, skip_none_value=True, **kwargs):
        """
        Add a dict as an option.

        :param skip_none_value: If value is None, don't add to the options
        :param kwargs: the name=list pairs
        """
        for name, the_dict in kwargs.items():
            if skip_none_value and the_dict is None:
                continue
            if the_dict and not isinstance(the_dict, list):
                raise ValueError('"{name}" is must be a dict, but got "{type}" instead.'
                                 .format(name=name, type=type(the_dict)))
            self.add_option(name, the_dict)

    def add_option(self, name, value):
        """
        Add an option to the current Action.

        :param name: Name of the option (must be in snake case format)
        :param value: The value of the option
        """
        if name != name.lower():
            warning_msg = 'The option name must be in snake_case format. Expect snake_case but got this "%s".' % name
            warnings.warn(warning_msg, stacklevel=2)

        if name == '_from':
            name = 'from'

        # All the key in Nexmo Call Control Objects are in camelCases,
        # but to conform to python variable naming we are using snake_case.
        # This method will convert all property names from snake_case to camelCase
        key = self._snake_case_to_camel(name)

        if isinstance(value, bool):
            # all boolean values in NCCO are string
            value = str(value).lower()

        self.options[key] = value

    def add_options(self, skip_none_value=True, **kwargs):
        """
        Add multiple options to the current Action

        :param kwargs: The list of the options
        """
        if kwargs:
            for k, v in kwargs.items():
                if skip_none_value and v is None:
                    continue
                self.add_option(k, v)

    def clear_options(self):
        """
        Remove all options already added.
        """
        self.options.clear()

    def _get_dict(self):
        """
        Get the options dictionary

        :rtype: dict
        """
        options = self.options or {}
        options.update({
            'action': self.action,
        })
        return options

    def __iter__(self):
        return self._get_dict().iteritems()


class Record(RequestAction):
    def __init__(self, event_url=None, event_method='POST', format='mp3', end_on_silence=None, end_on_key=None,
                 time_out=None, beep_start=None, **kwargs):
        """
        Record a conversation.

        :type event_url: list<str>
        :param event_url: The list of URLs to the webhook endpoint that is called asynchronously when a
                            recording is finished.
        :param event_method: [POST|GET]
        :param format: [mp3|wav]
        :type  end_on_silence: int
        :param end_on_silence: Top recording after n seconds of silence. Once the recording is stopped the recording
                            data is sent to event_url. The range of possible values is 3<=endOnSilence<=10.
        :type end_on_key: str
        :param end_on_key: Stop recording when a digit is pressed on the handset. Possible values are: [0-9*#]
        :type time_out: int
        :param time_out: The maximum length of a recording in seconds. One the recording is stopped the recording
                            data is sent to event_url. The range of possible values is 3<=timeOut<=7200
        :type beep_start: bool
        :param beep_start: Set to true to play a beep when a recording starts
        :param kwargs: Any additional options (make sure the keys are in snake_case format).
        """

        action = 'record'
        super(Record, self).__init__(action, **kwargs)
        self.add_lists(event_url=event_url)
        self.add_options(event_method=event_method, format=format, end_on_silence=end_on_silence,
                         end_on_key=end_on_key, time_out=time_out, beep_start=beep_start)


class Conversation(RequestAction):
    def __init__(self, name, event_url=None, event_method='POST', music_on_hold_url=None, start_on_enter=None,
                 end_on_exit=None, record=None, **kwargs):
        """
        You use the conversation NCCO to create standard or moderated Conversations. The first person to call the
            virtual number assigned to the Conversation creates it. This action is synchronous, the Conversation lasts
            until the number of participants is 0.

        :type name: str
        :param name: The name of the Conversation room. Names have to be unique per account.
        :type event_url: list<str>
        :param event_url: The list of URLs to the webhook endpoint that is called asynchronously when a
                            recording is finished.
        :param event_method: [POST|GET]
        :type music_on_hold_url: list<str>
        :param music_on_hold_url: A URL to the mp3 file to stream to participants until the conversation starts.
                                    By default the conversation starts when the first person calls the virtual number
                                    associated with your Voice app. To stream this mp3 before the moderator joins the
                                    conversation, set start_on_enter to false for all users other than the moderator.
        :type  start_on_enter: bool
        :param start_on_enter: The default value of true ensures that the conversation starts when this caller joins
                                    conversation name. Set to false for attendees in a moderated conversation.
        :type end_on_exit: bool
        :param end_on_exit: For moderated conversations, set to true in the moderator NCCO so the conversation is ended
                                    when the moderator hangs up. The default value of false means the conversation is
                                    not terminated when a caller hangs up; the conversation ends when the last caller
                                    hangs up.
        :type record: bool
        :param record: Set to true to record this conversation. For standard conversations, recordings start when one
                                    or more attendees connects to the conversation. For moderated conversations,
                                    recordings start when the moderator joins. That is, when an NCCO is executed for
                                    the named conversation where startOnEnter is set to true. When the recording is
                                    terminated, the URL you download the recording from is sent to the event URL.
        :param kwargs: Any additional options (make sure the keys are in snake_case format).
        """

        action = 'conversation'
        super(Conversation, self).__init__(action, **kwargs)
        self.add_lists(event_url=event_url, music_on_hold_url=music_on_hold_url)
        self.add_options(name=name, event_method=event_method, start_on_enter=start_on_enter, end_on_exit=end_on_exit,
                         record=record)


class Connect(RequestAction):
    def __init__(self, endpoint, event_url, event_method='POST', _from=None, event_type=None, timeout=60, limit=7200,
                 machine_detection=None, **kwargs):
        """
        Connect to endpoints such as phone numbers. This action is synchronous, after a connect the next action in the
            NCCO stack is processed. A connect action ends when the endpoint you are calling is busy or unavailable.
            You ring endpoints sequentially by nesting connect actions.

        :type endpoint: list<dict>
        :param endpoint: Connect to a single endpoint.

        :type event_url: list<str>
        :param event_url: Set the webhook endpoint that Nexmo calls asynchronously on each of the possible Call states.
                            If eventType is set to synchronous the eventUrl can return an NCCO that overrides the
                            current NCCO when a timeout occurs..
        :param event_method: [POST|GET]
        :type  _from: str
        :param _from: A number in e.164 format that identifies the caller ("_form" will be converted to "from").
        :type  event_type: string|None
        :param event_type: Set to "synchronous" to: make the connect action synchronous or enable eventUrl to return an
                            NCCO that overrides the current NCCO when a call moves to specific states.
        :param timeout: If the call is unanswered, set the number in seconds before Nexmo stops ringing endpoint
        :param limit: Maximum length of the call in seconds. The default and maximum value is 7200s.
        :type machine_detection: str
        :param machine_detection: Set to either "continue" or "hangup". Configure the behavior when Nexmo detects that
                                        a destination is an answerphone. Set to either:
                                        continue - Nexmo sends an HTTP request to event_url with the Call event machine
                                        hangup - end the Call
        :param kwargs: Any additional options (make sure the keys are in snake_case format).
        """

        action = 'connect'
        super(Connect, self).__init__(action, **kwargs)
        self.add_lists(endpoint=endpoint, sub_type=dict)
        self.add_lists(event_url=event_url)
        self.add_options(event_method=event_method, _from=_from, event_type=event_type, timeout=timeout, limit=limit,
                         machine_detection=machine_detection)


class Talk(RequestAction):
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
        :param text: A string of up to 1500 characters containing the message to be synthesized in the Call or
                        Conversation. Each comma in text adds a short pause to the synthesized speech.
        :type barge_in: bool
        :param barge_in: Set this to true to interrupt the voice before the talk command is finished.
                            This action must be followed by an input action.
        :type loop: int
        :param loop: The number of times text is repeated before the Call is closed. The default value is 1.
                            Set to 0 to loop infinitely.
        :param voice_name: The name of the voice used to deliver text. See Talk.VOICE_CHOICES for the list of choices.
        :param kwargs: Any additional options (make sure the keys are in snake_case format).
        """
        action = 'talk'
        super(Talk, self).__init__(action, **kwargs)
        self.add_options(text=text, barge_in=barge_in, loop=loop, voice_name=voice_name)


class Stream(RequestAction):
    def __init__(self, stream_url, level=0, barge_in=False, loop=1, **kwargs):
        """
        Send an audio stream to a Conversation. By default, the talk action is synchronous. However, if you set
                bargeIn to true you must set an input action later in the NCCO stack.

        :type stream_url: list<str>
        :param stream_url: An array containing a single URL to an mp3 or wav (16-bit) audio file to stream to the
                                Call or Conversation.
        :param level: Set the audio level of the stream in the range -1 >=level<=1 with a precision of 0.1.
        :param barge_in: Set to true so this action is terminated when the user presses a button on the keypad.
                                Use this feature to enable users to choose an option without having to listen to the
                                whole message in your Interactive Voice Response (IVR ). If you set bargeIn to true
                                the next action in the NCCO stack must be an input action.
        :param loop: The number of times stream is repeated before the Call is closed. The default value is 1.
                                Set to 0 to loop infinitely.
        :param kwargs: Any additional options (make sure the keys are in snake_case format).
        """
        action = 'stream'
        super(Stream, self).__init__(action, **kwargs)
        self.add_lists(stream_url)
        self.add_options(level=level, barge_in=barge_in, loop=loop)


class Input(RequestAction):
    def __init__(self, event_url=None, time_out=3, max_digits=None, submit_on_hash=False, event_method='POST', **kwargs):
        """
        :type event_url: list<str>
        :param event_url: Nexmo sends the digits pressed by the callee to this URL after timeOut pause in
                            activity or when # is pressed.
        :param time_out: The result of the callee's activity is sent to the event_url webhook endpoint time_out
                            seconds after the last action.
        :type max_digits: int
        :param max_digits: The number of digits the user can press. The maximum value is 20.
        :param submit_on_hash: Set to true so the callee's activity is sent to your webhook endpoint at eventUrl after
                            he or she presses #. If # is not pressed the result is submitted after timeOut seconds.
        :param event_method:  The HTTP method used to send event information to event_url.
        """
        action = 'input'
        super(Input, self).__init__(action, **kwargs)
        self.add_lists(event_url=event_url)
        self.add_options(max_digits=max_digits, time_out=time_out, submit_on_hash=submit_on_hash,
                         event_method=event_method)


class RequestJsonEncoder(json.JSONEncoder):
        def __init__(self, *args, **kwargs):
            super(RequestJsonEncoder, self).__init__(*args, **kwargs)

        def normalize_dict(self, obj):
            """
            Convert bool to lower case string True become "true"
            """
            if isinstance(obj, bool):
                return str(obj).lower()
            if isinstance(obj, (list, tuple)):
                return [self.normalize_dict(item) for item in obj]
            if isinstance(obj, dict):
                return {key: self.normalize_dict(value) for key, value in obj.items()}
            return obj

        def default(self, o):
            if isinstance(o, RequestAction):
                return self.normalize_dict(dict(o))
            return str(self.normalize_dict(o))


class Request:
    JSON_MIME = 'application/json'

    actions = None
    json_options = None

    def __init__(self, pretty=False, sort_keys=False, **json_options):
        """
        :param pretty: Set this to True to beautify the json render.
        :param sort_keys: Sort the json by the key value
        :param json_options: Options for json.dumps(**json_options)
        """
        self.json_options = json_options or {}
        self.actions = []
        if pretty:
            self.json_options['indent'] = 4
        if sort_keys:
            self.json_options['sort_keys'] = sort_keys

    def add_action(self, action):
        """
        Add an action to this request.

        :type action: RequestAction
        :param action: The action instance
        """
        self.actions.append(action)

    def get_json_string(self):
        """
        Compose this request as a json string

        :rtype: str
        """
        request = self.actions
        return json.dumps(request, cls=RequestJsonEncoder, **self.json_options)

    def render(self):
        """
        Return the json string as django HttpResponse.

        :rtype: HttpResponse
        """
        if HttpResponse is None:
            raise ImportError('This method requires HttpResponse class, make sure django is installed.')

        json_response = self.get_json_string()
        return HttpResponse(json_response, content_type=self.JSON_MIME)
