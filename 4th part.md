# Software Requirements Specification (SRS)
# WebGIS Disaster and AQI Monitoring System
## Part 4: API Specifications and Non-Functional Requirements

---

## 7. API Specifications

### 7.1 API Overview

The system provides a RESTful API built with Python Flask. The API serves as the communication layer between the frontend (React) and backend (Flask), as well as between the backend and external services.

**Base URL:** `http://localhost:5000/api` (development)
**Protocol:** HTTP/HTTPS
**Data Format:** JSON (request and response)
**Authentication:** None (initial version - all endpoints are publicly accessible)

---

### 7.2 API Endpoints

#### 7.2.1 Disaster Endpoints

**GET /api/disasters**

Fetch disaster events with optional filtering.

**Query Parameters:**
- `disaster_type` (optional): Filter by disaster type (e.g., "earthquake", "flood")
- `start_date` (optional): Start date (ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- `end_date` (optional): End date (ISO 8601 format)
- `min_magnitude` (optional): Minimum magnitude (decimal)
- `max_magnitude` (optional): Maximum magnitude (decimal)
- `bbox` (optional): Bounding box (format: min_lon,min_lat,max_lon,max_lat)
- `limit` (optional): Maximum number of results (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
{
  "success": true,
  "count": 50,
  "data": [
    {
      "id": 1,
      "disaster_type": "earthquake",
      "title": "Earthquake in California",
      "description": "Magnitude 5.2 earthquake",
      "latitude": 37.7749,
      "longitude": -122.4194,
      "occurred_at": "2024-01-15T10:30:00Z",
      "magnitude": 5.2,
      "severity": "medium",
      "status": "resolved",
      "source": "USGS",
      "source_id": "usgs12345",
      "url": "https://example.com/disaster/12345"
    }
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid date format",
  "message": "Date must be in ISO 8601 format"
}
```

---

**GET /api/disasters/{id}**

Fetch a specific disaster event by ID.

**Path Parameters:**
- `id`: Disaster event ID (integer)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "disaster_type": "earthquake",
    "title": "Earthquake in California",
    "description": "Magnitude 5.2 earthquake",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "occurred_at": "2024-01-15T10:30:00Z",
    "magnitude": 5.2,
    "severity": "medium",
    "status": "resolved",
    "source": "USGS",
    "source_id": "usgs12345",
    "url": "https://example.com/disaster/12345"
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Not Found",
  "message": "Disaster event not found"
}
```

---

**GET /api/disasters/geojson**

Fetch disaster events as GeoJSON format for map visualization.

**Query Parameters:** (Same as GET /api/disasters)

**Response (200 OK):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-122.4194, 37.7749]
      },
      "properties": {
        "id": 1,
        "disaster_type": "earthquake",
        "title": "Earthquake in California",
        "magnitude": 5.2,
        "severity": "medium",
        "occurred_at": "2024-01-15T10:30:00Z"
      }
    }
  ]
}
```

---

#### 7.2.2 AQI Endpoints

**GET /api/aqi**

Fetch AQI measurements with optional filtering.

**Query Parameters:**
- `city_id` (optional): Filter by city ID (integer)
- `city_name` (optional): Filter by city name (string)
- `start_date` (optional): Start date (ISO 8601 format)
- `end_date` (optional): End date (ISO 8601 format)
- `min_aqi` (optional): Minimum AQI value (integer, 0-500)
- `max_aqi` (optional): Maximum AQI value (integer, 0-500)
- `bbox` (optional): Bounding box
- `limit` (optional): Maximum number of results (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
{
  "success": true,
  "count": 25,
  "data": [
    {
      "id": 1,
      "city_id": 1,
      "city_name": "New York",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "measured_at": "2024-01-15T12:00:00Z",
      "aqi_value": 85,
      "aqi_category": "moderate",
      "pm25": 35.5,
      "pm10": 55.2,
      "o3": 120.0,
      "no2": 45.3,
      "co": 8.5,
      "so2": 12.1,
      "source": "OpenAQ",
      "url": "https://example.com/aqi/12345"
    }
  ]
}
```

---

**GET /api/aqi/latest**

Fetch latest AQI measurements for all cities or specific cities.

**Query Parameters:**
- `city_ids` (optional): Comma-separated city IDs (e.g., "1,2,3")
- `city_names` (optional): Comma-separated city names (e.g., "New York,London")

