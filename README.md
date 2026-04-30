# NaviX 🗺️
**Urban Safety-Aware Navigation Engine**

NaviX is an advanced navigation backend designed to prioritize pedestrian and vehicular safety in complex urban environments. While traditional routing engines strictly optimize for distance or time, NaviX introduces a dynamic **Safety Risk Engine** that actively evaluates spatial features like street lighting density, Points of Interest (POIs), road isolation, and human presence proxies.

## 🚀 Key Features
- **Intelligent Routing**: Modified A* pathfinding algorithm providing three distinct route options: Shortest, Safest, and Balanced.
- **Multithreaded Safety Engine**: Asynchronously queries OpenStreetMap spatial features via PostGIS to score road segments based on environmental risk factors.
- **Robust API**: A high-performance FastAPI backend delivering precise GeoJSON coordinates and segment-level metadata.
- **Spatial Database**: Powered by PostgreSQL + PostGIS, utilizing highly optimized spatial GiST indexing.

## 🛠️ Technology Stack
- **Backend Framework:** FastAPI (Python)
- **Database:** PostgreSQL + PostGIS
- **Data Ingestion:** OSMnx, Overpass API
- **Graph Processing:** NetworkX, SciPy
- **Containerization:** Docker, Docker Compose
- **Testing UI:** Streamlit, Folium Maps

## ⚙️ Local Development Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.10+

### Running the Project
1. **Clone the repository:**
   ```bash
   git clone https://github.com/AnanyaRana2312/NaviX.git
   cd NaviX
   ```

2. **Setup the Environment:**
   Ensure your `.env` file is present at the root of the project with the required database credentials (`DB_USER`, `DB_PASSWORD`, etc.).

3. **Start the Database (Docker):**
   Spin up the PostGIS container:
   ```bash
   docker-compose up -d db
   ```

4. **Run the Application (Windows):**
   Execute the startup script to automatically initialize the virtual environment, install dependencies, and launch both the FastAPI backend and Streamlit demo UI:
   ```cmd
   .\start.bat
   ```

## 👥 Team Roles
- **Member 1**: DevOps Engineering & Frontend Integration
- **Member 2**: Backend Architecture, Dataset Management, & Safety Modeling
- **Member 3**: UI/UX Design & Frontend Development

---
*Developed as a collaborative prototype for spatial data science and routing algorithms.*
