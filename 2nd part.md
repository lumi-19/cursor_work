# Software Requirements Specification (SRS)
# WebGIS Disaster and AQI Monitoring System
## Part 2: System Features (Functional Requirements)

---

## 3. System Features (Functional Requirements)

This section describes the detailed functional requirements for each major feature of the system.

### 3.1 Real-Time Disaster Data Visualization

**3.1.1 Description**
The system shall display real-time disaster events on an interactive web map with appropriate symbology and information popups.

**3.1.2 Functional Requirements**

**FR-1.1:** The system shall fetch real-time disaster data from external APIs at regular intervals (default: every 10 minutes).

**FR-1.2:** The system shall display disaster events on the map using different symbols/icons based on disaster type (e.g., earthquake, flood, wildfire, hurricane, tsunami, volcanic eruption, cyclone).

**FR-1.3:** The system shall store fetched disaster data in the PostGIS database for historical tracking.

**FR-1.4:** Each disaster marker on the map shall be clickable and display a popup/info window containing:
   - Disaster type
   - Location (coordinates and city name if available)
   - Date and time of occurrence
   - Magnitude/severity (if available)
   - Source of information
   - Link to detailed information (if available)

**FR-1.5:** The system shall support filtering disaster events by:
   - Disaster type (checkboxes/select menu)
   - Date range (date picker)
   - Magnitude/severity range (slider or input fields)

**FR-1.6:** The system shall provide a legend showing disaster type symbols and their meanings.

**FR-1.7:** The system shall support clustering of disaster markers when zoomed out for better performance.

**FR-1.8:** The system shall update disaster markers automatically without requiring page refresh.

**FR-1.9:** The system shall handle API failures gracefully and display error messages to users.

**3.1.3 Input/Output**
- **Input:** Real-time disaster data from external APIs (JSON format)
- **Output:** Interactive map visualization with clickable markers and popups

**3.1.4 Processing**
- Parse JSON response from disaster API
- Validate and sanitize data
- Store data in PostGIS database
- Transform data to GeoJSON format for map display
- Render markers on map based on coordinates
- Update map layer periodically

---

### 3.2 Real-Time AQI Data Visualization

**3.2.1 Description**
The system shall display current Air Quality Index (AQI) data for multiple cities on an interactive map with color-coded indicators.

**3.2.2 Functional Requirements**

**FR-2.1:** The system shall fetch real-time AQI data from external APIs (e.g., OpenAQ) at regular intervals (default: every 15 minutes).

**FR-2.2:** The system shall display AQI data for cities using color-coded markers based on AQI value:
   - Green (0-50): Good
   - Yellow (51-100): Moderate
   - Orange (101-150): Unhealthy for Sensitive Groups
   - Red (151-200): Unhealthy
   - Purple (201-300): Very Unhealthy
   - Maroon (301-500): Hazardous

**FR-2.3:** The system shall store AQI data in the PostGIS database with timestamp for historical tracking.

**FR-2.4:** Each AQI marker shall display a popup containing:
   - City name and location
   - Overall AQI value and category
   - Individual pollutant values (PM2.5, PM10, O3, NO2, CO, SO2)
   - Measurement timestamp
   - Data source

**FR-2.5:** The system shall support filtering AQI data by:
   - City name (search/autocomplete)
   - AQI range (slider)
   - Pollutant type
   - Date/time range

**FR-2.6:** The system shall provide a color-coded legend for AQI categories.

**FR-2.7:** The system shall support toggling AQI layer visibility on/off.

**FR-2.8:** The system shall display AQI data for a minimum of 50 cities globally.

**FR-2.9:** The system shall update AQI markers automatically without page refresh.

**3.2.3 Input/Output**
- **Input:** Real-time AQI data from external APIs (JSON format)
- **Output:** Color-coded map markers with detailed AQI information popups

**3.2.4 Processing**
- Fetch AQI data from API endpoints
- Parse and validate AQI measurements
- Calculate AQI category based on standard formulas
- Store data in PostGIS with spatial coordinates
- Transform to GeoJSON for map visualization
- Apply color-coding based on AQI values
- Update map markers periodically

