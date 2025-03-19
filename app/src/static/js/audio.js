function initializeVoiceRecognition(
    messageInput, sendButton, microphoneButton, recordingButton, recordingContainer, recordingText, recordingTime) {
    // 음성 인식 지원 확인
    const recognition = getSpeechRecognition();
    if(!recognition) {
        console.log('이 브라우저는 음성 인식을 지원하지 않습니다.');
        return null;
    }

    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.continuous = true;
    let totalResult = ""
    let localResult = ""

    recognition.onresult = function (event) {
        console.log("onresult event");
        localResult = ""
        for(let i = 0; i < event.results.length; i++){
            localResult += event.results[i][0].transcript;
        }
        recordingText.textContent = totalResult + " " + localResult;
    };

    recognition.onerror = function (event) {
        console.error('음성 인식 오류:', event.error);
    };

    recognition.onstart = function () {
        console.log('> 음성 인식 시작', new Date().toISOString());
    };

    recognition.onend = function () {
        console.log('> 음성 인식 종료', new Date().toISOString());
        console.log("onend", totalResult, localResult);
        totalResult += " " + localResult;
        localResult = "";
    };

    recognition.onspeechstart = function () {
        console.log('>> 스피치 시작', new Date().toISOString());
    };

    recognition.onspeechend = function () {
        console.log('>> 스피치 종료', new Date().toISOString());
        if(recording && restartSchedule){
            console.log('>> 스피치 종료 후 음성 인식 시작', new Date().toISOString());
            recognition.stop();
            recognitionStart();
        }
    };

    let recording = false;
    let recordingStartTime = null;
    let recordingTimer = null;
    let restartSchedule = false;

    // 모든 버튼 표시 여부 업데이트
    function updateInputDisplay() {
        if (recording) {
            sendButton.style.display = 'none';
            microphoneButton.style.display = 'none';
            recordingButton.style.display = 'flex';
            recordingContainer.style.display = 'flex';
            messageInput.style.display = 'none';
            return;
        }

        if (messageInput.value.trim()) {
            sendButton.style.display = 'flex';
            microphoneButton.style.display = 'none';
            recordingButton.style.display = 'none';
            recordingContainer.style.display = 'none';
            messageInput.style.display = 'flex';
            recordingTime.textContent = '00:00';
            return;
        }

        sendButton.style.display = 'none';
        microphoneButton.style.display = 'flex';
        recordingButton.style.display = 'none';
        recordingContainer.style.display = 'none';
        messageInput.style.display = 'flex';
        recordingTime.textContent = '00:00';
    }

    // 녹음 시간 업데이트 함수
    function updateRecordingTime() {
        const currentTime = new Date();
        const elapsedSeconds = Math.floor((currentTime - recordingStartTime) / 1000);
        const minutes = Math.floor(elapsedSeconds / 60);
        const seconds = elapsedSeconds % 60;

        recordingTime.textContent =
            (minutes < 10 ? '0' : '') + minutes + ':' +
            (seconds < 10 ? '0' : '') + seconds;
    }

    function updateRecordingTexts(){
        console.log("updateRecordingTexts", totalResult, localResult);
        messageInput.value = totalResult + localResult;
        recordingText.textContent = "";
        totalResult = "";
        localResult = "";
    }

    function recognitionStart(){
        restartSchedule = false;
        recordingContainer.classList.add('recording-pause');
        recognition.stop()
        recognition.start();
        
        // 1초 후에 클래스 제거
        setTimeout(() => {
            recordingContainer.classList.remove('recording-pause');
        }, 300);

        setTimeout(() => {
            restartSchedule = true;
        }, 5000);
    }

    function startRecrod() {
        recording = true;

        // 녹음 시간 타이머 시작
        recordingStartTime = new Date();
        recordingTimer = setInterval(updateRecordingTime, 1000);

        // 음성 인식 시작
        recognitionStart();

        updateInputDisplay();
    }

    function stopRecrod() {
        console.log("stopRecrod");
        recording = false;
        restartSchedule = false;

        recognition.stop();
        if(recordingTimer) {
            clearInterval(recordingTimer);
            recordingTimer = null;
        }

        updateRecordingTexts();

        updateInputDisplay();
    }

    recordingButton.addEventListener('click', () => { 
        recording = false; 
        updateInputDisplay() 
    });

    // 텍스트 변경 감지
    messageInput.addEventListener('input', function () {
        setTimeout(() => {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            updateInputDisplay();
        }, 0);
    });

    // 붙여넣기 감지
    messageInput.addEventListener('paste', function () {
        setTimeout(() => {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            updateInputDisplay();
        }, 0);
    });

    // 자르기 감지
    messageInput.addEventListener('cut', function () {
        setTimeout(() => {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            updateInputDisplay();
        }, 0);
    });

    messageInput.addEventListener('keyup', function () {
        setTimeout(() => {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            updateInputDisplay();
        }, 0);
    });

    microphoneButton.addEventListener('click', () => { 
        recording = true; 
        startRecrod();
        updateInputDisplay(); 
    });

    recordingButton.addEventListener('click', () => { 
        recording = false; 
        stopRecrod();
        updateInputDisplay(); 
    });

    sendButton.addEventListener('click', () => {
        updateInputDisplay();
    });


    return {
        recognition: recognition,
        startRecording: startRecrod,
        stopRecording: stopRecrod,
        updateInputDisplay: updateInputDisplay
    };
}

function getSpeechRecognition() {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        return new SpeechRecognition();
    }
    return null;
}

