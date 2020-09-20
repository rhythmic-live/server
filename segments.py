from aiortc import MediaStreamTrack
from av import AudioFrame
import asyncio
import threading

import numpy as np

def process_session(loop, session, track, quit_event):
    while not quit_event.is_set():
        while len(session.tracks['Joe']) - track.last_idx < 200:
            continue

        curr_len = track.last_idx + 200
        curr_nd = np.array([session.tracks['Joe'][track.last_idx:curr_len]]).view(np.int16)
        #print(f"New frame: {curr_nd}")

        frame = AudioFrame.from_ndarray(curr_nd, format='s16', layout='mono') 
        frame.sample_rate = 22050
        frame.pts = track.last_idx

        track.last_idx = curr_len

        asyncio.run_coroutine_threadsafe(track.q.put(frame), loop)

class RawTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "audio"

    def __init__(self, session):
        super().__init__()  # don't forget this!
        self.session = session
        self.last_idx = 0
        self.thread = None
        self.q = asyncio.Queue()

    def start(self):
        if self.thread is None:
            self.__thread_quit = threading.Event()
            self.thread = threading.Thread(
                name="raw-player",
                target=process_session,
                args=(
                    asyncio.get_event_loop(),
                    self.session,
                    self,
                    self.__thread_quit
                ),
            )
            self.thread.start()

    async def recv(self):
        self.start()
        a = await self.q.get()
        print(f"new frame: {a}")
        return a