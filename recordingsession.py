import numpy as np
from analysis import analytics
from queue import Queue
from pydub import AudioSegment
import tempfile
import os


class RecordingSession:
    WAV_SAMPLE_RATE = 22050
    
    def __init__(self, blob_len, sync_delay):
        self.blob_offset = sync_delay//blob_len + 1
        self.tracks = {} # A dict of buffers
        self.recording = False 

    def tell_segment(self, audio_buffer, blob_no, track_id):
        if self.recording:
            if track_id not in self.tracks:
                self.tracks[track_id] = bytearray()
            self.tracks[track_id].extend(audio_buffer)
                
    def run_analysis(self):
        wave_paths = self.wav_paths
        func = lambda x : x.split(".")[0]
        start_m = self.start_m
        end_m = self.end_m
        tempo = self.tempo
        mxml = self.mxml 
        print("Running konwoo's genius calculations")
        return [analytics.analyze(mxml, func(path), start_m, end_m, tempo, path) for path in wave_paths]
    
    def dump_data(self, start_m, end_m, tempo):
        self.start_m = int(start_m)
        self.end_m = int(end_m)
        self.tempo = int(tempo)
    
    @staticmethod
    def combineaudio(audios):
        if len(audios) == 1:
            return list(audios)[0]
        return np.mean(*audios)
    
    def start_recording(self):
        self.recording = True
        
    def finish_recording(self):
        self.recording = False
        self.wav_paths = []
        for part in self.tracks.keys():
            with open(f'tmp.wav', 'wb') as f:
                f.write(self.tracks[part])
            a = AudioSegment.from_file('tmp.wav', format='s16le')
            a.export(f'{part}.wav')
            self.wav_paths.append(f'{part}.wav')
            
    def mash_audio(self):
        mapped = list(map(lambda x : AudioSegment.from_file(x), self.wav_paths))
        front = mapped[0]
        for other in mapped[1:]:
            front.overlay(other)
        front.export("complete.wav")
        return "complete.wav"