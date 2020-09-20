import socketio
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
import json
import os

import logging
from recordingsession import RecordingSession
from tempfile import TemporaryDirectory

logging.basicConfig(level=logging.DEBUG)

BLOBLEN = 110  # ms
SYNCDELAY = 2000  # ms

sio = socketio.AsyncServer(async_mode="aiohttp")
app = web.Application()
sio.attach(app)

tmpdir = TemporaryDirectory()
tmp_directory = tmpdir.name
music_xml_path = None
os.mkfifo(f"{tmp_directory}/tmppipe")
audio_pipe_path = f"{tmp_directory}/tmppipe"
session = RecordingSession(BLOBLEN, SYNCDELAY, audio_pipe_path)


@sio.event
async def update_xml(sid, data):
    global tmp_directory, music_xml_path, session
    file, name = data
    session.songname = name
    music_xml_path = f"{tmp_directory}/{name}"
    with open(music_xml_path, "w") as f:
        f.write(file)

@sio.event
async def get_xml(sid, data):
    global music_xml_path
    with open(music_xml_path, "r") as f:
        return f.read()

@sio.event
async def start(sid):
    global session
    print("Got start signal")
    session.start_recording()
    await sio.emit("start-participants")

@sio.on("audio-tx")
async def recv_audio(sid, data):
    global session
    print(type(data))
    print(len(data))
    print(type(data[0]))
    audio, blob_no, name = data
    session.tell_segment(*data)
    if blob_no > 0: print(session)
    print(f"Received audio chunk from {sid}.")
    print(f"Length {len(audio)}, blob_no: {blob_no}, name: {name}")
    print(f"Preview: {audio[-100:]}")

async def offer(request):
    global audio_pipe_path, session
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    player = MediaPlayer(audio_pipe_path)
    # if write_audio:
    #     recorder = MediaRecorder(args.write_audio)
    @pc.on("track")
    def on_track(track):
        print(f"Streaming a {track.kind} track...")
        if track.kind == "audio":
            pc.addTrack(player.audio)
            # recorder.addTrack(track)
        elif track.kind == "video":
            raise RuntimeError("No Video :(")

        @track.on("ended")
        async def on_ended():
            print(f"Track {track.kind} ended")
            # await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    # await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Tell music session to start writing to pipe???
    session.send_stream = True
    
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    print("SHUTDOWN")

# html pages

ROOT = os.path.dirname(__file__)

async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)

async def javascript(request):
    content = open(os.path.join(ROOT, "./static/script.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

if __name__ == "__main__":
    app.on_shutdown.append(on_shutdown)
    app.router.add_post("/offer", offer)
    app.router.add_get("/", index)
    app.router.add_get("/script.js", javascript)
    web.run_app(app, access_log=None)