**Response (200 OK):**
```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "id": 1,
      "city_id": 1,
      "city_name": "New York",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "measured_at": "2024-01-15T12:00:00Z",
      "aqi_value": 85,
      "aqi_category": "moderate",
      "pm25": 35.5,
      "pm10": 55.2,
      "o3": 120.0,
      "no2": 45.3,
      "co": 8.5,
      "so2": 12.1
    }
  ]
}
```

---

**GET /api/aqi/geojson**

Fetch AQI measurements as GeoJSON format.

**Query Parameters:** (Same as GET /api/aqi)

**Response (200 OK):** (GeoJSON FeatureCollection format)

---

#### 7.2.3 City Endpoints

**GET /api/cities**

Fetch list of cities.

**Query Parameters:**
- `country` (optional): Filter by country name
- `country_code` (optional): Filter by country code (e.g., "US")
- `search` (optional): Search city name (case-insensitive)
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Pagination offset

**Response (200 OK):**
```json
{
  "success": true,
  "count": 50,
  "data": [
    {
      "id": 1,
      "name": "New York",
      "country": "United States",
      "country_code": "US",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "population": 8336817,
      "timezone": "America/New_York"
    }
  ]
}
```

---

**GET /api/cities/{id}**

Fetch a specific city by ID.

**Path Parameters:**
- `id`: City ID (integer)

**Response (200 OK):** (City object)

---

#### 7.2.4 Comparison Endpoints

**GET /api/comparison/aqi**

Compare AQI data between multiple cities.

**Query Parameters:**
- `city_ids` (required): Comma-separated city IDs (e.g., "1,2,3")
- `date` (optional): Specific date for comparison (ISO 8601 format, defaults to latest)

**Response (200 OK):**
```json
{
  "success": true,
  "comparison_date": "2024-01-15T12:00:00Z",
  "cities": [
    {
      "city_id": 1,
      "city_name": "New York",
      "aqi_value": 85,
      "aqi_category": "moderate",
      "pm25": 35.5,
      "pm10": 55.2,
      "o3": 120.0,
      "no2": 45.3,
      "co": 8.5,
      "so2": 12.1
    },
    {
      "city_id": 2,
      "city_name": "London",
      "aqi_value": 72,
      "aqi_category": "moderate",
      "pm25": 28.3,
      "pm10": 42.1,
      "o3": 95.0,
      "no2": 38.7,
      "co": 6.2,
      "so2": 8.9
    }
  ],
  "statistics": {
    "highest_aqi": 85,
    "lowest_aqi": 72,
    "average_aqi": 78.5
  }
}
```

---

**GET /api/comparison/aqi/historical**

Compare historical AQI trends between cities.

**Query Parameters:**
- `city_ids` (required): Comma-separated city IDs
- `start_date` (required): Start date (ISO 8601 format)
- `end_date` (required): End date (ISO 8601 format)
- `interval` (optional): Data aggregation interval - "hour", "day", "week" (default: "day")

**Response (200 OK):**
```json
{
  "success": true,
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-15T23:59:59Z",
  "interval": "day",
  "data": [
    {
      "date": "2024-01-01",
      "cities": [
        {
          "city_id": 1,
          "city_name": "New York",
          "avg_aqi": 82,
          "avg_pm25": 32.5
        },
        {
          "city_id": 2,
          "city_name": "London",
          "avg_aqi": 70,
          "avg_pm25": 26.8
        }
      ]
    }
  ]
}
```

---

#### 7.2.5 Correlation Endpoints

**GET /api/correlation/disaster-aqi**

Analyze correlation between disaster events and AQI data.

**Query Parameters:**
- `disaster_id` (optional): Specific disaster ID (if not provided, analyzes all disasters)
- `city_id` (optional): Filter by city ID
- `disaster_type` (optional): Filter by disaster type
- `pre_days` (optional): Days before disaster to analyze (default: 7)
- `post_days` (optional): Days after disaster to analyze (default: 30)
- `distance_km` (optional): Maximum distance from disaster location (default: 100)

