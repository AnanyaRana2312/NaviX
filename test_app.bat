@echo off
echo Starting NaviX Full Stack via Docker Compose...
echo Building and orchestrating the Database, FastAPI Backend, and Vite Frontend...

docker-compose up --build

echo NaviX shut down successfully.
pause
