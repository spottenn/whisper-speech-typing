from abc import ABC, abstractmethod


class Transcriber(ABC):
    """
    Base class for all transcribers. This class defines the interface that all
    transcriber implementations should follow.
    """

    @abstractmethod
    def transcribe_audio(self, audio):
        """
        Transcribe the given audio. This method should be implemented by all subclasses.

        :param audio: The audio to transcribe.
        :return: The transcribed text.
        """
        pass

    @abstractmethod
    def post_process(self, input_string):
        """
        Post-process the transcribed text. This method should be implemented by all subclasses.

        :param input_string: The transcribed text to post-process.
        :return: The post-processed text.
        """
        pass

    # TODO: start and stop methods to release resources
