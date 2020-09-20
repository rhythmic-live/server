SOCKET_ADDR = 'http://localhost:8080';

socket = io.connect(SOCKET_ADDR);

function myFunction(){
    console.log("emit start")
    socket.emit("start")
}

mediaConstraint = {
	video: false,
	audio: {
		sampleRate: 44100,
		channelCount: 1
	}
};

navigator.getUserMedia = ( navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia);


socket.on("start-participants", function() {
    let blob_no = 0
	navigator.getUserMedia(mediaConstraint, function(stream) {
		audioRecorder = new MediaStreamRecorder(stream);
		audioRecorder.mimeType = 'audio/pcm';
		//audioRecorder.sampleRate = 22050;
		audioRecorder.audioChannels = 1;
		audioRecorder.ondataavailable = function(e) {
            socket.emit("audio-tx", [e, blob_no, "Joe"]);
            blob_no++;
		}
		audioRecorder.start(100);
	}, function(error){
        console.log("Error in stream")
	});
});


var pc = null;


function createPeerConnection() {
    pc = new RTCPeerConnection();

    // connect audio / video
    pc.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video')
            document.getElementById('video').srcObject = evt.streams[0];
        else
            document.getElementById('audio').srcObject = evt.streams[0];
    });

    return pc;
}


function negotiate() {
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
        document.getElementById('answer-sdp').textContent = answer.sdp;
        return pc.setRemoteDescription(answer);
    }).catch(function(e) {
        alert(e);
    });
}



function getConductor(){
    pc = createPeerConnection();

    var constraints = {audio: true, video: false};

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        stream.getTracks().forEach(function(track) {
            pc.addTrack(track, stream);
        });
        return negotiate();
    }, function(err) {
        alert('Could not acquire media: ' + err);
    });

}