---

### 3.3 Historical Disaster Events

**3.3.1 Description**
The system shall provide access to historical disaster events stored in the database, allowing users to view and analyze past disasters.

**3.3.2 Functional Requirements**

**FR-3.1:** The system shall store all disaster events fetched from APIs in the PostGIS database with timestamps.

**FR-3.2:** The system shall provide a date range selector (calendar widget) to filter historical disasters.

**FR-3.3:** The system shall display historical disaster events on the map with the same symbology as real-time data.

**FR-3.4:** The system shall support filtering historical disasters by:
   - Disaster type
   - Date range (up to 1 year of historical data)
   - Geographic region/bounding box
   - Magnitude/severity range

**FR-3.5:** The system shall provide a timeline slider or date navigation controls for browsing historical events.

**FR-3.6:** The system shall display disaster event count statistics for selected filters.

**FR-3.7:** The system shall allow users to view detailed information for each historical disaster event.

**FR-3.8:** The system shall support animation/playback of disasters over time (optional advanced feature).

**FR-3.9:** The system shall display historical disaster events in a list/table view in addition to map view.

**FR-3.10:** The system shall support export of historical disaster data (see Section 3.6).

**3.3.3 Input/Output**
- **Input:** Date range, filter criteria from user interface
- **Output:** Map visualization of historical disasters, list/table view, statistics

**3.3.4 Processing**
- Query PostGIS database for disasters within date range
- Apply user-specified filters
- Retrieve spatial and attribute data
- Render markers on map
- Generate statistics and counts
- Display in both map and table formats

---

### 3.4 City Comparison for AQI

**3.4.1 Description**
The system shall enable users to compare AQI metrics between two or more cities, providing visual and tabular comparisons.

**3.4.2 Functional Requirements**

**FR-4.1:** The system shall allow users to select two or more cities for comparison through:
   - Search/autocomplete input
   - Checkbox list of available cities
   - Clicking on map markers

**FR-4.2:** The system shall display a comparison panel showing:
   - Side-by-side comparison of AQI values
   - Individual pollutant comparisons (PM2.5, PM10, O3, NO2, CO, SO2)
   - AQI category for each city
   - Timestamp of measurements

**FR-4.3:** The system shall generate visual comparison charts:
   - Bar charts for AQI and pollutant values
   - Line charts for historical trends (if historical data available)
   - Comparison tables

**FR-4.4:** The system shall highlight cities on the map that are being compared.

**FR-4.5:** The system shall allow users to add/remove cities from comparison dynamically.

**FR-4.6:** The system shall support comparison of current AQI values (real-time) and historical AQI values (for selected date range).

**FR-4.7:** The system shall display comparative statistics:
   - Highest/lowest AQI among selected cities
   - Average AQI
   - Rank ordering of cities by AQI

**FR-4.8:** The system shall support export of comparison data (see Section 3.6).

**FR-4.9:** The system shall provide a "Clear Comparison" button to reset selection.

**3.4.3 Input/Output**
- **Input:** City selection from user (2 or more cities)
- **Output:** Comparison panel with charts, tables, and highlighted map markers

**3.4.4 Processing**
- Retrieve AQI data for selected cities from database
- Calculate comparison metrics
- Generate visualization charts using charting library
- Update map highlighting
- Format data for display in comparison panel

---

### 3.5 Disaster-Pollution Correlation Analysis

**3.5.1 Description**
The system shall analyze and visualize the relationship between disaster events and pollution levels, showing how disasters affect air quality.

**3.5.2 Functional Requirements**

**FR-5.1:** The system shall identify AQI data for cities/regions where disasters occurred.

**FR-5.2:** The system shall retrieve AQI data for time periods:
   - Before disaster (pre-disaster baseline, e.g., 7-30 days before)
   - During disaster (if applicable, based on disaster duration)
   - After disaster (post-disaster, e.g., 7-30 days after)

**FR-5.3:** The system shall display pollution trend charts showing:
   - AQI values over time before, during, and after disaster
   - Individual pollutant trends (PM2.5, PM10, etc.)
   - Markers indicating disaster occurrence date

