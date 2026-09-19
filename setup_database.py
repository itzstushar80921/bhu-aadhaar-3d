"""
Database Setup & Seed Script for 3D Bhu-Aadhaar (ULPIN) Generation & Vertical Property Mapping System
Government of India • Department of Land Resources (DoLR), MoRD • Survey of India (SoI)
PostgreSQL 18 + PostGIS 3.6
Database: bhu_aadhaar_3d
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import random

DB_CONFIG = {
    "dbname": "bhu_aadhaar_3d",
    "user": "postgres",
    "password": "Tushar@123",
    "host": "localhost",
    "port": "5432"
}

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    print("[1/5] Enabling PostGIS extensions for Bhu-Aadhaar 3D...")
    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")

    print("[2/5] Creating Cadastral Schemas (DILRMP / Survey of India Standard)...")
    
    cur.execute("""
        DROP TABLE IF EXISTS cadastral_conflicts CASCADE;
        DROP TABLE IF EXISTS underground_utilities CASCADE;
        DROP TABLE IF EXISTS cadastral_volumetric_parcels CASCADE;
        DROP TABLE IF EXISTS cadastral_surface_parcels CASCADE;
        DROP TABLE IF EXISTS lidar_samples CASCADE;

        -- 1. Surface Cadastral Parcels (Khasra / Plot Boundaries)
        CREATE TABLE cadastral_surface_parcels (
            lot_id VARCHAR(50) PRIMARY KEY,       -- e.g. 'DL-ND-00101'
            ulpin_2d VARCHAR(50) NOT NULL UNIQUE, -- 14-digit Bhu-Aadhaar
            khasra_no VARCHAR(50),                -- Khasra / Survey / CTS No.
            land_use VARCHAR(80) NOT NULL,
            zoning_code VARCHAR(30),
            area_sqm NUMERIC(10,2),
            ground_elevation_msl NUMERIC(8,2) DEFAULT 216.0, -- New Delhi MSL ~216m
            address VARCHAR(250),
            geom_surface GEOMETRY(Polygon, 4326)
        );

        -- 2. 3D Volumetric Bhu-Aadhaar Parcels (Strata, Subterranean, Air-Rights)
        CREATE TABLE cadastral_volumetric_parcels (
            ulpin_3d_id VARCHAR(80) PRIMARY KEY,  -- 3D Bhu-Aadhaar (ULPIN)
            parent_lot_id VARCHAR(50) REFERENCES cadastral_surface_parcels(lot_id) ON DELETE CASCADE,
            stratum_type VARCHAR(30) NOT NULL,    -- 'SURFACE', 'STRATA', 'SUBTERRANEAN', 'AIR_RIGHTS'
            building_name VARCHAR(120),
            floor_level INT NOT NULL,              -- -2, -1, 1, 2, 3...
            floor_code VARCHAR(10),                -- 'B02', 'B01', 'L01', 'L04', 'RF01'
            unit_number VARCHAR(40),               -- 'FLAT-402', 'OFF-201', 'PARK-B2-01'
            min_z NUMERIC(8,2) NOT NULL,           -- Base height in meters MSL (Survey of India GTS Datum)
            max_z NUMERIC(8,2) NOT NULL,           -- Top height in meters MSL
            floor_area_sqm NUMERIC(10,2),          -- RERA Carpet Area
            volume_cum NUMERIC(12,2),              -- 3D Volumetric Extent
            strata_share_value INT DEFAULT 100,    -- Undivided Share of Land (UDS) / 1000
            owner_name VARCHAR(150) NOT NULL,
            owner_id VARCHAR(50),                  -- Aadhaar Hash / PAN / CIN
            legal_deed_no VARCHAR(60),             -- Sub-Registrar Office Deed Registration No.
            use_case VARCHAR(60),                  -- 'Residential', 'Commercial', 'Infrastructure', 'Utility'
            encumbrance_status VARCHAR(60) DEFAULT 'Clear Title / Non-Encumbered',
            tax_assessment_annual NUMERIC(10,2) DEFAULT 4500.0, -- MCD Unit Area Property Tax
            geom_3d GEOMETRY(PolygonZ, 4326)
        );

        -- 3. Subsurface Utility Networks (Power, Gas, Water, Metro, Telecom)
        CREATE TABLE underground_utilities (
            utility_id VARCHAR(50) PRIMARY KEY,
            utility_type VARCHAR(50) NOT NULL,      -- 'METRO_TUNNEL', 'WATER_TRUNK_MAIN', 'HIGH_VOLTAGE_POWER', 'CITY_GAS_PIPELINE', 'OPTICAL_FIBER'
            operator_name VARCHAR(120),             -- 'Delhi Metro Rail Corporation (DMRC)', 'Delhi Jal Board', 'GAIL India', 'Tata Power / BSES'
            diameter_or_width_m NUMERIC(6,2),
            depth_min_z NUMERIC(8,2),               -- Depth below ground MSL
            depth_max_z NUMERIC(8,2),
            service_status VARCHAR(40) DEFAULT 'Operational / Live',
            geom_3d GEOMETRY(LineStringZ, 4326)
        );

        -- 4. 3D LiDAR Point Cloud Samples
        CREATE TABLE lidar_samples (
            point_id SERIAL PRIMARY KEY,
            longitude DOUBLE PRECISION,
            latitude DOUBLE PRECISION,
            elevation_z DOUBLE PRECISION,
            intensity INT,
            classification VARCHAR(30)
        );

        -- 5. 3D Spatial Topology Conflicts (Encroachments & Buffer Violations)
        CREATE TABLE cadastral_conflicts (
            conflict_id VARCHAR(50) PRIMARY KEY,
            conflict_type VARCHAR(50),              -- 'VOLUMETRIC_OVERLAP', 'METRO_BUFFER_BREACH', 'AIR_RIGHTS_EXCESS'
            severity VARCHAR(20),                   -- 'CRITICAL', 'WARNING'
            parcel_a_ulpin VARCHAR(80),
            parcel_b_ulpin VARCHAR(80),
            description TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            conflict_volume_geom GEOMETRY(PolygonZ, 4326)
        );
    """)

    print("[3/5] Seeding Indian Urban Cadastral Surface Lots (Khasra Plots)...")

    # Indian Reference Center: Barakhamba / Connaught Place Smart Cadastre Zone, New Delhi
    # Longitude: 77.2167, Latitude: 28.6328 (or normalized grid relative to survey parcel)
    # Surface Khasra Lots:
    # Lot 1: Khasra 101/1 - Indraprastha Smart Heights & Commercial Hub
    # Lot 2: Khasra 101/2 - Digital India Tech Tower & Cyber Park
    # Lot 3: Khasra 101/3 - DMRC Metro Transit Corridor & Road Reserve

    lots = [
        (
            "DL-ND-00101", "IN-DL-0701-SRV-10101", "Khasra 101/1", "High-Density Mixed Commercial & Residential", "C-HDR-RERA",
            1600.0, 0.0, "Plot 10, Barakhamba Commercial Corridor, Connaught Place, New Delhi 110001",
            "POLYGON((77.2160 28.6325, 77.2166 28.6325, 77.2166 28.6331, 77.2160 28.6331, 77.2160 28.6325))"
        ),
        (
            "DL-ND-00102", "IN-DL-0701-SRV-10102", "Khasra 101/2", "IT / ITES Commercial Tech Park", "COMM-IT-5.0",
            1200.0, 0.0, "Plot 12, Digital India Boulevard, New Delhi 110001",
            "POLYGON((77.2168 28.6325, 77.2173 28.6325, 77.2173 28.6331, 77.2168 28.6331, 77.2168 28.6325))"
        ),
        (
            "DL-ND-00103", "IN-DL-0701-SRV-10103", "Khasra 101/3", "DMRC Metro Transit Reserve & Public Right-of-Way", "PUB-TRANS-ROW",
            2400.0, 0.0, "Metropolitan Transit Reserve Road, New Delhi 110001",
            "POLYGON((77.2158 28.6320, 77.2175 28.6320, 77.2175 28.6324, 77.2158 28.6324, 77.2158 28.6320))"
        )
    ]

    for lot in lots:
        cur.execute("""
            INSERT INTO cadastral_surface_parcels 
            (lot_id, ulpin_2d, khasra_no, land_use, zoning_code, area_sqm, ground_elevation_msl, address, geom_surface)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326));
        """, lot)

    print("[4/5] Seeding 3D Bhu-Aadhaar Volumetric Parcels (Multi-Storey RERA Flats, Basements, DMRC Tunnel)...")

    # Building 1: Indraprastha Heights (inside Khasra 101/1)
    # Slicing from Subterranean Basement 2 to Level 5 Penthouse
    parcels_3d = [
        # Subterranean Basement 2: Resident Vehicle Parking & Transformer Substation
        (
            "IN-DL-0701-SUB-B02-PRK01", "DL-ND-00101", "SUBTERRANEAN", "Indraprastha Heights", -2, "B02", "PARK-B2-01",
            -8.0, -4.0, 480.0, 1920.0, 120, "Indraprastha RWA Apartment Association", "PAN-AAATI9012K", "DEL-SR-2026-B201",
            "Underground Infrastructure", "Clear Title", 6200.0,
            "POLYGON Z ((77.21615 28.63265 -8.0, 77.21645 28.63265 -8.0, 77.21645 28.63295 -8.0, 77.21615 28.63295 -8.0, 77.21615 28.63265 -8.0))"
        ),
        # Subterranean Basement 1: Commercial Metro Retail Concourse
        (
            "IN-DL-0701-SUB-B01-RET01", "DL-ND-00101", "SUBTERRANEAN", "Indraprastha Heights", -1, "B01", "RETAIL-B1-01",
            -4.0, 0.0, 480.0, 1920.0, 180, "Bharti Urban Retail Holdings Ltd", "CIN-L74899DL2000PLC1", "DEL-SR-2026-B101",
            "Commercial", "Clear Title", 18500.0,
            "POLYGON Z ((77.21615 28.63265 -4.0, 77.21645 28.63265 -4.0, 77.21645 28.63295 -4.0, 77.21615 28.63295 -4.0, 77.21615 28.63265 -4.0))"
        ),
        # Ground Floor (Level 1): Grand Commercial Banking Hall & Retail Lobby
        (
            "IN-DL-0701-STR-L01-LOBBY", "DL-ND-00101", "STRATA", "Indraprastha Heights", 1, "L01", "COMM-L1-LOBBY",
            0.0, 4.5, 480.0, 2160.0, 200, "State Bank of India (SBI Commercial Branch)", "CIN-SBI-CENTRAL-01", "DEL-SR-2026-L101",
            "Commercial", "Clear Title", 24000.0,
            "POLYGON Z ((77.21615 28.63265 0.0, 77.21645 28.63265 0.0, 77.21645 28.63295 0.0, 77.21615 28.63295 0.0, 77.21615 28.63265 0.0))"
        ),
        # Level 2: Coworking & Start-up Hub
        (
            "IN-DL-0701-STR-L02-OFF01", "DL-ND-00101", "STRATA", "Indraprastha Heights", 2, "L02", "OFF-L2-01",
            4.5, 8.5, 480.0, 1920.0, 240, "Startup India Innovation Center", "PAN-DEL-GOV-9912", "DEL-SR-2026-L201",
            "Commercial", "Clear Title", 28000.0,
            "POLYGON Z ((77.21615 28.63265 4.5, 77.21645 28.63265 4.5, 77.21645 28.63295 4.5, 77.21615 28.63295 4.5, 77.21615 28.63265 4.5))"
        ),
        # Level 3 Flat 301 (West Wing): RERA Carpet Area 220 sqm
        (
            "IN-DL-0701-STR-L03-U301", "DL-ND-00101", "STRATA", "Indraprastha Heights", 3, "L03", "FLAT-301",
            8.5, 12.0, 220.0, 770.0, 110, "Rajesh Sharma & Anita Sharma", "AADHAAR-XXXX-XXXX-4812", "RERA-DEL-PRJ-2026-301",
            "Residential", "Mortgage Registered (HDFC Bank)", 12400.0,
            "POLYGON Z ((77.21615 28.63265 8.5, 77.21630 28.63265 8.5, 77.21630 28.63295 8.5, 77.21615 28.63295 8.5, 77.21615 28.63265 8.5))"
        ),
        # Level 3 Flat 302 (East Wing): RERA Carpet Area 220 sqm
        (
            "IN-DL-0701-STR-L03-U302", "DL-ND-00101", "STRATA", "Indraprastha Heights", 3, "L03", "FLAT-302",
            8.5, 12.0, 220.0, 770.0, 110, "Vikram Malhotra", "AADHAAR-XXXX-XXXX-8921", "RERA-DEL-PRJ-2026-302",
            "Residential", "Clear Title / Non-Encumbered", 12400.0,
            "POLYGON Z ((77.21630 28.63265 8.5, 77.21645 28.63265 8.5, 77.21645 28.63295 8.5, 77.21630 28.63295 8.5, 77.21630 28.63265 8.5))"
        ),
        # Level 4 Flat 401 (West Wing)
        (
            "IN-DL-0701-STR-L04-U401", "DL-ND-00101", "STRATA", "Indraprastha Heights", 4, "L04", "FLAT-401",
            12.0, 15.5, 220.0, 770.0, 110, "Sunita Deshmukh", "AADHAAR-XXXX-XXXX-3341", "RERA-DEL-PRJ-2026-401",
            "Residential", "Clear Title / Non-Encumbered", 13200.0,
            "POLYGON Z ((77.21615 28.63265 12.0, 77.21630 28.63265 12.0, 77.21630 28.63295 12.0, 77.21615 28.63295 12.0, 77.21615 28.63265 12.0))"
        ),
        # Level 4 Flat 402 (East Wing)
        (
            "IN-DL-0701-STR-L04-U402", "DL-ND-00101", "STRATA", "Indraprastha Heights", 4, "L04", "FLAT-402",
            12.0, 15.5, 220.0, 110, "Aakash Patel", "AADHAAR-XXXX-XXXX-7729", "RERA-DEL-PRJ-2026-402",
            "Residential", "Clear Title / Non-Encumbered", 13200.0,
            "POLYGON Z ((77.21630 28.63265 12.0, 77.21645 28.63265 12.0, 77.21645 28.63295 12.0, 77.21630 28.63295 12.0, 77.21630 28.63265 12.0))"
        ),
        # Level 5 Luxury Penthouse & Sky Garden
        (
            "IN-DL-0701-STR-L05-PENT", "DL-ND-00101", "STRATA", "Indraprastha Heights", 5, "L05", "PENTHOUSE-01",
            15.5, 20.0, 440.0, 1980.0, 320, "Karan Johar Oberoi", "AADHAAR-XXXX-XXXX-1102", "RERA-DEL-PRJ-2026-501",
            "Residential", "Clear Title / Non-Encumbered", 36000.0,
            "POLYGON Z ((77.21615 28.63265 15.5, 77.21645 28.63265 15.5, 77.21645 28.63295 15.5, 77.21615 28.63295 15.5, 77.21615 28.63265 15.5))"
        ),
        # Building 2: Digital India Cyber Tower (Plot 101/2)
        (
            "IN-DL-0702-STR-L01-TECH", "DL-ND-00102", "STRATA", "Digital India Tower", 1, "L01", "NIC-DATA-01",
            0.0, 6.0, 360.0, 2160.0, 200, "National Informatics Centre (NIC) / MeitY", "GOI-NIC-CENTRAL", "GOI-ALLOC-2026-01",
            "Commercial", "Government Sovereign Property", 0.0,
            "POLYGON Z ((77.21690 28.63265 0.0, 77.21720 28.63265 0.0, 77.21720 28.63295 0.0, 77.21690 28.63295 0.0, 77.21690 28.63265 0.0))"
        ),
        (
            "IN-DL-0702-STR-L02-OFF", "DL-ND-00102", "STRATA", "Digital India Tower", 2, "L02", "TCS-DEV-02",
            6.0, 12.0, 360.0, 2160.0, 220, "Tata Consultancy Services Ltd", "CIN-L22210MH1995PLC0", "DEL-SR-2026-T201",
            "Commercial", "Clear Title / Leasehold 99yr", 32000.0,
            "POLYGON Z ((77.21690 28.63265 6.0, 77.21720 28.63265 6.0, 77.21720 28.63295 6.0, 77.21690 28.63295 6.0, 77.21690 28.63265 6.0))"
        ),
        # Air-Rights Parcel: Elevated Pedestrian Skywalk spanning over Metropolitan Road
        (
            "IN-DL-0703-AIR-SKYWALK-01", "DL-ND-00103", "AIR_RIGHTS", "Barakhamba Pedestrian Skywalk", 3, "E03", "SKYWALK-01",
            14.0, 17.5, 180.0, 630.0, 80, "Delhi Development Authority (DDA) / CPWD", "GOI-DDA-DELHI", "DDA-AIR-2026-001",
            "Infrastructure", "Public Air-Rights Grant", 0.0,
            "POLYGON Z ((77.21645 28.63275 14.0, 77.21690 28.63275 14.0, 77.21690 28.63285 14.0, 77.21645 28.63285 14.0, 77.21645 28.63275 14.0))"
        ),
        # Subterranean Volumetric Corridor: Delhi Metro Rail Corporation (DMRC) Underground Tube
        (
            "IN-DL-0703-SUB-DMRC-TUNNEL", "DL-ND-00103", "SUBTERRANEAN", "DMRC Airport Express Subway Tube", -3, "B03", "DMRC-TUBE-01",
            -24.0, -18.0, 1200.0, 7200.0, 500, "Delhi Metro Rail Corporation Ltd (DMRC)", "CIN-U60221DL1995GOI068150", "DMRC-STATUTORY-SUB-01",
            "Infrastructure", "Statutory Subterranean Reserve", 0.0,
            "POLYGON Z ((77.21580 28.63210 -24.0, 77.21750 28.63210 -24.0, 77.21750 28.63225 -24.0, 77.21580 28.63225 -24.0, 77.21580 28.63210 -24.0))"
        )
    ]

    for p in parcels_3d:
        cur.execute("""
            INSERT INTO cadastral_volumetric_parcels 
            (ulpin_3d_id, parent_lot_id, stratum_type, building_name, floor_level, floor_code, unit_number,
             min_z, max_z, floor_area_sqm, volume_cum, strata_share_value, owner_name, owner_id, legal_deed_no,
             use_case, encumbrance_status, tax_assessment_annual, geom_3d)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326));
        """, p)

    # Sync into legacy volumetric_cadastre table for backwards compatibility
    cur.execute("""
        ALTER TABLE volumetric_cadastre ALTER COLUMN ulpin_3d_id TYPE VARCHAR(100);
        ALTER TABLE volumetric_cadastre ALTER COLUMN use_case TYPE VARCHAR(100);
        ALTER TABLE volumetric_cadastre ALTER COLUMN owner_name TYPE VARCHAR(150);
        DELETE FROM volumetric_cadastre;
        INSERT INTO volumetric_cadastre (ulpin_3d_id, owner_name, use_case, floor_level, min_z, max_z, geom_3d)
        SELECT ulpin_3d_id, owner_name, use_case, floor_level, min_z, max_z, geom_3d
        FROM cadastral_volumetric_parcels;
    """)

    print("[5/5] Seeding Underground Infrastructure Networks (Power, Gas, Water, Telecom)...")
    utilities = [
        (
            "UTIL-BSES-66KV-01", "HIGH_VOLTAGE_POWER", "BSES Yamuna Power Ltd / Tata Power-DDL", 1.2, -6.5, -5.0,
            "LINESTRING Z (77.2159 28.63215 -6.0, 77.2167 28.63255 -5.5, 77.2174 28.63265 -5.0)"
        ),
        (
            "UTIL-DJB-H2O-1200", "WATER_TRUNK_MAIN", "Delhi Jal Board (DJB 1200mm Master Main)", 1.5, -4.5, -3.0,
            "LINESTRING Z (77.2159 28.63220 -4.0, 77.2167 28.63260 -3.5, 77.2174 28.63270 -3.0)"
        ),
        (
            "UTIL-GAIL-GAS-01", "CITY_GAS_PIPELINE", "GAIL (India) Ltd City Gas Grid", 0.9, -3.5, -2.5,
            "LINESTRING Z (77.2159 28.63225 -3.0, 77.2166 28.63265 -2.8, 77.2174 28.63275 -2.5)"
        ),
        (
            "UTIL-JIO-FIBER-01", "OPTICAL_FIBER", "BharatNet / Jio 5G Optical Fiber Conduit", 0.8, -2.5, -1.8,
            "LINESTRING Z (77.2159 28.63230 -2.2, 77.2166 28.63270 -2.0, 77.2174 28.63280 -1.8)"
        ),
        (
            "UTIL-DJB-SEW-02", "STORM_SEWER", "Delhi Jal Board Deep Drainage Trunk", 2.8, -14.0, -11.0,
            "LINESTRING Z (77.2158 28.63205 -12.5, 77.2168 28.63245 -12.0, 77.2175 28.63255 -11.5)"
        )
    ]

    for u in utilities:
        cur.execute("""
            INSERT INTO underground_utilities 
            (utility_id, utility_type, operator_name, diameter_or_width_m, depth_min_z, depth_max_z, geom_3d)
            VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326));
        """, u)

    print("Generating simulated SVAMITVA / Survey of India 3D LiDAR point cloud...")
    lidar_data = []
    random.seed(42)
    for _ in range(120):
        lng = 77.2159 + random.random() * 0.0016
        lat = 77.2160 + random.random() * 0.0010
        z = random.uniform(-0.2, 0.4)
        lidar_data.append((lng, lat, z, random.randint(80, 140), "Ground"))
    for _ in range(250):
        lng = 77.21615 + random.random() * 0.00030
        lat = 28.63265 + random.random() * 0.00030
        z = random.uniform(0.5, 20.2)
        lidar_data.append((lng, lat, z, random.randint(150, 255), "Building"))
    for _ in range(180):
        lng = 77.21690 + random.random() * 0.00030
        lat = 28.63265 + random.random() * 0.00030
        z = random.uniform(0.5, 12.5)
        lidar_data.append((lng, lat, z, random.randint(150, 255), "Building"))
    for _ in range(80):
        lng = 77.2159 + random.random() * 0.0015
        lat = 28.63215 + random.random() * 0.00010
        z = random.uniform(-23.5, -18.5)
        lidar_data.append((lng, lat, z, random.randint(40, 100), "Underground"))

    for pt in lidar_data:
        cur.execute("""
            INSERT INTO lidar_samples (longitude, latitude, elevation_z, intensity, classification)
            VALUES (%s, %s, %s, %s, %s);
        """, pt)

    # 3D Topology Clash in Indian Context:
    # Basement foundation pile of Indraprastha Heights encroaching into the 20m statutory safety buffer
    # of the Delhi Metro Rail Corporation (DMRC) underground tunnel!
    cur.execute("""
        INSERT INTO cadastral_conflicts 
        (conflict_id, conflict_type, severity, parcel_a_ulpin, parcel_b_ulpin, description, conflict_volume_geom)
        VALUES (
            'CONF-IN-2026-001',
            'METRO_BUFFER_BREACH',
            'CRITICAL',
            'IN-DL-0701-SUB-B02-PRK01',
            'IN-DL-0703-SUB-DMRC-TUNNEL',
            'Basement foundation pile encroaches 1.8m into the statutory 20m safety buffer of Delhi Metro Rail Corporation (DMRC) Airport Express underground tunnel.',
            ST_GeomFromText('POLYGON Z ((77.21615 28.63240 -8.0, 77.21630 28.63240 -8.0, 77.21630 28.63250 -8.0, 77.21615 28.63250 -8.0, 77.21615 28.63240 -8.0))', 4326)
        );
    """)

    cur.close()
    conn.close()
    print("Database initialization for 3D Bhu-Aadhaar (India) completed successfully!")

if __name__ == "__main__":
    init_db()
