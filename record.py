"""Not my code. https://stackoverflow.com/questions/39474111/recording-audio-for-specific-amount-of-time-with-pyaudio.
"""

import pyaudio
import wave

RECORD_SECONDS = 20
WAVE_OUTPUT_FILE_NAME = "output.wav"


def record(file_name, record_seconds, chunk=1024, format=pyaudio.PaInt16, channels=1, rate=44100):
    p = pyaudio.PyAudio()

    input('Ready to start recording. Press Enter.')

    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

    print("* recording")
    frames = []
    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("* done")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_name, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("* done recording")


if __name__ == '__main__':
    record(WAVE_OUTPUT_FILE_NAME, RECORD_SECONDS)
