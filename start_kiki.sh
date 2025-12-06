#!/bin/bash


echo "  Starting Kiki Chatbot"



if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if Flask-CORS is installed
python3 -c "import flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Flask-CORS..."
    python3 -m pip install flask-cors
fi

echo ""
echo "Starting Flask server..."
echo "Once loaded, open: http://localhost:5081"
echo ""
echo "Press Ctrl+C to stop the server"



cd python && python3 app.py