**FR-5.4:** The system shall calculate and display correlation metrics:
   - Percentage change in AQI before vs. after disaster
   - Statistical correlation coefficients (if applicable)
   - Maximum pollutant levels during post-disaster period

**FR-5.5:** The system shall allow users to select:
   - Specific disaster event (from map or list)
   - Time window for analysis (pre/post disaster period length)
   - Pollutant type(s) to analyze

**FR-5.6:** The system shall support analysis for multiple disasters simultaneously (comparative analysis).

**FR-5.7:** The system shall generate summary reports showing:
   - Average AQI change
   - Most affected pollutants
   - Duration of pollution impact
   - Recovery timeline (if applicable)

**FR-5.8:** The system shall visualize correlation on the map using:
   - Color-coded regions showing pollution impact severity
   - Overlay of disaster locations with pollution data
   - Heat maps showing pollution levels

**FR-5.9:** The system shall support filtering correlation analysis by:
   - Disaster type
   - Geographic region
   - Time period
   - Minimum impact threshold

**FR-5.10:** The system shall export correlation analysis results (see Section 3.6).

**3.5.3 Input/Output**
- **Input:** Selected disaster event(s), time window parameters, pollutant selection
- **Output:** Trend charts, correlation metrics, summary reports, map visualizations

**3.5.4 Processing**
- Query database for disaster and AQI data in temporal proximity
- Calculate pre-disaster baseline AQI values
- Retrieve post-disaster AQI measurements
- Compute correlation metrics and percentage changes
- Generate time series charts
- Create map visualizations
- Format results for display and export

---

### 3.6 Data Download Functionality

**3.6.1 Description**
The system shall provide functionality for users to download disaster and AQI data in various formats for offline analysis.

**3.6.2 Functional Requirements**

**FR-6.1:** The system shall support data download in the following formats:
   - CSV (Comma-Separated Values)
   - GeoJSON (for spatial data)
   - Shapefile (compressed as .zip)
   - JSON

**FR-6.2:** The system shall allow users to download:
   - Real-time disaster data (current snapshot)
   - Historical disaster data (for selected date range)
   - Real-time AQI data (current snapshot)
   - Historical AQI data (for selected date range)
   - Comparison data (for selected cities)
   - Correlation analysis results

**FR-6.3:** The system shall provide download filters allowing users to specify:
   - Data type (disasters or AQI)
   - Date range
   - Geographic extent (bounding box or selected cities)
   - Disaster type (for disaster data)
   - Pollutant type (for AQI data)

**FR-6.4:** The system shall generate downloadable files on-demand (server-side processing).

**FR-6.5:** The system shall provide a "Download" button/link that triggers file generation and download.

**FR-6.6:** The system shall display download progress indicator for large datasets.

**FR-6.7:** The system shall handle download requests asynchronously to avoid blocking the UI.

**FR-6.8:** The system shall limit download data size to prevent server overload (e.g., max 10,000 records per download).

**FR-6.9:** The system shall include metadata in downloaded files:
   - Data source
   - Export date/time
   - Filter criteria applied
   - Data schema/field descriptions

**FR-6.10:** The system shall support batch downloads (multiple files) with progress tracking.

**3.6.3 Input/Output**
- **Input:** Download parameters (format, filters, data type) from user
- **Output:** Downloadable file(s) in specified format(s)

**3.6.4 Processing**
- Validate download parameters
- Query PostGIS database based on filters
- Format data according to selected format (CSV, GeoJSON, Shapefile, JSON)
- Generate file(s) server-side
- Stream file(s) to client browser
- Clean up temporary files after download

---

### 3.7 Chatbot Integration

**3.7.1 Description**
The system shall include an intelligent chatbot that allows users to query disaster and AQI data using natural language.

**3.7.2 Functional Requirements**

**FR-7.1:** The system shall provide a chatbot interface (chat window) accessible from the main interface.

**FR-7.2:** The chatbot shall understand natural language queries about:
   - Current disaster events (e.g., "What disasters happened today?")
   - AQI data (e.g., "What's the air quality in New York?")
   - Historical disasters (e.g., "Show me earthquakes in the last month")
   - City comparisons (e.g., "Compare AQI between London and Paris")
   - Disaster-pollution correlations (e.g., "How did wildfires affect air quality in California?")

