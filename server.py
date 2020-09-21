import socketio
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
import json, asyncio
import os
import multiprocessing as mp
import proxy

import logging
from recordingsession import RecordingSession
from tempfile import TemporaryDirectory
from segments import RawTrack

logging.basicConfig(level=logging.DEBUG)

BLOBLEN = 110  # ms
SYNCDELAY = 2000  # ms

sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
app = web.Application()
sio.attach(app)

tmpdir = TemporaryDirectory()
tmp_directory = tmpdir.name
music_xml_path = None
os.mkfifo(f"{tmp_directory}/tmppipe", 0o666)
audio_pipe_path = f"{tmp_directory}/tmppipe"
session = RecordingSession(BLOBLEN, SYNCDELAY)


@sio.event
async def update_xml(sid, data):
    global tmp_directory, music_xml_path, session
    file, name = data
    music_xml_path = f"{tmp_directory}/{name}"
    session.mxml = music_xml_path
    with open(music_xml_path, "w") as f:
        f.write(file)


@sio.event
async def get_xml(sid, data):
    global music_xml_path
    with open(music_xml_path, "r") as f:
        xml = f.read()
    await sio.emit("xml_return", xml)


@sio.event
async def start(sid, data):
    global session
    print(data)
    session.dump_data(*data)
    print("Got start signal")
    session.start_recording()
    await sio.emit("start-participants", data)


@sio.on("audio-tx")
async def recv_audio(sid, data):
    global session
    audio, blob_no, name = data
    session.tell_segment(*data)
    # if blob_no > 0: print(session)
    # print(f"Received audio chunk from {sid}.")
    # print(f"Length {len(audio)}, blob_no: {blob_no}, name: {name}")


@sio.event
async def stop(sid):
    global session
    print("asdf0")
    await asyncio.sleep(5)
    print("asdf1")
    await sio.emit("stop-participants")
    print("asdf2")
    session.finish_recording()
    print("asdf3")
    await sio.emit("analytics", session.run_analysis())
    print("asdf3.5")
    complete_wav_path = session.mash_audio()
    print("asdf4")
    await sio.emit("final_audio", complete_wav_path)
    # with open(complete_wav_path, "r") as f:
    #     byte_arr = f.read()
    # print("asdf5")
    # await sio.emit("final_audio", byte_arr)


"""
async def offer(request):
    global audio_pipe_path, session
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    # shutdown = mp.Event()
    # proc = mp.Process(target=proxy.server, args=(shutdown, audio_pipe_path))
    # proc.daemon = True
    # proc.start()
    # print("1")
    # session.setup_zmq()
    # print("2")
    # player = MediaPlayer(audio_pipe_path, format="wav")
    # print("3")
    #player = MediaPlayer("demo-instruct.wav")
    pp = RawTrack(session)
    # if write_audio:
    #     recorder = MediaRecorder(args.write_audio)
    @pc.on("track")
    def on_track(track):
        print(f"Streaming a {track.kind} track...")
        if track.kind == "audio":
            pc.addTrack(pp)
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

    # Tell music session to start writing to pipe
    # session.send_stream = True
    
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )
"""


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
    # app.router.add_post("/offer", offer)
    app.router.add_get("/", index)
    app.router.add_get("/script.js", javascript)
    web.run_app(app, access_log=None, host="0.0.0.0", port=8081)
