let currentAudio = null;

async function generateAndPlayTTS(text) {
    if (currentAudio) currentAudio.pause();
    try {
        // Asks your Python backend to trigger the generation task safely
        await fetch(`/api/proxy-tts?text=${encodeURIComponent(text)}`);
        
        // Audio generation target path
        const staticFileUrl = `https://shahid202-kokoro-api.hf.space/static/output.wav?v=${Date.now()}`;
        currentAudio = new Audio(staticFileUrl);
        
        const lipSync = () => {
            if (currentAudio && !currentAudio.paused && !currentAudio.ended) {
                let val = Math.abs(Math.sin(Date.now() / 55)) * 0.85;
                if(model) model.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', val);
                requestAnimationFrame(lipSync);
            } else { 
                if(model) model.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', 0); 
            }
        };
        currentAudio.addEventListener('play', lipSync);
        await currentAudio.play();
    } catch (err) { console.error("Audio system error:", err); }
}

async function handleSend() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if(!text) return;
    input.value = '';

    appendMessage(text, true);
    document.getElementById('typing-indicator').style.display = 'block';

    try {
        // Talks directly to your secure Python backend instead of Hugging Face
        const res = await fetch("/api/proxy-chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        const responseText = data.response || "...";
        
        document.getElementById('typing-indicator').style.display = 'none';
        appendMessage(responseText, false);
        await generateAndPlayTTS(responseText);
    } catch(e) { 
        document.getElementById('typing-indicator').style.display = 'none'; 
    }
}

function appendMessage(text, isUser) {
    const hist = document.getElementById('chat-history');
    const d = document.createElement('div');
    d.className = `message ${isUser ? 'user-msg' : 'bot-msg'}`;
    d.innerText = text;
    hist.appendChild(d);
    hist.scrollTop = hist.scrollHeight;
}

document.getElementById('user-input').onkeydown = e => e.key === 'Enter' && handleSend();