**FR-7.3:** The chatbot shall integrate with AI API service (DeepSeek API or OpenRouter API) for natural language processing.

**FR-7.4:** The chatbot backend (Flask) shall:
   - Receive user messages
   - Query PostGIS database based on interpreted user intent
   - Format database results for AI response
   - Send query and context to AI API
   - Return AI-generated response to user

**FR-7.5:** The chatbot shall provide conversational responses with:
   - Natural language text
   - Relevant statistics and data
   - Links or suggestions to view data on map (if applicable)
   - Follow-up question suggestions

**FR-7.6:** The chatbot shall handle ambiguous queries and ask for clarification when needed.

**FR-7.7:** The chatbot shall maintain conversation context within a session.

**FR-7.8:** The chatbot shall provide helpful tips and examples of queries users can ask.

**FR-7.9:** The chatbot interface shall include:
   - Chat message history
   - Input field for typing messages
   - Send button
   - Clear/restart conversation button
   - Minimize/maximize chat window

**FR-7.10:** The chatbot shall handle errors gracefully and provide helpful error messages.

**FR-7.11:** The chatbot shall respect API rate limits and handle API failures.

**3.7.3 Input/Output**
- **Input:** Natural language text queries from user
- **Output:** Natural language responses with relevant data and suggestions

**3.7.4 Processing**
- Receive user message via Flask API endpoint
- Parse and understand user intent (may use AI API or pattern matching)
- Query PostGIS database based on intent
- Format database results
- Send context and query to AI API (DeepSeek/OpenRouter)
- Receive AI-generated response
- Return formatted response to frontend
- Display response in chat interface

---

### 3.8 Interactive Map Visualization

**3.8.1 Description**
The system shall provide an interactive web map as the primary interface for visualizing disaster and AQI data.

**3.8.2 Functional Requirements**

**FR-8.1:** The system shall use Leaflet or MapLibre library for map rendering.

**FR-8.2:** The map shall support standard navigation controls:
   - Zoom in/out (mouse wheel, buttons, pinch on mobile)
   - Pan (click and drag)
   - Fit to bounds for selected data

**FR-8.3:** The system shall provide multiple base map options:
   - OpenStreetMap (default)
   - Satellite imagery
   - Terrain
   - Dark mode

**FR-8.4:** The system shall support layer management:
   - Toggle visibility of disaster layer
   - Toggle visibility of AQI layer
   - Toggle visibility of GeoServer layers
   - Layer opacity controls
   - Layer ordering (z-index)

**FR-8.5:** The system shall display a layer control panel (collapsible).

**FR-8.6:** The map shall be responsive and work on desktop and tablet devices.

**FR-8.7:** The system shall support map popups/tooltips for markers with detailed information.

**FR-8.8:** The system shall provide a search/geocoding feature to locate cities or coordinates.

**FR-8.9:** The system shall display coordinates and zoom level in status bar or info panel.

**FR-8.10:** The system shall support drawing tools (optional):
   - Draw bounding box for area selection
   - Measure distance
   - Measure area

**FR-8.11:** The map shall handle large numbers of markers efficiently (clustering, virtualization).

**FR-8.12:** The system shall integrate at least one GeoServer layer (WMS or WFS) as an overlay.

**3.8.3 Input/Output**
- **Input:** User interactions (zoom, pan, click), layer toggles, filter selections
- **Output:** Interactive map with markers, popups, and overlay layers

**3.8.4 Processing**
- Initialize map with default view and base layer
- Load and render GeoJSON data as map layers
- Handle user interactions and update map accordingly
- Fetch and render GeoServer layers via WMS/WFS
- Manage layer visibility and ordering
- Update markers based on filters and data updates

---

### 3.9 Two Unique/Innovative Features

**3.9.1 Description**
The system shall include two unique and innovative features that demonstrate advanced capabilities and creative thinking.

**3.9.2 Functional Requirements**

