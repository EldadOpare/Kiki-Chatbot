/*
This was our main JavaScript file that powered the chat interface for our Ghana chatbot.
We designed this script to handle user interactions, manage conversations, integrate voice functionality,
and provide both chat and RAG mode capabilities with real-time communication to our Flask backend.

The script managed conversation history, file uploads, voice recording, and dynamic UI updates
to create a seamless chat experience for users interacting with our Ghana-focused AI assistant.
*/

//DOM Elements - We selected all the key elements we needed for the chat interface
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const newChatBtn = document.querySelector('.new-chat-btn');
const conversationList = document.getElementById('conversationList');
const ragModeRadio = document.getElementById('ragMode');
const chatModeRadio = document.getElementById('chatMode');

//Voice Elements - We set up voice recording functionality
const micBtn = document.getElementById('micBtn');
const voiceStatus = document.getElementById('voiceStatus');

//Configuration - We configured our API endpoint
const API_URL = 'http://localhost:5081/api';

//Global State - We used these variables to manage conversation state
let conversations = [];
let currentConversationId = null;

//Helper function to get the current mode - we checked the active toggle
function getCurrentMode() {
    //We checked if chat was active (chat toggle visible)
    const modeSelectorChat = document.getElementById('modeSelectorChat');
    if (modeSelectorChat && modeSelectorChat.style.display !== 'none') {
        //We used the chat toggle
        const ragModeActive = document.getElementById('ragModeActive');
        return ragModeActive && ragModeActive.checked;
    } else {
        //We used the welcome toggle
        return ragModeRadio.checked;
    }
}

function removeWelcomeMessage() {
    //We removed the welcome message when chat started
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    //We showed mode selector when chat started
    const modeSelectorChat = document.getElementById('modeSelectorChat');
    if (modeSelectorChat) {
        modeSelectorChat.style.display = 'flex';
    }
}

