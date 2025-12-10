/*
This was our URL scraping interface script that handled web content analysis and querying functionality.
We designed this script to provide a two-step process where users could ask questions about web content,
allowing them to scrape URLs and get contextual answers based on the scraped content.

The script managed URL validation, progress tracking, and communication with our Flask backend
to scrape web content and provide answers based on the extracted information.
*/


//API Configuration - We configured our Flask backend endpoint
const API_URL = 'http://localhost:5081/api';

//DOM Elements - We selected all the elements needed for the URL scraping interface
const queryInput = document.getElementById('queryInput');

const nextToUrlBtn = document.getElementById('nextToUrlBtn');

const querySection = document.getElementById('querySection');

const urlSection = document.getElementById('urlSection');

const resultsSection = document.getElementById('resultsSection');

const urlInput = document.getElementById('urlInput');

const backToQueryBtn = document.getElementById('backToQueryBtn');

const submitBtn = document.getElementById('submitBtn');

const displayQuestion = document.getElementById('displayQuestion');

const displayUrl = document.getElementById('displayUrl');

const answerDisplay = document.getElementById('answerDisplay');

const newQueryBtn = document.getElementById('newQueryBtn');

//Progress Indicators - We used these to show the user's progress through the steps
const progress1 = document.getElementById('progress1');

const progress2 = document.getElementById('progress2');

const progress3 = document.getElementById('progress3');

//Step 1: Next to URL input - We handled moving from query input to URL input
nextToUrlBtn.addEventListener('click', () => {
    const query = queryInput.value.trim();

    if (!query) {
        alert('Please enter a question first');
        return;
    }

    //We moved to URL section
    querySection.classList.remove('active');
    urlSection.classList.add('active');

    //We updated progress indicators
    progress1.classList.add('completed');
    progress1.classList.remove('active');
    progress2.classList.add('active');
});

//Back to query functionality - We allowed users to go back and edit their question
backToQueryBtn.addEventListener('click', () => {
    urlSection.classList.remove('active');
    querySection.classList.add('active');

    //We updated progress indicators
    progress2.classList.remove('active');
    progress1.classList.add('active');
    progress1.classList.remove('completed');
});

//Step 2: Submit and get answer - We handled the final submission and processing
submitBtn.addEventListener('click', async () => {
    const query = queryInput.value.trim();
    const url = urlInput.value.trim();

    if (!query) {
        alert('Please enter a question');
        return;
    }

    if (!url) {
        alert('Please enter a URL');
        return;
    }

    //We performed basic URL validation
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        alert('URL must start with http:// or https://');
        return;
    }

    //We moved to results section
    urlSection.classList.remove('active');
    resultsSection.classList.add('active');

    //We updated progress indicators
    progress2.classList.add('completed');
    progress2.classList.remove('active');
    progress3.classList.add('active');

    // Display question and URL
    displayQuestion.textContent = query;
    displayUrl.textContent = url;

    // Show loading
    answerDisplay.innerHTML = `
        <div class="loading-answer">
            <div class="loader"></div>
            <span class="typing-indicator">Kiki is analyzing the webpage...</span>
        </div>
    `;

    try {
        // First, scrape the URL and add to database with document ID
        const scrapeResponse = await fetch(`${API_URL}/scrape_url_rag`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const scrapeData = await scrapeResponse.json();

        if (!scrapeData.success) {
            answerDisplay.innerHTML = `
                <div class="answer-text" style="color: #d32f2f;">
                    <strong>Error:</strong> ${scrapeData.error}
                </div>
            `;
            return;
        }

        // Now query with the document ID
        const queryResponse = await fetch(`${API_URL}/query_document`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: query,
                document_id: scrapeData.document_id
            })
        });

        const queryData = await queryResponse.json();

        if (queryData.success) {
            // Format answer with markdown support
            let answerText = queryData.answer;

            // Convert **bold** to <strong>bold</strong>
            answerText = answerText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

            // Convert *italic* to <em>italic</em>
            answerText = answerText.replace(/\*(.*?)\*/g, '<em>$1</em>');

            // Convert newlines to <br>
            answerText = answerText.replace(/\n/g, '<br>');

            answerDisplay.innerHTML = `
                <div class="answer-text">${answerText}</div>
            `;
        } else {
            answerDisplay.innerHTML = `
                <div class="answer-text" style="color: #d32f2f;">
                    <strong>Error:</strong> ${queryData.error}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        answerDisplay.innerHTML = `
            <div class="answer-text" style="color: #d32f2f;">
                <strong>Error:</strong> Failed to connect to the server. Please make sure the backend is running.
            </div>
        `;
    }
});

// Start a new query
newQueryBtn.addEventListener('click', () => {
    // Reset everything
    queryInput.value = '';
    urlInput.value = '';

    // Go back to step 1
    resultsSection.classList.remove('active');
    querySection.classList.add('active');

    // Reset progress
    progress1.classList.add('active');
    progress1.classList.remove('completed');
    progress2.classList.remove('active');
    progress2.classList.remove('completed');
    progress3.classList.remove('active');
    progress3.classList.remove('completed');
});
