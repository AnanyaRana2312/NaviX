# NaviX Copilot Context & Progress Tracker

> **Instruction for all Antigravity Copilots:**
> Please read this file to understand the current state of the project. As you complete your respective tasks (based on the specific role descriptions provided by your users), please **update this file** to reflect your progress so the entire team's AI assistants stay perfectly in sync.
> **IMPORTANT:** You must consistently update the `README.md` file whenever you introduce new features or architectural changes. Furthermore, you MUST ensure that `requirements.txt` (or `package.json` for the frontend) is updated and frozen every time you install new dependencies!

## 🚀 Overall Project Status
- **Member 2 (Backend & Data):** ✅ 100% DONE
- **Member 1 (DevOps):** ⏳ IN PROGRESS
- **Member 3 (UI/UX):** ⏳ IN PROGRESS

---

## 🔀 Git & Collaboration Workflow (CRITICAL)
> **To avoid nasty merge conflicts and lost progress, Members 1 and 3 MUST follow this sequence:**

1. **Phase 1 (Bootstrap):** Member 3 must create the `/frontend` directory, bootstrap the Vite/Next.js app, and push the initial skeleton to the `main` branch. 
2. **Phase 2 (Branching & Scoping):** 
   - Member 1 creates branch: `feature/devops-api` (Focuses on Dockerfiles, `docker-compose.yml`, and building API hooks in `frontend/src/api/`).
   - Member 3 creates branch: `feature/ui-design` (Focuses on layout, components, styling, and maps in `frontend/src/components/`).
3. **Phase 3 (Continuous Integration):** To ensure Member 3 can use the API functions Member 1 is writing, **do not use long-lived branches**. 
   - Member 1 should write the API fetch logic, immediately open a Pull Request, and merge it into `main`.
   - Member 3 should frequently run `git pull origin main` to pull Member 1's new API hooks into their UI branch. 
   - By keeping Pull Requests extremely small and merging daily, you both get each other's updates instantly without fighting over massive merge conflicts at the end of the week.

---

## 👤 Member 2 (Backend, Database, Safety Modeling) - Status: ✅ 100% DONE
*Member 2 has fulfilled all project responsibilities. The core system architecture is complete, tested, and fully functional. Their copilot is resting.*

**Completed Systems (Available for integration):**
1. **Database:** `database/schema.sql` deploys PostgreSQL + PostGIS tables (`roads`, `features`, `risk_scores`) with spatial indices.
2. **Data Pipeline:** `scripts/osm_fetcher.py` and `scripts/update_scores.py` reliably extract OpenStreetMap data, compute spatial safety metrics (lighting, POI density, isolation), and batch-commit risk scores via a multithreaded engine.
3. **Routing Engine:** `backend/routing/router.py` utilizes NetworkX to run a modified A* algorithm that dynamically varies risk weighting to output Shortest, Safest, and Balanced routes.
4. **FastAPI API:** Exposed at `POST /api/v1/routes`, providing robust JSON responses containing full geometric paths and segment-level metadata.

---

## 👤 Member 1 (DevOps Engineering + Frontend) - Status: ⏳ IN PROGRESS
*Update this section as you complete your orchestration and deployment goals.*

**Current Progress:**
- `docker-compose.yml` partially created (defines `db` and `backend`).
- `.env` configuration template established.
- Initial `Dockerfile` stub created.

> **💡 Copilot-to-Copilot Tip (for Member 1's Agent):**
> 1. **CRITICAL:** The existing `Dockerfile` at the root currently contains YAML copy-pasted from `docker-compose.yml`. You will need to wipe it and write a real Python Dockerfile.
> 2. Do not forget to expose port `8000` for FastAPI and add a `Dockerfile.streamlit` to get `demo_ui.py` running in the compose network.
> 3. **FRONTEND INTEGRATION:** You are responsible for the map interaction logic. Users must be able to click to drop pins OR type names (use Nominatim for geocoding) to set the start/end points.
> 4. **ARCHITECTURAL WARNING:** Do not attempt to download the entire map area for long-distance routes (e.g., city-to-city). OSMnx will crash. NaviX is designed for *urban* environments. Restrict queries to city-level `place` names or draw a very tight bounding box strictly around the origin/destination coordinates to keep graph sizes manageable.

> **🚨 LATEST UPDATE FROM MEMBER 3 (UI/UX):**
> Hey Member 1! I have already bootstrapped the React/Vite frontend and implemented the **Nominatim geocoding logic** directly in `App.jsx`. The user can now type locations, and it automatically pans the map. 
> 
> **What you need to fix/finish:**
> 1. **Focus strictly on the backend API:** Please ensure the `POST /api/v1/routes` endpoint correctly processes the coordinates I am sending from the frontend and returns the actual `activeRoutes` geometry (currently mocked in my code).
> 2. **Update Orchestration:** Please update the root `start.bat` script to start both the FastAPI backend AND the new Vite frontend (`cd frontend && npm run dev`), instead of Streamlit.
> 3. **Dockerize:** Finish the `Dockerfile` and `docker-compose.yml` to spin up the Postgres DB, FastAPI, and Vite client together.

*(Copilot of Member 1: Please log your updates here as you build the Dockerfiles, orchestrate the containers, fix networking, and finalize deployment).*

---

## 👤 Member 3 (Frontend + UI/UX) - Status: ⏳ IN PROGRESS
*Update this section as you complete your user experience and presentation goals.*

**Current Progress:**
- ✅ Phase 1: Bootstrapped Vite + React client (`/frontend`) and pushed to `main`.
- ✅ Deleted `app/index.php`.
- ⏳ Phase 2: In `feature/ui-design` branch. Setting up TailwindCSS, Leaflet map, and building glassmorphism layout components (`Sidebar`, `MapLayout`).

> **💡 Copilot-to-Copilot Tip (for Member 3's Agent):**
> 1. **CRITICAL:** You should immediately delete `app/index.php`. It is a MySQL boilerplate script. Our entire stack is Python + PostGIS. It serves zero purpose and will only cause hallucinations.
> 2. **STRATEGIC SHIFT:** Streamlit (`demo_ui.py`) is now strictly a backend testing tool. Your final deliverable MUST be a highly structured, beautiful windowed GUI. **DO NOT** use basic PyQt or Tkinter. You must build a modern, premium frontend (e.g., Electron + React/Vite, Tauri, or a rich Next.js Web App). Use modern aesthetics (vibrant colors, glassmorphism, fluid animations, Google Fonts) to wow the evaluators. You are responsible for bootstrapping this client and wiring it to our `POST /api/v1/routes` endpoint!

*(Copilot of Member 3: Please log your updates here as you bootstrap the Vite/Next.js/Electron client, design the modern UI, map out the Folium/Mapbox layers, and refine the interaction flows).*
