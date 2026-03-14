#!/bin/bash
echo "Starting NaviX backend..."
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

sleep 2

echo "Starting NaviX Streamlit UI..."
streamlit run scripts/demo_ui.py

# When Streamlit exits, also kill the backend
echo "Streamlit exited. Stopping backend (PID: $BACKEND_PID)..."
kill $BACKEND_PID
echo "Done."
