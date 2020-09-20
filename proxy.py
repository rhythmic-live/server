import zmq


def server(shutdown, stupidpipe):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("ipc:///tmp/proxypipe")
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    with open(stupidpipe, "w") as pipe:
        print("I Opened the damn pipe bro")
        while not shutdown.is_set():
            if poller.poll(0):
                print("Bruh moment")
                pipe.write(socket.recv(copy=False))
                socket.send(b"thx")