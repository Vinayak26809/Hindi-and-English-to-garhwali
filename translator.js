let recognition;
const synth = window.speechSynthesis;

function autoExpand(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = textarea.scrollHeight + 'px';
}

function startVoiceInput() {
  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    alert('Speech recognition not supported in this browser.');
    return;
  }

  recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'hi-IN';
  recognition.interimResults = false;

  recognition.onresult = function(event) {
    document.getElementById("inputText").value = event.results[0][0].transcript;
    autoExpand(document.getElementById("inputText"));
  };

  recognition.start();
}

function stopVoiceInput() {
  if (recognition) recognition.stop();
}

function translateText() {
  const text = document.getElementById("inputText").value.trim();
  const source = document.getElementById("source").value;

  if(!text) {
    alert('Please enter some text to translate.');
    return;
  }

  fetch('/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, source })
  })
  .then(res => {
    if (!res.ok) {
      throw new Error(`Server returned status ${res.status}`);
    }
    return res.json();
  })
  .then(data => {
    document.getElementById("result").innerText = data.result;
  })
  .catch(err => {
    console.error('Translation error:', err);
    alert('Error occurred during translation. See console for details.');
  });
}

function clearText() {
  document.getElementById("inputText").value = '';
  document.getElementById("result").innerText = '';
}

function speakOutput() {
  const text = document.getElementById("result").innerText;
  if (!text) return;

  stopSpeaking();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'hi-IN';
  synth.speak(utterance);
}

function stopSpeaking() {
  if (synth.speaking) {
    synth.cancel();
  }
}