function formatText(text) {
    //We formatted text with markdown-like styling
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

function addMessage(text, isUser) {
    //We removed the welcome message when starting chat
    removeWelcomeMessage();

    //We created the main message container
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    //We created the message content wrapper
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';

    //We created the message header with avatar and name
    const messageHeader = document.createElement('div');
    messageHeader.className = 'message-header';

    //We created the avatar element
    const avatar = document.createElement('span');
    avatar.className = isUser ? 'user-avatar-small' : 'bot-avatar-small';

    if (isUser) {
        avatar.textContent = 'U';
    } else {
        avatar.textContent = 'K';
    }

    //We created the sender name element
    const senderName = document.createElement('span');
    senderName.className = 'sender-name';
    if (isUser) {
        senderName.textContent = 'You';
    } else {
        //We determined bot name based on current mode
        const useRag = getCurrentMode();
        senderName.textContent = useRag ? 'Rag Kiki' : 'Chat Kiki';
    }

    messageHeader.appendChild(avatar);
    messageHeader.appendChild(senderName);

    //We created the message text container
    const messageText = document.createElement('div');
    messageText.className = 'message-text';

    if (!isUser) {
        //We formatted bot messages with HTML styling
        messageText.innerHTML = formatText(text);
    } else {
        //We kept user messages as plain text
        messageText.textContent = text;
    }

    messageContent.appendChild(messageHeader);
    messageContent.appendChild(messageText);

    //We added speaker button for bot messages
    if (!isUser) {
        const speakerBtn = document.createElement('button');
        speakerBtn.className = 'message-speaker-btn';
        speakerBtn.title = 'Listen to this response';
        speakerBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
            </svg>
        `;

        //We stored the clean text for speaking
        const cleanText = text
            .replace(/\*\*/g, '')
            .replace(/\*/g, '')
            .replace(/\[.*?\]\(.*?\)/g, '')
            .replace(/<[^>]*>/g, '')
            .replace(/\n/g, ' ');

        speakerBtn.addEventListener('click', function() {
            //If already speaking this message, we stopped it
            if (speakerBtn.classList.contains('speaking')) {
                stopSpeaking();
                speakerBtn.classList.remove('speaking');
            } else {
                //We stopped any other currently playing speech
                stopSpeaking();

                //We removed speaking class from all other speaker buttons
                document.querySelectorAll('.message-speaker-btn.speaking').forEach(btn => {
                    btn.classList.remove('speaking');
                });

                //We spoke this message
                speak(cleanText);

                //We added visual feedback
                speakerBtn.classList.add('speaking');
            }
        });

        messageContent.appendChild(speakerBtn);
    }

    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoadingMessage(initialMessage = 'Kiki is thinking...') {
    // Determine bot name based on current mode
    const useRag = getCurrentMode();
    const botName = useRag ? 'Rag Kiki' : 'Chat Kiki';

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading-message';
    loadingDiv.innerHTML = `
        <div class="message-content">
            <div class="message-header">
                <span class="bot-avatar-small">K</span>
                <span class="sender-name">${botName}</span>
            </div>
            <div class="message-text">
                <span class="typing-indicator">${initialMessage}</span>
            </div>
        </div>
    `;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return loadingDiv;
}

function updateLoadingMessage(loadingDiv, message) {
    const indicator = loadingDiv.querySelector('.typing-indicator');
    if (indicator) {
        indicator.textContent = message;
    }
}

async function sendMessage() {
    const text = userInput.value.trim();

    if (text === '') {
        return;
    }

    // Stop listening when send is clicked
    if (getIsListening()) {
        stopListening();
    }

    userInput.disabled = true;
    sendBtn.disabled = true;

    addMessage(text, true);

    userInput.value = '';

    const useRag = getCurrentMode();
    const botName = useRag ? 'Rag Kiki' : 'Chat Kiki';
    const loadingMsg = showLoadingMessage(useRag ? `${botName} is thinking...` : `${botName} is thinking...`);

    const loadingMessages = useRag
        ? [`${botName} is thinking...`, 'Consulting data sources...', 'Analyzing information...', 'Preparing response...']
        : [`${botName} is thinking...`, 'Processing your question...', 'Generating response...'];

    let messageIndex = 0;
    const loadingInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % loadingMessages.length;
        updateLoadingMessage(loadingMsg, loadingMessages[messageIndex]);
    }, 2000);

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                use_rag: useRag
            })
        });

        clearInterval(loadingInterval);
        loadingMsg.remove();

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            addMessage(`Error: ${data.error}`, false);
        } else {
            addMessage(data.response, false);
            saveToConversationHistory(text);
        }

    } catch (error) {
        clearInterval(loadingInterval);
        loadingMsg.remove();
        console.error('Error:', error);
        addMessage(`Sorry, I'm having trouble connecting to the server. Please make sure the backend is running on port 5081.`, false);
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function saveToConversationHistory(firstMessage) {
    if (chatMessages.querySelectorAll('.message').length <= 2) {
        const conversationTitle = firstMessage.substring(0, 40) + (firstMessage.length > 40 ? '...' : '');
        addConversationToSidebar(conversationTitle);
    }
}



sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

newChatBtn.addEventListener('click', async () => {
    chatMessages.innerHTML = `
        <div class="welcome-message" id="welcomeMessage">
            <div class="welcome-icon-container">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                    <rect width="24" height="24" rx="6" fill="#4A72FF"/>
                    <path d="M12 6L13.5 9.5L17 11L13.5 12.5L12 16L10.5 12.5L7 11L10.5 9.5L12 6Z" fill="white"/>
                    <path d="M16 14L16.75 15.75L18.5 16.5L16.75 17.25L16 19L15.25 17.25L13.5 16.5L15.25 15.75L16 14Z" fill="white"/>
                </svg>
            </div>
            <h2>Welcome to Kiki</h2>
            <p>Your AI assistant for Ghanaian Government data and information</p>
            <div class="welcome-subtitle">Ask me anything about policies, services, and public data</div>
            <div class="mode-selector-welcome">
                <label class="mode-option-welcome">
                    <input type="radio" name="chatMode" value="rag" id="ragMode" checked>
                    <span>RAG Mode</span>
                </label>
                <label class="mode-option-welcome">
                    <input type="radio" name="chatMode" value="chat" id="chatMode">
                    <span>Chat Mode</span>
                </label>
            </div>
        </div>
    `;

    // Hide mode selector when clearing chat
    const modeSelectorChat = document.getElementById('modeSelectorChat');
    if (modeSelectorChat) {
        modeSelectorChat.style.display = 'none';
    }

    try {
        await fetch(`${API_URL}/clear`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('Error clearing history:', error);
    }

    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
});

const clearAllBtn = document.querySelector('.clear-all');
if (clearAllBtn) {
    clearAllBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        if (confirm('Are you sure you want to clear all conversations?')) {
            if (conversationList) {
                conversationList.innerHTML = '';
            }
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <h2>Welcome to Kiki</h2>
                    <p>Your AI assistant for Ghanaian Government data and information</p>
                    <div class="welcome-subtitle">Ask me anything about policies, services, and public data</div>
                </div>
            `;

            try {
                await fetch(`${API_URL}/clear`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
            } catch (error) {
                console.error('Error clearing history:', error);
            }
        }
    });
}

// Function to show mode switch notification
function showModeSwitch(modeName) {
    const notification = document.createElement('div');
    notification.className = 'mode-switch-notification';
    notification.textContent = `Switched to ${modeName}`;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: #4A72FF;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideDown 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideUp 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// Sync mode selectors
document.addEventListener('change', (e) => {
    if (e.target.name === 'chatMode') {
        const ragModeActive = document.getElementById('ragModeActive');
        const chatModeActive = document.getElementById('chatModeActive');

        if (e.target.value === 'rag' && ragModeActive) {
            ragModeActive.checked = true;
        } else if (e.target.value === 'chat' && chatModeActive) {
            chatModeActive.checked = true;
        }
    }

    if (e.target.name === 'chatModeActive') {
        const ragMode = document.getElementById('ragMode');
        const chatMode = document.getElementById('chatMode');

        if (e.target.value === 'rag' && ragMode) {
            ragMode.checked = true;
            showModeSwitch('Rag Kiki');
        } else if (e.target.value === 'chat' && chatMode) {
            chatMode.checked = true;
            showModeSwitch('Chat Kiki');
        }
    }
});

window.addEventListener('load', () => {
    userInput.focus();
    fetchClimateData();
    setInterval(fetchClimateData, 300000); // Auto-refresh every 5 minutes
});

async function fetchClimateData() {
    const API_KEY = '19942997e8fda3f20d9a4434ac3009ee';
    const ACCRA_LAT = 5.6037;
    const ACCRA_LON = -0.1870;

    const climateDataDiv = document.getElementById('climateData');

    try {
        const [weatherResponse, forecastResponse, airQualityResponse] = await Promise.all([
            fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${ACCRA_LAT}&lon=${ACCRA_LON}&units=metric&appid=${API_KEY}`),
            fetch(`https://api.openweathermap.org/data/2.5/forecast?lat=${ACCRA_LAT}&lon=${ACCRA_LON}&units=metric&appid=${API_KEY}`),
            fetch(`http://api.openweathermap.org/data/2.5/air_pollution?lat=${ACCRA_LAT}&lon=${ACCRA_LON}&appid=${API_KEY}`)
        ]);

        if (!weatherResponse.ok) throw new Error('Failed to fetch weather data');

        const weatherData = await weatherResponse.json();
        const forecastData = forecastResponse.ok ? await forecastResponse.json() : null;
        const airQualityData = airQualityResponse.ok ? await airQualityResponse.json() : null;

        const airQualityIndex = airQualityData?.list[0]?.main?.aqi;
        const airQualityLabels = ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'];
        const airQualityText = airQualityIndex ? airQualityLabels[airQualityIndex - 1] : 'N/A';

        let forecastHTML = '';
        if (forecastData?.list) {
            const dailyForecasts = {};
            forecastData.list.forEach(item => {
                const date = item.dt_txt.split(' ')[0];
                if (!dailyForecasts[date]) {
                    dailyForecasts[date] = {
                        temps: [],
                        descriptions: [],
                        date: date
                    };
                }
                dailyForecasts[date].temps.push(item.main.temp);
                dailyForecasts[date].descriptions.push(item.weather[0].description);
            });

            const today = new Date().toISOString().split('T')[0];
            const forecastDays = Object.keys(dailyForecasts)
                .filter(date => date > today)
                .slice(0, 5);

            if (forecastDays.length > 0) {
                forecastHTML = '<div class="forecast-section"><div class="forecast-title">5-Day Forecast</div>';
                forecastDays.forEach(date => {
                    const dayData = dailyForecasts[date];
                    const avgTemp = Math.round(dayData.temps.reduce((a, b) => a + b, 0) / dayData.temps.length);
                    const mostCommonDesc = dayData.descriptions.sort((a, b) =>
                        dayData.descriptions.filter(v => v === a).length - dayData.descriptions.filter(v => v === b).length
                    ).pop();
                    const dayName = new Date(date).toLocaleDateString('en-US', { weekday: 'short' });

                    forecastHTML += `
                        <div class="forecast-day">
                            <span class="forecast-day-name">${dayName}</span>
                            <span class="forecast-day-desc">${mostCommonDesc}</span>
                            <span class="forecast-day-temp">${avgTemp}°C</span>
                        </div>`;
                });
                forecastHTML += '</div>';
            }
        }

        climateDataDiv.innerHTML = `
            <div class="climate-temp">${Math.round(weatherData.main.temp)}°C</div>
            <div class="climate-description">${weatherData.weather[0].description}</div>
            <div class="climate-detail">
                <span>Feels Like</span>
                <span>${Math.round(weatherData.main.feels_like)}°C</span>
            </div>
            <div class="climate-detail">
                <span>Humidity</span>
                <span>${weatherData.main.humidity}%</span>
            </div>
            <div class="climate-detail">
                <span>Wind</span>
                <span>${weatherData.wind.speed} m/s</span>
            </div>
            <div class="climate-detail">
                <span>Pressure</span>
                <span>${weatherData.main.pressure} hPa</span>
            </div>
            <div class="climate-detail">
                <span>Air Quality</span>
                <span>${airQualityText}</span>
            </div>
            ${forecastHTML}
        `;
    } catch (error) {
        console.error('Climate data error:', error);
        climateDataDiv.innerHTML = `
            <div class="climate-temp">--°C</div>
            <div class="climate-description">Data unavailable</div>
            <div class="climate-detail">
                <span>Unable to load climate data</span>
            </div>
        `;
    }
}

const uploadBtn = document.getElementById('uploadBtn');
const uploadMenu = document.getElementById('uploadMenu');
const toolsBtn = document.getElementById('toolsBtn');
const toolsMenu = document.getElementById('toolsMenu');
const fileInput = document.getElementById('fileInput');
const imageInput = document.getElementById('imageInput');
const uploadDocOption = document.getElementById('uploadDocOption');
const uploadImageOption = document.getElementById('uploadImageOption');

uploadBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    uploadMenu.style.display = uploadMenu.style.display === 'none' ? 'block' : 'none';
    toolsMenu.style.display = 'none';
});

