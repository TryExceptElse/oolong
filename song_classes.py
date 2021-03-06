from json_tricks.np import load

# Loading songs from a path
import os
from librosa import load, beat, output

from src.features import getFeatures

class Song:
    def __init__(self, name, path):
        '''
        This is the main Song class. It holds basic data about the song name, genre, and path.
        Each of the other attributes are set via the analyze_song() function and represent
        the sub-classes below.

        :param name: (string)         | song name
        :param path: (string)         | full path to the song
        :attr load: (Load)            | y and sr from Librosa's load()
        :attr genre: (string)         | genre for the song (manually set for training)
        :attr beat_track: (beatTrack) | beat track from Librosa's beat.beat_track()
        :attr segments: (dict)        | dictionary of the segments of a song and their bounds as tuples
        :attr slice: (Slice)          | variant of Load that takes a slice of a song at an offset and duration
        :attr: features: (Features)   | class to store feature scatterplot
        '''
        self.name = name
        self.path = path
        self.load = Load(path)
        self.genre = None
        self.segments = None
        self.beat_track = None
        self.slice = None
        self.features = None

    def __json_encode__(self):
        return {'name': self.name, 'path': self.path, 'genre': self.genre,
                'segments': dict([(str(k), v) for k, v in self.segments.items()]),
                'beat_track': self.beat_track, 'features': self.features}

    def __json_decode__(self, **attrs):
        self.features = attrs['features']

class Load:
    def __init__(self, path, **kwargs):
        '''
        Load takes in a path and calls Librosa's load.load_song() on it.

        :param path: (string)    | path to load
        :param kwargs: (arr)     | to pass arguments to the Slice sub class
        :attr y: (numpy.ndarray) | audio time series
        :attr sr: (int)          | sample rate
        '''
        y, sr = load_song(path, **kwargs)
        self.y = y
        self.sr = sr

    def __iter__(self):
        return iter([self.y, self.sr])

    def output_wav(self, folder, filename):
        '''
        Small function to output a Load or Slice to a wav file

        :param folder: (string)   | the folder to output to
        :param filename: (string) | filename to output as
        :return:
        '''
        audio = os.path.join(folder, filename)
        output.write_wav(audio, self.y, self.sr)

class Slice(Load):
    def __init__(self, path, offset=None, duration=None):
        '''
        This is a sub-class of Load. It 'records' a slice

        :param path: (string)       | path to load
        :param offset: (float)      | offset to start load (in seconds)
        :param duration: (float)    | duration to 'record' (in seconds)
        '''
        super().__init__(path, offset=offset, duration=duration)
        self.offset = offset
        self.duration = duration

class beatTrack():
    def __init__(self, y, sr):
        '''
        Generates a Librosa beat.beat_track() for the song.

        :param tempo: (float) | beats per minute
        :param beats: (list)  | list of beat frames
        '''
        tempo, beats = beat.beat_track(y=y, sr=sr, trim=False, start_bpm=160)
        self.tempo = tempo
        self.beats = beats

    def __iter__(self):
        return iter([self.tempo, self.beats])

class Features:
    def __init__(self, slice):
        '''
        Features takes a slice and uses CENSURE image detection to create a scatterplot of the notable features.
        Read more here: https://link.springer.com/chapter/10.1007/978-3-540-88693-8_8

        :param slice: (Slice)     | slice to find features for
        :attr detector: (CENSURE) | CENSURE image detector
        :attr kp: (numpy.ndarray) | feature scatterplot
        '''
        detector, kp = getFeatures(slice)
        self.detector = detector
        self.kp = kp

def load_song(path, **kwargs):
    '''
    Small helper function to load song from path
    :param path: (string)    | path to load
    :param kwargs: (arr)     | to pass arguments to the Slice sub class
    :return:
    '''
    y, sr = load(path=path, **kwargs)
    return (y, sr)