**FR-9.1:** *(Feature 1 - To be specified by development team)*
- Description: [To be determined]
- Requirements: [To be determined]
- Implementation approach: [To be determined]

**FR-9.2:** *(Feature 2 - To be specified by development team)*
- Description: [To be determined]
- Requirements: [To be determined]
- Implementation approach: [To be determined]

**Note:** These features should be innovative, technically challenging, and add significant value to the system. Some suggestions (not requirements):
- Predictive analytics or trend forecasting
- 3D visualization of disaster or pollution data
- Real-time notification system
- Advanced statistical analysis tools
- Machine learning-based pattern recognition
- Social media integration for disaster reports
- Collaborative annotation features
- Mobile-responsive progressive web app features

---

## 4. External Interface Requirements

### 4.1 User Interfaces

**4.1.1 Web Application Interface**

The system shall provide a web-based user interface built with React and styled with Tailwind CSS.

**UI-1.1:** **Layout Structure**
- Header bar with system title and navigation
- Main content area with map (occupying majority of screen)
- Sidebar panel (collapsible) for filters, comparisons, and controls
- Footer with attribution and metadata

**UI-1.2:** **Map Interface**
- Interactive map using Leaflet/MapLibre
- Map controls (zoom, layer switcher, fullscreen)
- Marker clusters for performance
- Popups with detailed information
- Legend panel

**UI-1.3:** **Navigation and Menu**
- Menu button/toggle for sidebar
- Clear navigation between different views
- Breadcrumbs or back button where applicable
- Help/documentation link

**UI-1.4:** **Filter Panel**
- Date range picker
- Disaster type checkboxes
- City search/selection
- AQI range sliders
- Apply/Reset filter buttons
- Active filter indicators

**UI-1.5:** **Comparison Panel**
- City selection interface
- Comparison charts and tables
- Add/remove city buttons
- Export comparison data button

**UI-1.6:** **Data Download Interface**
- Format selection (radio buttons or dropdown)
- Filter selection interface
- Download button with progress indicator
- Download history (optional)

**UI-1.7:** **Chatbot Interface**
- Chat window (minimizable/maximizable)
- Message history area (scrollable)
- Input field with send button
- Typing indicator
- Clear conversation button

**UI-1.8:** **Responsive Design**
- Desktop layout (full features)
- Tablet layout (adapted sidebar, touch-friendly)
- Mobile-friendly elements (larger buttons, touch targets)

**UI-1.9:** **Visual Design Requirements**
- Clean, modern design using Tailwind CSS
- Consistent color scheme
- Accessible color contrasts
- Readable fonts and sizes
- Loading indicators for async operations
- Error message displays
- Success confirmations

**UI-1.10:** **User Feedback**
- Loading spinners for data fetching
- Success messages for downloads
- Error messages for failures
- Tooltips for unclear elements
- Confirmation dialogs for destructive actions

---

### 4.2 Hardware Interfaces

**4.2.1 Server Hardware**
- Standard x86/x64 architecture
- Minimum 8GB RAM (recommended: 16GB)
- Minimum 100GB storage (SSD recommended)
- Network interface for internet connectivity
- Local server deployment (no cloud requirements)

**4.2.2 Client Hardware**
- Desktop computers, laptops, or tablets
- Standard input devices (keyboard, mouse, touchscreen)
- Display resolution: minimum 1280x720, recommended 1920x1080 or higher
- Internet connection (broadband recommended)

---

### 4.3 Software Interfaces

**4.3.1 Operating System**
- Server: Windows, Linux, or macOS (local server)
- Client: Any OS with modern web browser

**4.3.2 Database Interface**
- **PostgreSQL with PostGIS:** Primary database for spatial and attribute data
  - Connection: Python psycopg2 or SQLAlchemy
  - Version: PostgreSQL 12+ with PostGIS 3.0+
  - Authentication: Database user credentials
  - Connection pooling for performance

**4.3.3 Map Server Interface**
- **GeoServer:** OGC-compliant map server
  - Protocols: WMS (Web Map Service), WFS (Web Feature Service)
  - Authentication: Basic HTTP authentication (if configured)
  - Connection: HTTP/HTTPS requests
  - At least one GeoServer layer must be integrated

