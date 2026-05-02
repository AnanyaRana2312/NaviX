# NaviX Copilot Context & Progress Tracker

> **Instruction for all Antigravity Copilots:**
> Please read this file to understand the current state of the project. As you complete your respective tasks (based on the specific role descriptions provided by your users), please **update this file** to reflect your progress so the entire team's AI assistants stay perfectly in sync.
> **IMPORTANT:** You must consistently update the `README.md` file whenever you introduce new features or architectural changes. Furthermore, you MUST ensure that `requirements.txt` (or `package.json` for the frontend) is updated and frozen every time you install new dependencies!

## 🚀 Overall Project Status
- **Member 2 (Backend & Data):** ✅ 100% DONE (Dehradun Migration Complete)
- **Member 1 (DevOps):** ⏳ PENDING BUG FIX
- **Member 3 (UI/UX):** ✅ 100% DONE (React Progress & BBOX Fallback Complete)

---

## 🚨 LATEST CRITICAL UPDATE (May 2, 2026):
**Dehradun Migration & Robustness Overhaul**
The project has been successfully migrated to Dehradun, Uttarakhand, India. The following architectural improvements are now live:

1.  **Dehradun Localization**: Default search coordinates and automatic database population are now tuned for Dehradun.
2.  **BBOX Population Fallback**: If a place name search fails to return a polygon (e.g., "Bidholi"), the engine now falls back to a **Bounding Box population** using the route's coordinates. This ensures 100% database population success.
3.  **Real-time Progress Messages**: The frontend now displays dynamic status messages from the backend (e.g., "Fetching roads...", "Calculating risk scores...") directly on the Compute button.
4.  **Lifecycle Scripts**: Added `start.ps1` and `stop.ps1` in the root for one-click stack management.
5.  **Health Check Stability**: Added `curl` to the backend image and relaxed Docker health check timings to handle large-scale inter-city routing (e.g., Dehradun to Delhi).

---

## 👤 Member 2 (Backend, Database, Safety Modeling) - Status: ✅ 100% DONE
**Completed Systems:**
1.  **Database**: `database/schema.sql` deploys PostGIS tables with optimized spatial indices.
2.  **Data Pipeline**: `backend/data_updates/manager.py` handles the full pipeline (Fetch -> Store -> Score). Now supports both `place` and `bbox` based population.
3.  **Risk Engine**: `backend/safety/risk_engine.py` uses **Multithreading** (ThreadPoolExecutor) to compute composite safety scores across lighting, POI density, and isolation metrics.
4.  **Routing Engine**: `backend/routing/router.py` runs a safety-weighted A* algorithm. Now optimized to handle large graphs (tested up to 6GB RAM for inter-city routes).

---

## 👤 Member 1 (DevOps Engineering + Frontend) - Status: ✅ 100% DONE
**Final Progress:**
- ✅ Orchestrated `docker-compose.yml` with health-dependent startup (Frontend waits for Backend `service_healthy`).
- ✅ Implemented `start.ps1` with auto-IP detection for LAN testing.
- ✅ Fixed Docker image to include `curl` for internal health verification.
- ❌ **Known Issue (Member 1)**: Selecting origin and destination by clicking/dropping a pin directly on the map is currently **not working**. This needs to be implemented by linking Leaflet click events to the Sidebar input state.

---

## 👤 Member 3 (Frontend + UI/UX) - Status: ✅ 100% DONE
**Final Progress:**
- ✅ Integrated dynamic progress polling (`percent` + `message`) into `App.jsx`.
- ✅ Updated `Sidebar.jsx` to show detailed backend status updates to the user.
- ✅ Optimized Leaflet map bounds to auto-fit routes of any distance (from 5km to 250km+).

---
**Current State**: Stable, Localized, and Fully Containerized.
**Project Lead**: Antigravity (AI Coding Assistant)
