# भू-आधार 3D • National 3D Volumetric Cadastre & Colony Digital Twin Platform

[![Vercel Deployment](https://img.shields.io/badge/Frontend-Vercel-black?style=flat&logo=vercel)](https://vercel.com)
[![Render Deployment](https://img.shields.io/badge/Backend-Render-46E3B7?style=flat&logo=render)](https://render.com)
[![Standard](https://img.shields.io/badge/Standard-ISO%2019152%20LADM%203D-10B981)](#)
[![Theme](https://img.shields.io/badge/Palette-Forest%20Emerald%20%26%20Heritage%20Gold-D97706)](#)

A production-ready **3D Bhu-Aadhaar (ULPIN) Volumetric Cadastre and Colony Digital Twin Platform** built for the **Survey of India (SoI)** and **Department of Land Resources (DoLR), Ministry of Rural Development, Government of India**.

---

## 🌟 Key Features

1. **Strictly Zero Blue Palette**:
   - Designed with an authoritative, elegant Indian Land Registry aesthetic: **Deep Slate Obsidian (`#080D0B`)**, **Indian Forest Emerald (`#10B981`)**, **Heritage Amber/Gold (`#F59E0B`, `#D97706`)**, and **Terracotta Sandstone (`#E07A5F`)**.
   - Zero blue/navy tones for superior contrast, warmth, and ease of understanding.

2. **Interactive Hover Tooltips on Acronyms & Legal Terms**:
   - Every abbreviation and technical land revenue term in Hindi/Urdu/English features an interactive dotted underline with an explanatory hover popup:
     - **ULPIN** (Unique Land Parcel Identification Number / 14-digit Bhu-Aadhaar)
     - **Khasra** (Cadastral survey plot document & shajra number)
     - **Khatauni / Jamabandi** (Record of Rights / Title Register)
     - **SVAMITVA Scheme** (Drone-based village inhabited area 3D mapping)
     - **FAR / FSI** (Floor Area Ratio / Floor Space Index limits)
     - **Setback** (Statutory open space buffers)
     - **Nazul Land & Gaon Sabha Land** (Government & Community lands)
     - **Mutation (Dakhil-Kharij)**, **Circle Rate**, **Encumbrance**, **LADM (ISO 19152)**, and more.
   - Includes a searchable **Quick Glossary Dictionary Drawer**.

3. **Colony Township View (Not a Single Building)**:
   - Full 3D model of **Aryavarta Enclave - Sector 12**:
     - **Road Corridors**: 24m Main Sector Arterial Road with centerlines, sidewalks, and 12m/9m internal colony avenues.
     - **Government Properties** (Tagged with Ashoka Pillar badges):
       - Gram Panchayat Bhawan & CSC Digital Seva Kendra (Khasra #GOVT/101)
       - Govt Primary Health Centre (PHC) & Ayush Clinic (Khasra #GOVT/102)
       - PM SHRI Govt Model Senior Secondary School (Khasra #GOVT/103)
       - Community Park & Amrit Sarovar Water Body (Khasra #GOVT/104)
       - Power Grid 33kV Substation (Khasra #GOVT/105)
     - **Residential Strata Societies**: *Ganga Heights* (8 floors with clickable flats & penthouse) and *Yamuna Residency*.
     - **Plotted Independent Houses (Kothis)**: Khasra #201 to #206 with boundary walls, garden setbacks, and verified owner records.
     - **Commercial Complex**: *Vyapar Kendra Plaza* (retail shops, bank ATM, offices).
     - **Subterranean Infrastructure**: Delhi Metro Pink Line underground transit tunnel (-18m) and underground utilities (Water, Sewer, 11kV Power, BharatNet Fiber) with **Underground X-Ray Mode**!

4. **Officer 2D Upload & 3D Extrusion Portal**:
   - Revenue officers can upload 2D cadastre files (`.geojson`, `.kml`, `.csv`) or enter coordinates.
   - Specify State, Tehsil, Khasra No., Khata No., Land classification, Owner details, Floor count, Plinth height, Basement levels, and Setback rules.
   - Click **"Process & Extrude to 3D Cadastre"**:
     - Automatically generates 14-digit ULPIN from centroid.
     - Checks FAR/FSI compliance.
     - Extrudes into 3D volumetric model directly into the Colony View.
     - Automatically animates the camera to fly to the newly constructed parcel!
     - Generates an official printable **3D Cadastral Property Card / Bhu-Aadhaar Certificate** with QR verification code.

5. **Resilient Dual-Mode Architecture (Zero Errors)**:
   - Can run connected to a live PostgreSQL/PostGIS database, OR seamlessly fall back to the built-in high-performance in-memory Indian cadastral dataset without 500 errors.

---

## 🚀 Deployment Guide

### Option 1: Deploy Frontend on Vercel

The frontend is ready for instant 1-click deployment on **Vercel** with the included `vercel.json`:

1. Push this repository to GitHub / GitLab / Bitbucket.
2. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New Project"**.
3. Import your repository:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: None (leave empty)
   - **Output Directory**: `./` (leave default)
4. Click **Deploy**.
5. Once deployed, open your Vercel URL (e.g. `https://your-project.vercel.app`).
6. Click the **"⚙️ API Config"** button in the top navigation bar and enter your Render backend URL (or leave blank to use the built-in offline engine).

---

### Option 2: Deploy Backend on Render

The backend is built with FastAPI and includes both a `render.yaml` blueprint and a `Dockerfile`.

#### Method A: Using Render Blueprint (Recommended)
1. In your [Render Dashboard](https://dashboard.render.com), click **"New +"** -> **"Blueprint"**.
2. Connect your GitHub repository.
3. Render will automatically detect `render.yaml` and create the `bhu-aadhaar-3d-backend` Web Service.
4. Click **Apply**.

#### Method B: Manual Web Service Setup
1. In Render Dashboard, click **"New +"** -> **"Web Service"**.
2. Connect your repository.
3. Configure the settings:
   - **Name**: `bhu-aadhaar-3d-backend`
   - **Region**: Singapore or Frankfurt
   - **Language**: Python 3
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
4. (Optional) Add environment variables for PostgreSQL:
   - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   *(Note: If no database is configured, the backend automatically uses the built-in high-performance Indian colony dataset with 100% feature parity!)*
5. Click **Deploy Web Service**.
6. Copy your Render service URL (e.g. `https://bhu-aadhaar-3d-backend.onrender.com`) and paste it into the frontend's API Config modal.

---

## 💻 Local Development

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run the Full Stack Service
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Open in Browser
Visit **`http://localhost:8000`** in your web browser. Both the interactive frontend portal and all REST API endpoints are served simultaneously.

---

## 📡 Core API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the interactive 3D Bhu-Aadhaar frontend portal |
| `GET` | `/health` | Service health check for Render & uptime monitors |
| `GET` | `/api/cadastre/3d-layers` | Retrieves all 3D colony layers (Govt, Strata, Roads, Utilities, Metro) |
| `GET` | `/api/cadastre/stats` | Colony statistics (parcels, strata units, volume, circle rates) |
| `POST` | `/api/cadastre/officer-upload` | Officer 2D cadastre ingestion, ULPIN calculation, and 3D extrusion |
| `POST` | `/api/cadastre/generate-3d-ulpin` | Standardized 3D Bhu-Aadhaar ULPIN generator |
| `GET` | `/api/cadastre/parcel/{ulpin}` | Statutory Record of Rights (RoR) for a specific parcel |
| `POST` | `/api/ai/validate-topology` | 3D spatial buffer & setback encroachment audit |
| `GET` | `/api/cadastre/dem-profile` | Bare-earth DEM vs Digital Surface Model (DSM) transect |
| `GET` | `/api/cadastre/lidar-pointcloud` | Sample classified drone LiDAR point cloud points |

---

## 📜 Compliance & Standards
- **LADM (ISO 19152)**: International Land Administration Domain Model 3D volumetric rights, restrictions, and responsibilities (RRR).
- **DILRMP**: Digital India Land Records Modernization Programme.
- **SVAMITVA Scheme**: Ministry of Panchayati Raj & Survey of India.
