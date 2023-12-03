# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project

import os
import time
import wave
import pyaudio
import logging
import tempfile
import threading


# for handling audio record and play
class AudioUtils:
    CHANNEL = 1
    CHUNK = 1024
    RATE = 44100
    FORMAT = pyaudio.paInt16

    def __init__(self):
        self.thread = threading.Thread(target=self.__record)
        self.halt_recording = threading.Event()
        self.logger = logging.getLogger(__name__)
        self.audio = pyaudio.PyAudio()
        self.tempfile = None  # temporary file to save the recorded wav audio
        self.frames = []  # audio frame
        self.stream = None

    # audio recording thread worker
    def __record(self):
        while not self.halt_recording.is_set():
            data = self.stream.read(1024)
            self.frames.append(data)
        return

    # start the audio record
    def start_record(self):
        # create audio stream
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNEL,
                                      rate=self.RATE, input=True,
                                      frames_per_buffer=self.CHUNK)

        # start the record thread
        self.logger.info("Now starting the AudioUtils record thread.")
        self.thread.start()
        return

    # stop the audio record
    def stop_record(self):
        self.halt_recording.set()

        # wait for the subthread to terminate completely
        self.logger.info("Waiting for the audio thread worker to join")
        self.thread.join()
        self.logger.info("Audio thread worker joined main thread !!")

        # save to file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temporary:
            with wave.open(temporary, 'wb') as file:
                file.setnchannels(self.CHANNEL)
                file.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                file.setframerate(self.RATE)
                file.writeframes(b''.join(self.frames))

            # log filename
            self.tempfile = temporary.name
            self.logger.info("Successfully saved the recorded audio as: {}".format(self.tempfile))

        return

    # play the voice record by file
    def play(self, filename):
        # open wave file
        self.logger.info(f"Trying to play wav file: {filename}")
        wf = wave.open(filename, 'rb')

        # Open a stream to play audio
        stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)

        # Read data in chunks and play
        data = wf.readframes(self.CHUNK)
        while data:
            stream.write(data)
            data = wf.readframes(self.CHUNK)

        # Close the stream and PyAudio instance
        stream.stop_stream()
        stream.close()
        self.audio.terminate()
        return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # try record audio
    instance = AudioUtils()
    instance.start_record()
    time.sleep(3)
    instance.stop_record()

    # try play audio
    instance.play(instance.tempfile)

    # now clean up manually
    while not instance.tempfile:
        os.remove(instance.tempfile)