**Response (200 OK):**
```json
{
  "success": true,
  "correlations": [
    {
      "disaster_id": 1,
      "disaster_type": "wildfire",
      "disaster_title": "Wildfire in California",
      "disaster_date": "2024-01-10T00:00:00Z",
      "location": {
        "latitude": 37.7749,
        "longitude": -122.4194
      },
      "affected_cities": [
        {
          "city_id": 1,
          "city_name": "San Francisco",
          "distance_km": 25.5,
          "pre_disaster_avg_aqi": 65,
          "post_disaster_avg_aqi": 185,
          "aqi_change_percent": 184.6,
          "peak_aqi": 285,
          "peak_aqi_date": "2024-01-12T00:00:00Z",
          "pollutants_affected": ["pm25", "pm10"],
          "recovery_days": 15
        }
      ],
      "summary": {
        "total_affected_cities": 3,
        "avg_aqi_increase": 125.5,
        "max_aqi_increase": 220
      }
    }
  ]
}
```

---

#### 7.2.6 Download Endpoints

**GET /api/download/disasters**

Download disaster data in specified format.

**Query Parameters:**
- `format` (required): Export format - "csv", "geojson", "json", "shapefile"
- `disaster_type` (optional): Filter by disaster type
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `bbox` (optional): Bounding box

**Response:**
- For CSV/JSON/GeoJSON: Direct download with appropriate Content-Type header
- For Shapefile: ZIP file download

**Headers:**
```
Content-Type: application/csv (for CSV)
Content-Type: application/json (for JSON)
Content-Type: application/geo+json (for GeoJSON)
Content-Type: application/zip (for Shapefile)
Content-Disposition: attachment; filename="disasters_2024-01-15.csv"
```

---

**GET /api/download/aqi**

Download AQI data in specified format.

**Query Parameters:**
- `format` (required): Export format
- `city_ids` (optional): Comma-separated city IDs
- `start_date` (optional): Start date
- `end_date` (optional): End date

**Response:** (Same as download/disasters)

---

#### 7.2.7 Chatbot Endpoints

**POST /api/chatbot/message**

Send a message to the chatbot and receive a response.

**Request Body:**
```json
{
  "message": "What disasters happened today?",
  "conversation_id": "optional-conversation-id",
  "context": {
    "city_name": "optional",
    "date_range": "optional"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "response": "Today, there were 3 earthquakes, 2 wildfires, and 1 flood reported. The most significant was a magnitude 5.2 earthquake in California. Would you like more details about any specific event?",
  "conversation_id": "generated-conversation-id",
  "suggested_actions": [
    {
      "type": "view_map",
      "label": "View disasters on map",
      "url": "/map?filter=disasters"
    },
    {
      "type": "query",
      "label": "Show details about California earthquake",
      "query": "Show details about earthquake in California"
    }
  ],
  "data_references": [
    {
      "type": "disaster",
      "id": 1,
      "title": "Earthquake in California"
    }
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid request",
  "message": "Message field is required"
}
```

---

**POST /api/chatbot/clear**

Clear conversation history for a conversation ID.

**Request Body:**
```json
{
  "conversation_id": "conversation-id-to-clear"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Conversation cleared"
}
```

---

### 7.3 Error Handling

**Standard Error Response Format:**
```json
{
  "success": false,
  "error": "Error Type",
  "message": "Detailed error message",
  "code": 400
}
```

**HTTP Status Codes:**
- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: External API unavailable

---

### 7.4 API Rate Limiting (Optional)

For production deployment, rate limiting should be implemented:
- Limit: 100 requests per minute per IP address
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

### 7.5 Data Format Specifications

