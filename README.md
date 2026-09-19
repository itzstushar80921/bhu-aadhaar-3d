# Bhu-Aadhaar 3D (भू-आधार 3D)

A web-based 3D cadastral mapping and land administration platform tailored for Indian urban and peri-urban land records. The system converts traditional 2D land parcels (Khasra/Khatauni) into 3D volumetric spatial units compliant with ISO 19152 (LADM), calculates Undivided Share of Land (UDS) for multi-story apartments, detects vertical structural encroachments over public rights-of-way, and models underground utilities.

Built with a FastAPI spatial backend and a lightweight Three.js/WebGL frontend that runs in standard browsers without desktop GIS software.

---

## Background & Problem Statement

Most state land revenue systems in India (Bhulekh, Bhu-Naksha, Jharbhoomi) record properties purely on a 2D plane:
- **Vertical Strata Gap**: In high-rise apartments, flat buyers hold registered deeds for "air space" without volumetric boundary coordinates ($X, Y, Z$). This opens room for illegal additional floors, floor plan deviations, and duplicate sales.
- **Encroachment Blind Spots**: Upper-floor balcony extensions and cantilever structures frequently protrude into municipal road buffers without altering the 2D ground footprint, evading satellite and drone boundary detection.
- **Subterranean Conflicts**: Urban development work routinely causes utility damage or tunnel strikes because underground water, gas, electricity, and metro corridors are not mapped relative to ground datum.

This project implements volumetric parcel subdivision, generates standard 14-digit ULPIN identifiers down to individual flats, and exposes an officer-facing ingestion tool for AutoCAD DXF, GeoJSON, and KML files.

---

## Key Capabilities

