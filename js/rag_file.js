/*
This was our RAG file upload interface script that handled document upload and querying functionality.
We designed this script to provide a step-by-step process where users could ask questions about uploaded documents,
creating a temporary RAG collection for document-specific queries.

The script managed file uploads, progress indicators, and communication with our Flask backend
to process documents and provide contextual answers based on the uploaded content.
*/

//API Configuration - We configured our Flask backend endpoint
const API_URL = 'http://localhost:5081/api';

//DOM Elements - We selected all the elements needed for the RAG file interface
const queryInput = document.getElementById('queryInput');
const nextToUploadBtn = document.getElementById('nextToUploadBtn');
const querySection = document.getElementById('querySection');
const uploadSection = document.getElementById('uploadSection');
const resultsSection = document.getElementById('resultsSection');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectedFile = document.getElementById('selectedFile');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFileBtn');
const backToQueryBtn = document.getElementById('backToQueryBtn');
const submitBtn = document.getElementById('submitBtn');
const displayQuestion = document.getElementById('displayQuestion');
const answerDisplay = document.getElementById('answerDisplay');
const newQueryBtn = document.getElementById('newQueryBtn');

//Progress Indicators - We used these to show the user's progress through the steps
const progress1 = document.getElementById('progress1');
const progress2 = document.getElementById('progress2');
const progress3 = document.getElementById('progress3');

//Global State - We stored the selected file for processing
let selectedPdfFile = null;

//Step 1: Next to upload - We handled moving from query input to file upload
nextToUploadBtn.addEventListener('click', () => {
    const query = queryInput.value.trim();

    if (!query) {
        alert('Please enter a question first');
        return;
    }

    //We moved to upload section
    querySection.classList.remove('active');
    uploadSection.classList.add('active');

    //We updated progress indicators
    progress1.classList.add('completed');
    progress1.classList.remove('active');
    progress2.classList.add('active');
});

//Step 2: File upload handling - We set up file selection and drag-and-drop
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

//Drag and drop functionality - We implemented file drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

//File input change handler - We handled traditional file selection
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileSelect(file);
    }
});

function handleFileSelect(file) {
    //We defined allowed file extensions
    const allowedExtensions = ['.pdf', '.docx', '.pptx', '.csv', '.xlsx', '.xls'];
    const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

    if (!allowedExtensions.includes(fileExt)) {
        alert('Please select a supported file type: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx, .xls), or CSV');
        return;
    }

    selectedPdfFile = file;
    fileName.textContent = file.name;
    uploadArea.style.display = 'none';
    selectedFile.classList.add('active');
    submitBtn.disabled = false;
}

removeFileBtn.addEventListener('click', () => {
    selectedPdfFile = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    selectedFile.classList.remove('active');
    submitBtn.disabled = true;
});

backToQueryBtn.addEventListener('click', () => {
    uploadSection.classList.remove('active');
    querySection.classList.add('active');

    // Update progress
    progress2.classList.remove('active');
    progress1.classList.add('active');
    progress1.classList.remove('completed');
});

// Step 3: Submit and get answer
submitBtn.addEventListener('click', async () => {
    const query = queryInput.value.trim();

    if (!query || !selectedPdfFile) {
        alert('Please provide both a question and a file');
        return;
    }

    // Move to results section
    uploadSection.classList.remove('active');
    resultsSection.classList.add('active');

    // Update progress
    progress2.classList.add('completed');
    progress2.classList.remove('active');
    progress3.classList.add('active');

    // Display question
    displayQuestion.textContent = query;

    // Show loading
    answerDisplay.innerHTML = `
        <div class="loading-answer">
            <div class="loader"></div>
            <span class="typing-indicator">Kiki is analyzing your document...</span>
        </div>
    `;

    try {
        const formData = new FormData();
        formData.append('file', selectedPdfFile);
        formData.append('question', query);

        const response = await fetch(`${API_URL}/rag_file`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Format answer with markdown support
            let answerText = data.answer;

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
                    <strong>Error:</strong> ${data.error}
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
    selectedPdfFile = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    selectedFile.classList.remove('active');
    submitBtn.disabled = true;

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