uploadDocOption.addEventListener('click', () => {
    fileInput.click();
    uploadMenu.style.display = 'none';
});

uploadImageOption.addEventListener('click', () => {
    imageInput.click();
    uploadMenu.style.display = 'none';
});

toolsBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toolsMenu.style.display = toolsMenu.style.display === 'none' ? 'block' : 'none';
    uploadMenu.style.display = 'none';
});

document.addEventListener('click', (e) => {
    if (!toolsMenu.contains(e.target) && e.target !== toolsBtn) {
        toolsMenu.style.display = 'none';
    }
    if (!uploadMenu.contains(e.target) && e.target !== uploadBtn) {
        uploadMenu.style.display = 'none';
    }
});

toolsMenu.addEventListener('click', () => {
    toolsMenu.style.display = 'none';
});

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const loadingMsg = showLoadingMessage(`Uploading "${file.name}"...`);

    const uploadMessages = [
        `Uploading "${file.name}"...`,
        'Document is being ingested...',
        'Extracting text content...',
        'Chunking document...',
        'Creating embeddings...',
        'Almost done...'
    ];

    let messageIndex = 0;
    const uploadInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % uploadMessages.length;
        updateLoadingMessage(loadingMsg, uploadMessages[messageIndex]);
    }, 2500);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_URL}/upload_pdf`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        clearInterval(uploadInterval);
        loadingMsg.remove();

        if (data.success) {
            addMessage(data.message || 'Document uploaded and processed successfully!', false);
        } else {
            addMessage(`Error: ${data.error}`, false);
        }
    } catch (error) {
        clearInterval(uploadInterval);
        loadingMsg.remove();
        console.error('Upload error:', error);
        addMessage('Sorry, there was an error uploading the file.', false);
    }

    fileInput.value = '';
});

imageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const loadingMsg = showLoadingMessage(`Processing image "${file.name}"...`);

    const imageMessages = [
        `Processing image "${file.name}"...`,
        'Analyzing image content...',
        'Extracting visual information...',
        'Finalizing upload...'
    ];

    let messageIndex = 0;
    const imageInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % imageMessages.length;
        updateLoadingMessage(loadingMsg, imageMessages[messageIndex]);
    }, 2000);

    try {
        const formData = new FormData();
        formData.append('image', file);

        const response = await fetch(`${API_URL}/upload_image`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        clearInterval(imageInterval);
        loadingMsg.remove();

        if (data.success) {
            addMessage(data.message || 'Image uploaded successfully!', false);
        } else {
            addMessage(`Error: ${data.error}`, false);
        }
    } catch (error) {
        clearInterval(imageInterval);
        loadingMsg.remove();
        console.error('Image upload error:', error);
        addMessage('Sorry, there was an error uploading the image.', false);
    }

    imageInput.value = '';
});


// =============================================================================
// VOICE FEATURES INTEGRATION
// =============================================================================

// Check if voice features are supported
const voiceSupport = checkVoiceSupport();

// Show browser compatibility message if voice features not supported
if (!voiceSupport.speechRecognition || !voiceSupport.speechSynthesis) {
    // Only show message once per session
    if (!sessionStorage.getItem('voiceCompatibilityShown')) {
        setTimeout(function() {
            let missingFeatures = [];
            if (!voiceSupport.speechRecognition) missingFeatures.push('voice input');
            if (!voiceSupport.speechSynthesis) missingFeatures.push('voice output');

            const message = `Voice features (${missingFeatures.join(' and ')}) are not supported in this browser. For the best experience, please use Chrome or Edge.`;

            // Show as a friendly notification
            const notification = document.createElement('div');
            notification.className = 'browser-compatibility-notice';
            notification.innerHTML = `
                <div class="compatibility-icon">ℹ️</div>
                <div class="compatibility-text">${message}</div>
                <button class="compatibility-close" onclick="this.parentElement.remove()">×</button>
            `;
            document.body.appendChild(notification);

            sessionStorage.setItem('voiceCompatibilityShown', 'true');

            // Auto-dismiss after 10 seconds
            setTimeout(function() {
                if (notification.parentElement) {
                    notification.style.animation = 'slideUp 0.3s ease';
                    setTimeout(function() {
                        notification.remove();
                    }, 300);
                }
            }, 10000);
        }, 2000);
    }
}

// Hide microphone button if not supported
if (!voiceSupport.speechRecognition && micBtn) {
    micBtn.style.display = 'none';
}

// Setup voice callbacks
setOnSpeechResult(function(text) {
    // Update input field with recognized speech
    userInput.value = text;
});

setOnListeningChange(function(isListening) {
    // Update mic button appearance
    if (isListening) {
        micBtn.classList.add('listening');
        micBtn.title = 'Stop Listening';

        // Show listening status
        if (voiceStatus) {
            voiceStatus.style.display = 'flex';
            voiceStatus.className = 'voice-status listening';
            voiceStatus.querySelector('.voice-status-text').textContent = 'Listening...';
        }
    } else {
        micBtn.classList.remove('listening');
        micBtn.title = 'Voice Input';

        // Hide listening status
        if (voiceStatus && !getIsSpeaking()) {
            voiceStatus.style.display = 'none';
        }
    }
});

setOnSpeakingChange(function(speaking) {
    // Update speaking status
    if (speaking) {
        // Show speaking status
        if (voiceStatus) {
            voiceStatus.style.display = 'flex';
            voiceStatus.className = 'voice-status speaking';
            voiceStatus.querySelector('.voice-status-text').textContent = 'Speaking...';
        }
    } else {
        // Hide speaking status
        if (voiceStatus && !getIsListening()) {
            voiceStatus.style.display = 'none';
        }

        // Remove speaking class from all message speaker buttons
        document.querySelectorAll('.message-speaker-btn.speaking').forEach(btn => {
            btn.classList.remove('speaking');
        });
    }
});

// Microphone button click handler
if (micBtn) {
    micBtn.addEventListener('click', function() {
        toggleListening();
    });
}

// =============================================================================
// VOICE SELECTOR FUNCTIONALITY
// =============================================================================

const voiceSelect = document.getElementById('voiceSelect');

/**
 * Populate the voice selector dropdown with available voices
 */
function populateVoiceSelector() {
    const voices = getAvailableVoices();

    if (voices.length === 0 || !voiceSelect) {
        // Voices not loaded yet, wait for them
        setTimeout(populateVoiceSelector, 100);
        return;
    }

    // Clear existing options
    voiceSelect.innerHTML = '';

    // Group voices by language for better organization
    const englishVoices = voices.filter(v => v.lang.startsWith('en'));
    const otherVoices = voices.filter(v => !v.lang.startsWith('en'));

    // Add English voices first
    if (englishVoices.length > 0) {
        const englishGroup = document.createElement('optgroup');
        englishGroup.label = 'English Voices';

        englishVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = voice.name;
            englishGroup.appendChild(option);
        });

        voiceSelect.appendChild(englishGroup);
    }

    // Add other language voices
    if (otherVoices.length > 0) {
        const otherGroup = document.createElement('optgroup');
        otherGroup.label = 'Other Languages';

        otherVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = voice.name;
            otherGroup.appendChild(option);
        });

        voiceSelect.appendChild(otherGroup);
    }

    // Set the selected voice in the dropdown
    updateVoiceSelector();
}

/**
 * Update the dropdown to show the currently selected voice
 */
function updateVoiceSelector() {
    const voices = getAvailableVoices();
    const currentVoice = voices.find(v => v.name === voiceSelect.value);

    // If no voice is selected, select the first English voice or first available
    if (!currentVoice) {
        const englishVoice = voices.find(v => v.lang.startsWith('en'));
        if (englishVoice) {
            voiceSelect.value = englishVoice.name;
        } else if (voices.length > 0) {
            voiceSelect.value = voices[0].name;
        }
    }
}

/**
 * Handle voice selection change
 */
if (voiceSelect) {
    voiceSelect.addEventListener('change', function() {
        const selectedVoiceName = this.value;
        const success = setVoice(selectedVoiceName);

        if (success) {
            console.log('Voice changed to:', selectedVoiceName);

            // Optional: Speak a sample text to preview the voice
            // Uncomment the line below if you want to hear the voice when selected
            // speak('Hello, this is the selected voice.');
        }
    });
}

// Initialize voice selector when page loads
if (typeof window !== 'undefined' && window.speechSynthesis) {
    // Wait for voices to load
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = populateVoiceSelector;
    }

    // Also try immediately in case voices are already loaded
    setTimeout(populateVoiceSelector, 200);
}
