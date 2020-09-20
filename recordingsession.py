import numpy as np

# from pydub import AudioSegment

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
        self.tracks = [] # A list of dictionaries
        self.mixed = [] # Fully reconstructed audio
        self.recording = False 
        self.send_stream = False

    def tell_segment(self, audio_buffer, blob_no, track_id):
        if self.recording:
            while len(self.tracks) <= blob_no:
                self.tracks.append(dict())
            self.tracks[blob_no][track_id] = np.frombuffer(audio_buffer, dtype=np.uint8)
            num_mixed = len(self.mixed)
            if blob_no > num_mixed + self.blob_offset: 
                mixed = self.combineaudio(self.tracks[num_mixed].values())
                self.mixed.append(mixed)
                if self.send_stream:
                    with open(self.audio_pipe_dir, "w") as pipe:
                        pipe.write(mixed.tobytes())
                # send shit into a pipe?
    
    def __repr__(self):
        ret = f"Blob_offset: {self.blob_offset}\n"
        ret += f"Tracks: {self.tracks[0].keys()} as keys with {len(self.tracks)} entries\n"
        ret += f"Mixed: {len(self.mixed)}\n"
        return ret
    
    @staticmethod
    def combineaudio(audios):
        return np.mean(*audios)
    
    def start_recording(self):
        self.recording = True
        
    def finish_recording(self):
        self.recording = False
        self.send_stream = False