**4.3.4 External API Interfaces**

**Disaster Data APIs:**
- USGS Earthquake API
- NOAA Severe Weather API
- ReliefWeb API
- Or other publicly available disaster data APIs
- Protocol: REST API (JSON responses)
- Authentication: API keys (if required)

**AQI Data APIs:**
- OpenAQ API
- AQICN API
- AirVisual API
- Or other publicly available AQI data APIs
- Protocol: REST API (JSON responses)
- Authentication: API keys (if required)

**AI Service APIs:**
- DeepSeek API or OpenRouter API
- Protocol: REST API (JSON requests/responses)
- Authentication: API keys (required)
- Endpoint: Chat/completion endpoint

---

### 4.4 Communication Interfaces

**4.4.1 Frontend-Backend Communication**
- **Protocol:** HTTP/HTTPS
- **Format:** REST API
- **Data Format:** JSON
- **Endpoints:** Defined in API Specifications (Section 7)

**4.4.2 Backend-Database Communication**
- **Protocol:** PostgreSQL native protocol
- **Library:** psycopg2 or SQLAlchemy (Python)
- **Connection String:** Database connection parameters
- **Queries:** SQL with PostGIS spatial functions

**4.4.3 Backend-External API Communication**
- **Protocol:** HTTP/HTTPS
- **Library:** Python requests library
- **Format:** JSON (request/response)
- **Authentication:** API keys in headers (if required)
- **Error Handling:** HTTP status codes, retry logic

**4.4.4 Backend-GeoServer Communication**
- **Protocol:** HTTP/HTTPS
- **WMS Requests:** GetMap, GetCapabilities
- **WFS Requests:** GetFeature (if applicable)
- **Format:** Image tiles (WMS), GeoJSON/XML (WFS)
- **Parameters:** BBOX, CRS, layers, format, etc.

**4.4.5 Frontend-Map Library Communication**
- **Library:** Leaflet.js or MapLibre GL JS
- **Data Format:** GeoJSON for vector data
- **Tile Format:** Image tiles or vector tiles
- **Protocol:** HTTP/HTTPS for tile requests

---

## 5. System Architecture

### 5.1 Architecture Overview

The WebGIS Disaster and AQI Monitoring System follows a three-tier client-server architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT TIER                          │
│  (React Frontend - Browser)                             │
│  - User Interface                                       │
│  - Map Visualization (Leaflet/MapLibre)                │
│  - State Management                                     │
│  - API Calls to Backend                                 │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/HTTPS (REST API)
                   │ JSON
┌──────────────────▼──────────────────────────────────────┐
│                 APPLICATION TIER                        │
│  (Python Flask Backend)                                 │
│  - REST API Endpoints                                   │
│  - Business Logic                                       │
│  - Data Processing                                      │
│  - AI Chatbot Integration                               │
│  - External API Integration                             │
└──┬───────────────┬───────────────┬─────────────────────┘
   │               │               │
   │               │               │
   │               │               │
┌──▼──────┐  ┌─────▼─────┐  ┌─────▼────────┐
│ PostGIS │  │ GeoServer │  │ External APIs│
│Database │  │ (WMS/WFS) │  │ (Disaster,   │
│         │  │           │  │  AQI, AI)    │
└─────────┘  └───────────┘  └──────────────┘
          DATA TIER
