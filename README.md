# Car Search API

A FastAPI-based web application that enables natural language search for cars using LLM-powered filtering. The application loads car data from a CSV file and allows users to query cars using conversational language.

## Features

- **Natural Language Search**: Query cars using everyday language (e.g., "Find red cars under 10 lakhs")
- **LLM-Powered Filtering**: Uses OpenAI-compatible models via OpenRouter for intelligent query understanding
- **RESTful API**: Clean API endpoints for integration
- **Web Interface**: Simple frontend for direct user interaction
- **Docker Support**: Containerized deployment with Docker Compose
- **Health Monitoring**: Built-in health checks and dataset information

## Technologies

- **Backend**: FastAPI (Python)
- **Data Processing**: Pandas
- **LLM Integration**: OpenAI API via OpenRouter
- **Frontend**: HTML/CSS/JavaScript
- **Containerization**: Docker & Docker Compose
- **Data Source**: CarDekho CSV dataset

## Installation

### Prerequisites

- Python 3.8+
- Docker & Docker Compose (for containerized deployment)

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cardekho
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env` and configure your OpenRouter API key

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Open your browser to `http://localhost:8000`

### Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. The application will be available at `http://localhost:8000`

## Usage

### Web Interface

Visit the root URL to access the web interface. Enter natural language queries like:
- "Show me Toyota cars from 2020"
- "Find SUVs with automatic transmission"
- "Red cars with mileage above 15 km/l"

### API Usage

The API provides several endpoints:

#### Health Check
```bash
GET /health
```

#### Dataset Information
```bash
GET /dataset
```

#### Search Cars (GET)
```bash
GET /search?q=your+query&max_results=100
```

#### Search Cars (POST)
```bash
POST /search
Content-Type: application/json

{
  "query": "Find red cars under 10 lakhs",
  "max_results": 50
}
```

#### API Information
```bash
GET /api
```

## Configuration

Environment variables (in `.env` file):
- `OPENROUTER_API_KEY`: Your OpenRouter API key for LLM access
- `PORT`: Server port (default: 8000)

## Data

The application uses a CSV file (`app/cardekho.csv`) containing car data with columns for:
- Car name
- Year
- Selling price
- Present price
- Kms driven
- Fuel type
- Seller type
- Transmission
- Owner

## Development

### Running Tests

```bash
python -m pytest test_scripts.py/
```

### Code Structure

```
app/
├── main.py          # FastAPI application and routes
├── caragent.py      # LLM-powered car search agent
├── schemas.py       # Pydantic models
├── config.py        # Configuration
├── cardekho.csv     # Car dataset
└── __init__.py

static/
├── index.html       # Frontend HTML
├── style.css        # Frontend styles
└── script.js        # Frontend JavaScript

test_scripts.py/
├── test.py          # Unit tests
└── test.ipynb       # Jupyter notebook for testing
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.