**7.5.1 Date/Time Format**
- ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ` (UTC)
- Example: `2024-01-15T10:30:00Z`

**7.5.2 Coordinate Format**
- Decimal degrees (WGS84)
- Latitude: -90 to 90
- Longitude: -180 to 180

**7.5.3 Bounding Box Format**
- Format: `min_lon,min_lat,max_lon,max_lat`
- Example: `-122.5,37.7,-122.3,37.8`

**7.5.4 GeoJSON Format**
- Follows GeoJSON specification (RFC 7946)
- Coordinate order: [longitude, latitude]
- CRS: WGS84 (EPSG:4326)

---

## 8. Non-Functional Requirements

### 8.1 Performance Requirements

**8.1.1 Response Time**
- API endpoints should respond within 2 seconds for standard queries
- Map tiles should load within 1 second
- Database queries should complete within 500ms for common operations
- Chatbot responses should be returned within 5 seconds

**8.1.2 Throughput**
- System should handle at least 100 concurrent users
- API should support at least 1000 requests per minute
- Database should handle at least 100 queries per second

**8.1.3 Data Update Frequency**
- Real-time disaster data: Updated every 10 minutes
- Real-time AQI data: Updated every 15 minutes
- Historical data: Available immediately after fetching

**8.1.4 Scalability**
- System should be able to store 1 year of historical data
- Database should handle at least 100,000 disaster records
- Database should handle at least 500,000 AQI measurement records
- System should handle growth in data volume over time

**8.1.5 Resource Usage**
- Server memory usage should not exceed 4GB under normal load
- Database size should not exceed 50GB (with 1 year of data)
- CPU usage should remain below 70% under normal load

---

### 8.2 Security Requirements

**8.2.1 Data Security**
- All API endpoints should validate input parameters
- SQL injection prevention through parameterized queries
- XSS (Cross-Site Scripting) prevention through input sanitization
- CSRF protection for state-changing operations (if authentication added)

**8.2.2 API Security**
- Input validation for all API parameters
- Rate limiting to prevent abuse (optional for initial version)
- CORS (Cross-Origin Resource Sharing) configuration for frontend access
- Error messages should not expose sensitive system information

**8.2.3 Data Privacy**
- No personal user data is collected (initial version)
- Attribution of external data sources
- Compliance with API terms of service

**8.2.4 System Security**
- Secure configuration of PostgreSQL database
- Secure configuration of GeoServer
- Regular security updates for dependencies
- Environment variables for sensitive configuration (API keys, database credentials)

---

### 8.3 Reliability Requirements

**8.3.1 Availability**
- System should be available 95% of the time during operational hours
- Graceful degradation when external APIs are unavailable
- Error handling for API failures

**8.3.2 Fault Tolerance**
- System should handle external API failures gracefully
- Database connection failures should be handled with retry logic
- Frontend should handle API errors with user-friendly messages

**8.3.3 Data Integrity**
- Database transactions for critical operations
- Data validation before storage
- Duplicate detection for external API data

**8.3.4 Backup and Recovery**
- Regular database backups (recommended)
- Recovery procedures for data loss scenarios
- Version control for code and configuration

---

### 8.4 Maintainability Requirements

**8.4.1 Code Quality**
- Follow Python PEP 8 style guide for backend code
- Follow JavaScript/React best practices for frontend code
- Code comments and documentation
- Modular code structure

**8.4.2 Documentation**
- API documentation (this SRS)
- Code comments and docstrings
- Deployment instructions
- Configuration guides

**8.4.3 Testing**
- Unit tests for critical functions
- Integration tests for API endpoints
- End-to-end tests for user workflows (recommended)
- Testing documentation

**8.4.4 Logging**
- Application logging for errors and important events
- API request/response logging (optional)
- Database query logging (optional, for debugging)

---

### 8.5 Usability Requirements

**8.5.1 User Interface**
- Intuitive and easy-to-use interface
- Clear navigation and controls
- Responsive design for desktop and tablet devices
- Accessible design (WCAG 2.1 Level AA compliance recommended)

**8.5.2 User Feedback**
- Loading indicators for async operations
- Success messages for completed actions
- Clear error messages
- Tooltips for complex features

**8.5.3 Performance**
- Fast page load times (< 3 seconds)
- Smooth map interactions
- Responsive UI elements
- Minimal lag when interacting with filters and controls

**8.5.4 Documentation**
- User guide/documentation (recommended)
- Help tooltips and inline help
- Example queries for chatbot
- Feature explanations

---

### 8.6 Compatibility Requirements

**8.6.1 Browser Compatibility**
- Chrome (latest version)
- Firefox (latest version)
- Safari (latest version)
- Edge (latest version)

**8.6.2 Operating System Compatibility**
- Windows 10+
- macOS 10.15+
- Linux (Ubuntu 20.04+)

**8.6.3 Database Compatibility**
- PostgreSQL 12+ with PostGIS 3.0+

**8.6.4 API Compatibility**
- REST API following RESTful principles
- OGC standards (WMS, WFS) for GeoServer layers
- GeoJSON format for spatial data

---

### 8.7 Portability Requirements

**8.7.1 Deployment**
- System should run on local server infrastructure
- Docker containerization support (optional)
- Environment-based configuration
- Easy deployment instructions

**8.7.2 Configuration**
- Configuration through environment variables
- Separate configuration for development and production
- Database connection configuration
- API key configuration

---

This completes the API Specifications and Non-Functional Requirements sections.
