SOCKET_ADDR = 'http://localhost:8081';

socket = io.connect(SOCKET_ADDR);

function myFunction(){
    console.log("emit start")
    socket.emit("start", [0, 0, 0])
}
function stopbutton(){
    console.log("emit stop")
    socket.emit("stop")
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


// var pc = null;


// function createPeerConnection() {
//     var config = {
//         sdpSemantics: 'unified-plan'
//         //iceServers: [{urls: ['stun:stun.l.google.com:19302']}]
//     }

//     pc = new RTCPeerConnection(config);

//     // connect audio / video
//     pc.addEventListener('track', function(evt) {
//         if (evt.track.kind == 'video')
//             document.getElementById('video').srcObject = evt.streams[0];
//         else
//             document.getElementById('audio').srcObject = evt.streams[0];
//     });

//     return pc;
// }


// function negotiate() {
//     return pc.createOffer().then(function(offer) {
//         console.log("offer created...");
//         return pc.setLocalDescription(offer);
//     }).then(function() {
//         // wait for ICE gathering to complete
//         return new Promise(function(resolve) {
//             if (pc.iceGatheringState === 'complete') {
//                 resolve();
//             } else {
//                 function checkState() {
//                     console.log('event listener called...');
//                     if (pc.iceGatheringState === 'complete') {
//                         pc.removeEventListener('icegatheringstatechange', checkState);
//                         resolve();
//                     }
//                 }
//                 pc.addEventListener('icegatheringstatechange', checkState);
//                 console.log('event listener installed...');
//             }
//         });
//     }).then(function() {
//         var offer = pc.localDescription;
//         console.log(offer);
//         return fetch('/offer', {
//             body: JSON.stringify({
//                 sdp: offer.sdp,
//                 type: offer.type
//             }),
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             method: 'POST'
//         });
//     }).then(function(response) {
//         return response.json();
//     }).then(function(answer) {
//         //document.getElementById('answer-sdp').textContent = answer.sdp;
//         return pc.setRemoteDescription(answer);
//     }).catch(function(e) {
//         alert(e);
//     });
// }



// function getConductor(){
//     console.log("creating peer connection");
//     pc = createPeerConnection();

//     var constraints = {audio: true, video: false};

//     console.log("negotiating...");
//     // negotiate();

//     navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
//         stream.getTracks().forEach(function(track) {
//             pc.addTrack(track, stream);
//         });
//         return negotiate();
//     }, function(err) {
//         alert('Could not acquire media: ' + err);
//     });

// }