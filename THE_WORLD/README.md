# THE_WORLD - WebGIS Disaster and AQI Monitoring System

A comprehensive web-based Geographic Information System for monitoring real-time disasters and Air Quality Index (AQI) data with interactive mapping, analysis, and intelligent chatbot capabilities.

## Project Structure

```
THE_WORLD/
├── backend/          # Python Flask backend
│   ├── app/          # Application code
│   ├── services/     # External API services
│   ├── utils/        # Utility functions
│   └── app.py        # Flask application entry point
├── frontend/         # React + Vite frontend
└── README.md         # This file
```

## Technology Stack

### Backend
- Python 3.8+
- Flask (Web framework)
- PostgreSQL with PostGIS (Spatial database)
- SQLAlchemy (ORM)
- GeoAlchemy2 (PostGIS support)

### Frontend
- React 18+
- Vite (Build tool)
- Tailwind CSS (Styling)
- Leaflet (Mapping library)
- Axios (HTTP client)

### Services
- GeoServer (Map server)
- OpenRouter API (AI Chatbot)
- OpenAQ API (AQI data)
- OpenWeather API (Weather/AQI data)
- USGS API (Earthquake data)
- NOAA API (Disaster data)

## Setup Instructions

### Prerequisites
- PostgreSQL 12+ with PostGIS extension
- GeoServer 2.20+
- Python 3.8+
- Node.js 16+
- npm or yarn

### Database Setup

1. Create the database schema:
```bash
psql -U postgres -d WebGis -f backend/database_schema.sql
```

2. Verify PostGIS extension is enabled:
```sql
SELECT PostGIS_version();
```

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy `.env` file and update with your credentials
   - Ensure all API keys are set

5. Run the Flask application:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## Configuration

### Environment Variables (Backend)

See `backend/.env` file for configuration:
- Database connection settings
- GeoServer settings
- API keys
- Flask configuration

## Development

### Backend API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check

More endpoints will be added as development progresses.

### Database Schema

- `cities` - City information with spatial data
- `disasters` - Disaster event records
- `aqi_measurements` - AQI measurement records

## License

Academic project - Final Year Project