- **Colony-Level Digital Twin**: Renders township layouts (roads, government plots with state emblem markings, plotted housing, strata societies, and subterranean utility tunnels).
- **2D-to-3D Cadastre Extrusion**: Officers can upload parcel boundary files or input coordinates with setback and FAR rules to generate 3D solids.
- **Strata & UDS Calculation**: Splits apartment envelopes into floor units and computes statutory Undivided Share of Land (UDS) based on carpet area.
- **Encroachment Collision Flagging**: Uses Separating Axis Theorem (SAT) bounding checks against municipal road Right-of-Way (RoW) buffers (demonstrated on Khasra #202).
- **Interactive Section Slicer**: Real-time vertical clipping plane to inspect interior floor plans, structural shafts, and underground layers.
- **Statutory 3D Property Card**: Generates printable verification certificates with dynamic QR codes and SHA-256 masked identity tokens.
- **Contextual Tooltips & Multilingual Support**: Hover definitions for Indian revenue terms (*Khasra*, *Jamabandi*, *Nazul*, *FAR*, *ULPIN*) and UI localization into Hindi, Marathi, Gujarati, Kannada, Tamil, and English.
- **High-Contrast Dark Theme**: Styled with a dark slate/emerald/amber palette (`#080D0B`, `#10B981`, `#F59E0B`) avoiding blue tones to ensure visual contrast on municipal projection displays.

---

## Technical Architecture

```
Client (Browser)
├── WebGL / Three.js r128 (Scene Graph, Local Clipping Planes, Raycasting)
├── Vanilla ES6+ UI Components & Canvas 2D
└── Client-side DXF / GeoJSON Parser & QR Generator

REST API Backend (FastAPI / Python 3.10+)
├── Spatial Projection & Geometry: Shapely, PyProj, Math
├── CRS Engine: EPSG:4326 (WGS84) -> EPSG:32643 (UTM 43N) / EGM2008 MSL Datum
├── Cadastral File Parser: Handles GeoJSON, AutoCAD DXF, and KML
└── Identity Masking: SHA-256 e-KYC token generation
```

### Coordinate Reference Systems (CRS)
- **Horizontal**: Input coordinates in WGS84 (`EPSG:4326`) are reprojected to UTM Zone 43N (`EPSG:32643`) or Web Mercator (`EPSG:3857`) for metric calculations.
- **Vertical**: Elevation values ($Z$) are referenced to the Survey of India GTS Benchmark datum using the EGM2008 Geoid model for orthometric height above Mean Sea Level.

### ULPIN Syntax Specification
Follows the Survey of India / NIC 14-digit alphanumeric standard for base parcels, appending strata tokens for vertical subdivisions:

```
Root Parcel (Ground):          IN2877214100A1
Strata Unit (4th Floor Flat):  IN2877214100A1/L04/U401
Basement Parking:              IN2877214100A1/B01/PARK
Ground Floor Commercial:       IN2877214100A1/L01/RET02
```

---

## Repository Structure

```
.
├── main.py                     # FastAPI application and spatial endpoints
├── index.html                  # Three.js 3D cadastre frontend application
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment configuration
├── vercel.json                 # Vercel deployment configuration
├── Dockerfile                  # Container definition for backend service
├── setup_database.py           # Optional PostgreSQL/PostGIS schema initializer
├── generate_documentation.py   # Script to generate .docx and .pptx reports
│
├── Sample Cadastral Files (for testing upload):
│   ├── sample_cadastre_plot_342_1.geojson
│   ├── sample_township_plot.dxf
│   └── sample_land_parcel.kml
│
└── Generated Documentation:
    ├── Bhu_Aadhaar_3D_Comprehensive_Technical_Report.docx
    └── Bhu_Aadhaar_3D_Judges_Presentation.pptx
```

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Modern web browser with WebGL enabled (Chrome, Edge, Firefox, Safari)

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/3d_mapping.git
   cd 3d_mapping
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Open in browser**:
   Navigate to `http://127.0.0.1:8000`. The server hosts both the API endpoints and the static 3D frontend.

---

## Testing File Uploads

You can test the 2D-to-3D cadastre conversion using the sample files included in the root directory:

1. Open the web interface.
2. In the left panel, locate the **Officer Cadastre Portal**.
3. Choose either:
   - `sample_cadastre_plot_342_1.geojson`: Contains 4-vertex plot boundaries with Khasra, Jamabandi, and land use metadata.
   - `sample_township_plot.dxf`: AutoCAD ASCII DXF format containing polyline boundary entities.
   - `sample_land_parcel.kml`: Keyhole Markup Language boundary polygon.
4. Set the desired number of floors, plinth height, and setback values.
5. Click **Process & Extrude to 3D Cadastre**. The system calculates the centroid, generates the 14-digit ULPIN, displays the 3D volume in the colony view, and generates a downloadable 3D Property Card.

---

## API Reference

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Serves the single-page 3D application |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/api/cadastre/3d-layers` | Retrieves all 3D colony layer meshes (parcels, roads, utilities, metro) |
| `GET` | `/api/cadastre/stats` | Summary statistics (parcel counts, strata units, volume, circle rates) |
| `POST` | `/api/cadastre/parse-file` | Parses uploaded GeoJSON, DXF, or KML files |
| `POST` | `/api/cadastre/officer-upload` | Extrudes 2D polygon into 3D parcel and assigns ULPIN |
| `POST` | `/api/cadastre/generate-3d-ulpin` | Computes 14-digit NIC-compliant ULPIN from coordinates |
| `GET` | `/api/cadastre/parcel/{ulpin}` | Returns Record of Rights (RoR) data for a parcel |
| `POST` | `/api/ai/validate-topology` | Performs 3D setback and encroachment collision verification |

---

## Deployment

### Frontend (Vercel)
The root folder is configured with `vercel.json` for static deployment.
1. Connect this repository to Vercel.
2. Leave root directory as `./` and framework as `Other`.
3. Deploy. If connecting to a remote backend, set the backend URL in the web UI via the **API Config** modal.

### Backend (Render)
The repository includes a `render.yaml` blueprint.
1. In Render, select **New > Blueprint** and point to your repository.
2. Render detects `render.yaml` and deploys the FastAPI service.
3. Alternatively, deploy as a **Web Service** using Docker via the included `Dockerfile`.

*Note: The backend operates with an in-memory spatial database by default. To connect a live database, provide standard PostgreSQL/PostGIS credentials via environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).*

---

## Standards & Specifications

- **ISO 19152 (LADM)**: Geographic information — Land Administration Domain Model (Part 1: Generic conceptual model, Part 2: Land registration).
- **Survey of India / DoLR Guidelines**: Standard Operating Procedure for Unique Land Parcel Identification Number (ULPIN / Bhu-Aadhaar).
- **RERA (Real Estate Regulatory Authority)**: Standardized definition of carpet area and proportional undivided share of land.
- **Digital Personal Data Protection Act, 2023**: Zero-knowledge tokenization of citizen identifiers (Aadhaar/PAN) in public cadastral systems.
