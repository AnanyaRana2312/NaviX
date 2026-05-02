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

## 🚨 LATEST UPDATE FOR MEMBER 2:
> Hey Member 2, the frontend integration and Docker orchestration are fully complete! During integration, we noticed the routing engine (`ox.graph_from_place`) was crashing for locations outside of New York. We applied a hotfix in `router.py` to use a dynamic Bounding Box (`ox.graph_from_bbox`) with a scaling buffer to ensure global routing works without returning mock lines. Please review these changes and apply any further backend fixes if necessary!

---

## 👤 Member 2 (Backend, Database, Safety Modeling) - Status: ⏳ IN PROGRESS (Review Required)
*Member 2 initially completed the system, but must now review the BBox routing hotfix.*

**Completed Systems (Available for integration):**
1. **Database:** `database/schema.sql` deploys PostgreSQL + PostGIS tables (`roads`, `features`, `risk_scores`) with spatial indices.
2. **Data Pipeline:** `scripts/osm_fetcher.py` and `scripts/update_scores.py` reliably extract OpenStreetMap data, compute spatial safety metrics (lighting, POI density, isolation), and batch-commit risk scores via a multithreaded engine.
3. **Routing Engine:** `backend/routing/router.py` utilizes NetworkX to run a modified A* algorithm. **(Recently overhauled to use dynamic Bounding Boxes instead of fixed location strings to support global routing).**
4. **FastAPI API:** Exposed at `POST /api/v1/routes`, providing robust JSON responses containing full geometric paths and segment-level metadata.

---

## 👤 Member 1 (DevOps Engineering + Frontend) - Status: ✅ 100% DONE
*DevOps and Frontend orchestration is complete and working flawlessly.*

**Final Progress:**
- ✅ Created lean `requirements.backend.txt` to eliminate dependency bloat and fix Docker timeouts.
- ✅ Orchestrated `docker-compose.yml` to spin up `db`, `backend` (FastAPI), and `frontend` (Vite) seamlessly.
- ✅ Configured Vite proxy in `vite.config.js` to route `/api/v1` traffic internally to the backend container, entirely eliminating CORS issues.
- ✅ Updated `start.bat` to correctly run the Vite server instead of the deprecated Streamlit app.
- ✅ Overhauled `router.py` to use `ox.graph_from_bbox` dynamically based on input coordinates, eliminating straight-line mock route fallbacks.

---

## 👤 Member 3 (Frontend + UI/UX) - Status: ✅ 100% DONE
*UI/UX design is fully integrated and stunning.*

**Final Progress:**
- ✅ Bootstrapped Vite + React client (`/frontend`).
- ✅ Built beautiful glassmorphism `Sidebar.jsx` with dynamic route options (Safest, Balanced, Shortest).
- ✅ Integrated real backend data: replaced mock API with live Axios calls that map real `[lat, lon]` arrays to `react-leaflet` Polylines.
- ✅ Added custom turn-by-turn navigation algorithm in the frontend that calculates bearings to generate instructions.
- ✅ Improved `MapLayout.jsx` with Standard OpenStreetMap tiles, automatic bounds fitting, and interactive hover tooltips.
