/*
This was our voice utility module that provided speech-to-text and text-to-speech functionality for our Ghana chatbot.
We designed this module to work entirely in the browser using the Web Speech API, requiring no backend processing
and providing zero-latency voice interactions for users.

We implemented voice input for speech recognition and voice output for reading bot responses aloud,
creating a hands-free chat experience for users who preferred voice interaction.
*/



//We stored the speech recognition object (for listening)
let recognition = null;          

//We tracked whether we were currently listening
let isListening = false;  

//We tracked whether we were currently speaking
let isSpeaking = false;          

//We controlled whether responses were spoken automatically
let autoSpeak = true;      

//We stored the selected voice for speech generation
let selectedVoice = null;       

//Callbacks - we set these from the main app to handle voice events

//We called this when we heard speech
let onSpeechResult = null;     

//We called this when listening status changed
let onListeningChange = null;   

//We called this when speaking status changed
let onSpeakingChange = null;     




// We checked if the browser supported voice features and returned what was available

function checkVoiceSupport() {
    const support = {
        speechRecognition: false,
        speechSynthesis: false
    };

    //We checked for speech recognition (voice input) support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        support.speechRecognition = true;
    }

    //We checked for speech synthesis (voice output) support
    if ('speechSynthesis' in window) {
        support.speechSynthesis = true;
    }

    return support;
}




// We initialized speech recognition and set up the microphone listener

function initSpeechRecognition() {

    // We got the recognition class different browsers used different names
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        return false;
    }

    //We created the recognition object
    recognition = new SpeechRecognition();

    //We configured recognition with our preferred settings

    //We kept listening until we stopped
    recognition.continuous = true;           
    recognition.interimResults = true;     
    recognition.lang = 'en-US';             

    //When we got speech results
    recognition.onresult = function(event) {
        let finalTranscript = '';
        let interimTranscript = '';

        // Loop through ALL results from the beginning to accumulate text
        for (let i = 0; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }

        // Call the callback with accumulated text (final + interim)
        if (onSpeechResult) {
            const fullText = finalTranscript + interimTranscript;
            onSpeechResult(fullText);
        }
    };

    // When recognition ends
    recognition.onend = function() {
        isListening = false;
        if (onListeningChange) {
            onListeningChange(false);
        }
    };

    // If there's an error
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        isListening = false;
        if (onListeningChange) {
            onListeningChange(false);
        }
    };

    return true;
}


// Start listening to user's voice
function startListening() {
    if (!recognition) {
        const initialized = initSpeechRecognition();
        if (!initialized) {
            alert('Voice input is not supported in this browser. Please use Chrome or Edge.');
            return;
        }
    }

    if (isListening) {
        return; // Already listening
    }

    try {
        recognition.start();
        isListening = true;

        if (onListeningChange) {
            onListeningChange(true);
        }
    } catch (error) {
        console.error('Error starting recognition:', error);
    }
}



// Stop listening to user's voice
 
function stopListening() {
    if (!recognition || !isListening) {
        return;
    }

    try {
        recognition.stop();
        isListening = false;

        if (onListeningChange) {
            onListeningChange(false);
        }
    } catch (error) {
        console.error('Error stopping recognition:', error);
    }
}



// Toggle listening on/off
 
function toggleListening() {
    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
}




// We got the list of available voices for speech synthesis
function getAvailableVoices() {
    if (!window.speechSynthesis) {
        return [];
    }
    return window.speechSynthesis.getVoices();
}



function initVoice() {
    const voices = getAvailableVoices();

    if (voices.length === 0) {

        // Voices not loaded yet, try again when they load
        window.speechSynthesis.onvoiceschanged = function() {
            initVoice();
        };
        return;
    }


    const preferredVoices = [
        'Google US English',
        'Google UK English Female',
        'Microsoft Zira - English (United States)',
        'Samantha',
        'Karen',
        'Victoria',
        'Alex'
    ];

    // Try to find a preferred voice
    for (const voiceName of preferredVoices) {
        const voice = voices.find(v => v.name === voiceName);
        if (voice) {
            selectedVoice = voice;
            console.log('Selected voice:', voice.name);
            return;
        }
    }

    // Fallback: look for any high-quality English voice
    const englishVoices = voices.filter(v => v.lang.startsWith('en'));

    // Prefer Google or Premium voices
    const googleVoice = englishVoices.find(v => v.name.includes('Google'));
    if (googleVoice) {
        selectedVoice = googleVoice;
        console.log('Selected voice:', googleVoice.name);
        return;
    }

    // Otherwise use first English voice
    if (englishVoices.length > 0) {
        selectedVoice = englishVoices[0];
        console.log('Selected voice:', englishVoices[0].name);
    }
}

// Set the voice by name
function setVoice(voiceName) {
    const voices = getAvailableVoices();
    const voice = voices.find(v => v.name === voiceName);

    if (voice) {
        selectedVoice = voice;
        console.log('Voice changed to:', voice.name);
        return true;
    }

    console.warn('Voice not found:', voiceName);
    return false;
}


function speak(text) {
    if (!window.speechSynthesis) {
        console.warn('Speech synthesis not supported in this browser');
        return;
    }

    // Initialize voice if not done yet
    if (!selectedVoice) {
        initVoice();
    }

    // Stop any current speech
    window.speechSynthesis.cancel();

    // Create utterance (the thing to speak)
    const utterance = new SpeechSynthesisUtterance(text);

    // Set the voice
    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }

    // Configure voice settings - adjusted for better quality

    utterance.rate = 1.1;     
    
    utterance.pitch = 1.0;    
    
    utterance.volume = 1.0;   

    // When speech starts
    utterance.onstart = function() {
        isSpeaking = true;
        if (onSpeakingChange) {
            onSpeakingChange(true);
        }
    };

    // When speech ends
    utterance.onend = function() {
        isSpeaking = false;
        if (onSpeakingChange) {
            onSpeakingChange(false);
        }
    };

    // If there's an error
    utterance.onerror = function(event) {
        console.error('Speech synthesis error:', event.error);
        isSpeaking = false;
        if (onSpeakingChange) {
            onSpeakingChange(false);
        }
    };

    // Speak!
    window.speechSynthesis.speak(utterance);
}



// Stop speaking
 
function stopSpeaking() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        isSpeaking = false;

        if (onSpeakingChange) {
            onSpeakingChange(false);
        }
    }
}



// Toggle auto-speak on/off
 
function toggleAutoSpeak() {
    autoSpeak = !autoSpeak;
    return autoSpeak;
}



function getIsListening() {
    return isListening;
}

function getIsSpeaking() {
    return isSpeaking;
}

function getAutoSpeak() {
    return autoSpeak;
}


function setOnSpeechResult(callback) {
    onSpeechResult = callback;
}

function setOnListeningChange(callback) {
    onListeningChange = callback;
}

function setOnSpeakingChange(callback) {
    onSpeakingChange = callback;
}


// Initialize voice selection when page loads
if (typeof window !== 'undefined') {

    if (window.speechSynthesis) {

        // Some browsers need a delay to load voices
        setTimeout(initVoice, 100);
        window.speechSynthesis.onvoiceschanged = initVoice;
    }
}
