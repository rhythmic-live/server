import numpy as np
import zmq

from queue import Queue

from pydub import AudioSegment
import tempfile
import os

# sound1 = AudioSegment.from_file("/Users/elizabethxu/Desktop/REVERSE_CantinaBand3.wav")
# sound2 = AudioSegment.from_file("/Users/elizabethxu/Desktop/CantinaBand3.wav")

# combined = sound1.overlay(sound2)

# # https://stackoverflow.com/questions/35735497/how-to-create-a-pydub-audiosegment-using-an-numpy-array

# combined.export("mixedbetter.wav", format='wav')

class RecordingSession:
    WAV_SAMPLE_RATE = 22050
    
    def __init__(self, blob_len, sync_delay, audio_pipe_dir, songname=None):
        self.songname = songname
        self.blob_len = blob_len
        self.sync_delay = sync_delay # delay send to allow for synchronizaiton
        self.audio_pipe_dir = audio_pipe_dir
        self.blob_offset = sync_delay//blob_len + 1
        self.tracks = {} # A list of dictionaries
        self.mixed = [] # Fully reconstructed audio
        self.recording = False 
        self.send_stream = False
        self.q = Queue()
        self.last_sent = 0
        self.curr_audio = None

    def tell_segment(self, audio_buffer, blob_no, track_id):
        if self.recording:
            if track_id not in self.tracks:
                self.tracks[track_id] = bytearray()

            self.tracks[track_id].extend(audio_buffer)

            if blob_no == 100:
                with open('tmp.wav', 'wb') as f:
                    f.write(self.tracks[track_id])
                
                a = AudioSegment.from_file('tmp.wav', format='s16le')
                a.export('good.wav')
    
    def setup_zmq(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("ipc:///tmp/proxypipe")
    
    def __repr__(self):
        # ret = f"Blob_offset: {self.blob_offset}\n"
        # ret += f"Tracks: {self.tracks[0].keys()} as keys with {len(self.tracks)} entries\n"
        # ret += f"Mixed: {len(self.mixed)}\n"
        # return ret
        return "fuck"
    
    @staticmethod
    def combineaudio(audios):
        if len(audios) == 1:
            return list(audios)[0]
        return np.mean(*audios)
    
    def start_recording(self):
        self.recording = True
        
    def finish_recording(self):
        self.recording = False
        self.send_stream = False