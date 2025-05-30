# Stock Terminal

A Bloomberg-style stock terminal built with Python FastAPI backend and vanilla JavaScript frontend.

## Features

- **Terminal Interface**: Command-line style interface with Bloomberg aesthetics
- **Real-time Data**: Stock quotes, charts, and market information
- **Portfolio Management**: Track your investments with P&L calculations
- **Multiple Data Sources**: Yahoo Finance, Polygon.io, SEC filings with fallbacks
- **Movable/Resizable Windows**: Drag and resize terminal windows
- **API Integration**: RESTful API with comprehensive endpoints

## Quick Start

### Using Docker (Recommended)

\`\`\`bash
# Clone the repository
git clone <repository-url>
cd stock-terminal

# Copy environment file
cp .env.example .env

# Edit .env with your API keys (optional - demo keys work for testing)
nano .env

# Start with Docker Compose
docker-compose up
\`\`\`

### Manual Installation

\`\`\`bash
# Install Python dependencies
pip install -r requirements.txt

# Start the server
python main.py
\`\`\`

Open your browser to `http://localhost:8000`

## Terminal Commands

- `help` - Show command reference
- `view AAPL` - Comprehensive stock analysis
- `quote MSFT` - Quick price quote
- `chart GOOGL` - ASCII price chart
- `portfolio` - Portfolio summary with P&L
- `add TSLA 10 800` - Add stock to portfolio
- `news` - Market news feed
- `sec AAPL` - SEC filings
- `clear` - Clear all windows

## API Endpoints

### Stock Router (`/stocks`)
- `GET /stocks/{ticker}/info` - Comprehensive stock info with Plotly charts
- `GET /stocks/{ticker}/quote` - Quick stock quote
- `GET /stocks/{ticker}/chart` - Chart data with period parameter
- `GET /stocks/{ticker}/sec` - SEC filings

### Portfolio Router (`/portfolio`)
- `POST /portfolio/add` - Add stock with validation
- `GET /portfolio/summary` - Portfolio summary
- `GET /portfolio/holdings` - Detailed holdings

### Legacy Endpoints (`/api`)
- Backward compatible endpoints for existing integrations

## Configuration

Set your API keys in `.env`:

\`\`\`env
POLYGON_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
\`\`\`

## Architecture

\`\`\`
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── core/
│   └── http_client.py     # HTTP client with retry logic
├── services/              # External API services
│   ├── yahoo_finance_service.py
│   ├── polygon_service.py
│   └── sec_service.py
├── models/                # Pydantic models
│   ├── stock_models.py
│   └── portfolio_models.py
├── routers/               # API route handlers
│   ├── stock_router.py
│   └── portfolio_router.py
├── portfolio/             # Portfolio management
│   └── portfolio_manager.py
└── static/                # Frontend assets
    ├── index.html
    ├── css/terminal.css
    └── js/terminal.js
\`\`\`

## Development

\`\`\`bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# http://localhost:8000/docs
\`\`\`

## License

MIT License
\`\`\`

Perfect! Now you have the complete Stock Terminal codebase with:

## 🚀 **Complete Features:**

1. **Python FastAPI Backend** with robust error handling and retry logic
2. **Router Architecture** with comprehensive API endpoints
3. **Multiple Data Sources** (Yahoo Finance, Polygon.io, SEC) with fallbacks
4. **Portfolio Management** with real-time P&L calculations
5. **Bloomberg-style Terminal** with movable/resizable windows
6. **Docker Support** for easy deployment
7. **Comprehensive Documentation** and setup instructions

## 📁 **File Structure:**

- **Backend**: Python FastAPI with modular services and routers
- **Frontend**: Vanilla JavaScript with terminal aesthetics
- **Configuration**: Environment-based settings
- **Docker**: Ready for containerized deployment
- **Documentation**: Complete setup and usage guide

You can now download all files and run the terminal with:

\`\`\`bash
docker-compose up
\`\`\`

The terminal will be available at `http://localhost:8000` with your original Bloomberg-style interface and all the enhanced backend functionality!
