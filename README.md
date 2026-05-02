# NaviX 🗺️
**Urban Safety-Aware Navigation Engine**

NaviX is an advanced navigation backend designed to prioritize pedestrian and vehicular safety in complex urban environments. While traditional routing engines strictly optimize for distance or time, NaviX introduces a dynamic **Safety Risk Engine** that actively evaluates spatial features like street lighting density, Points of Interest (POIs), road isolation, and human presence proxies.

## 🚀 Key Features
- **Intelligent Routing**: Modified A* pathfinding algorithm providing three distinct route options: **Safest**, **Balanced**, and **Shortest**.
- **Multithreaded Safety Engine**: Asynchronously queries OpenStreetMap spatial features via PostGIS to score road segments based on environmental risk factors.
- **Automated Data Population**: Automatically fetches and scores road networks for new areas (localized to Dehradun, India).
- **Containerized Architecture**: Full stack deployment using Docker Compose (React + FastAPI + PostGIS).
- **Real-time Feedback**: Dynamic progress bar and status updates during large-scale data computations.

## ⚙️ Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- PowerShell (on Windows)

### Running the App
1. **Clone & Setup**:
   ```powershell
   git clone https://github.com/AnanyaRana2312/NaviX.git
   cd NaviX
   cp demo.env .env
   ```
2. **Start Everything**:
   ```powershell
   .\start.ps1
   ```
   *This will build the containers, initialize the database, and show you the local/network links.*

3. **Stop Everything**:
   ```powershell
   .\stop.ps1
   ```

## 🛠️ Technology Stack
- **Frontend**: React (Vite), TailwindCSS, Leaflet
- **Backend**: FastAPI (Python), Uvicorn
- **Database**: PostgreSQL 15 + PostGIS
- **Data**: OSMnx, NetworkX, GeoPandas, Scikit-learn
- **Orchestration**: Docker Compose

## 👥 Team
- **Ananya Rana**: DevOps & Frontend Integration
- **Pranav Akshit**: Backend Architecture & Safety Modeling
- **Zoya**: UI/UX Design

---
*Developed as a collaborative prototype for spatial data science and routing algorithms.*