```

### 5.2 Component Architecture

**5.2.1 Frontend Components (React)**

The frontend is organized into React components:

- **App Component:** Main application container
- **Map Component:** Interactive map using Leaflet/MapLibre
- **DisasterLayer Component:** Disaster markers layer
- **AQILayer Component:** AQI markers layer
- **FilterPanel Component:** Filter controls sidebar
- **ComparisonPanel Component:** City comparison interface
- **CorrelationPanel Component:** Disaster-pollution correlation interface
- **DownloadPanel Component:** Data download interface
- **Chatbot Component:** Chatbot interface
- **Header Component:** Navigation header
- **Legend Component:** Map legend
- **Popup Component:** Marker information popups

**5.2.2 Backend Components (Flask)**

The backend is organized into Flask blueprints/modules:

- **API Routes:** REST API endpoints
  - `/api/disasters` - Disaster data endpoints
  - `/api/aqi` - AQI data endpoints
  - `/api/cities` - City data endpoints
  - `/api/comparison` - Comparison endpoints
  - `/api/correlation` - Correlation analysis endpoints
  - `/api/download` - Download endpoints
  - `/api/chatbot` - Chatbot endpoints

- **Database Models:** SQLAlchemy models for PostGIS
- **Services:** Business logic modules
  - DisasterService
  - AQIService
  - ComparisonService
  - CorrelationService
  - DownloadService
  - ChatbotService

- **API Clients:** External API integration modules
  - DisasterAPIClient
  - AQAPIClient
  - AIServiceClient (DeepSeek/OpenRouter)

- **Utilities:** Helper functions
  - Database utilities
  - Data transformation utilities
  - File generation utilities

**5.2.3 Database Components (PostGIS)**

- **Tables:**
  - `disasters` - Disaster events table
  - `aqi_measurements` - AQI data table
  - `cities` - City information table
  - `geoserver_layers` - GeoServer layer metadata (optional)

- **Spatial Functions:**
  - PostGIS spatial queries
  - Spatial indexing (GIST indexes)
  - Coordinate transformations

**5.2.4 GeoServer Components**

- **Workspaces:** Organization of layers
- **Data Stores:** Connections to PostGIS
- **Layers:** Published map layers (minimum one required)
- **Styles:** Symbology definitions

### 5.3 Data Flow

**5.3.1 Real-Time Data Flow**

```
External APIs → Flask Backend → PostGIS Database
                     ↓
              Frontend (React)
                     ↓
              User Browser
```

1. Flask backend periodically fetches data from external APIs
2. Data is processed and validated
3. Data is stored in PostGIS database
4. Frontend requests data via REST API
5. Backend queries PostGIS and returns JSON
6. Frontend renders data on map

**5.3.2 User Query Flow**

```
User Input → Frontend → Flask API → PostGIS Query → Results → Frontend → User Display
```

**5.3.3 Chatbot Flow**

```
User Message → Frontend → Flask API → PostGIS Query → AI API (DeepSeek/OpenRouter) → Response → Frontend → User Display
```

**5.3.4 GeoServer Layer Flow**

```
PostGIS → GeoServer → WMS/WFS Request → Frontend → Map Display
```

### 5.4 Technology Stack Details

**Frontend Stack:**
- **React:** UI library (version 18+)
- **Tailwind CSS:** Styling framework
- **Leaflet/MapLibre:** Mapping library
- **Axios/Fetch:** HTTP client for API calls
- **React Router:** Client-side routing (if multi-page)
- **State Management:** React Context API or Redux (if needed)
- **Chart Libraries:** Chart.js or Recharts (for comparison charts)
- **Build Tool:** Create React App or Vite

**Backend Stack:**
- **Python:** Programming language (3.8+)
- **Flask:** Web framework
- **SQLAlchemy:** ORM for database
- **psycopg2:** PostgreSQL adapter
- **GeoAlchemy2:** PostGIS support for SQLAlchemy
- **Requests:** HTTP client for external APIs
- **Flask-CORS:** CORS handling
- **Python-dotenv:** Environment variables

**Database Stack:**
- **PostgreSQL:** Relational database (12+)
- **PostGIS:** Spatial extension (3.0+)

**Map Server:**
- **GeoServer:** OGC-compliant map server (2.20+)

**AI Integration:**
- **DeepSeek API** or **OpenRouter API**

### 5.5 System Integration Points

1. **Frontend ↔ Backend:** REST API over HTTP/HTTPS
2. **Backend ↔ PostGIS:** PostgreSQL connection via psycopg2/SQLAlchemy
3. **Backend ↔ External APIs:** HTTP requests (disaster data, AQI data)
4. **Backend ↔ AI API:** HTTP requests (chatbot functionality)
5. **Frontend ↔ GeoServer:** WMS/WFS requests for map layers
6. **Backend ↔ GeoServer:** Configuration and layer management (optional, can be manual)
