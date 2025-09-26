# Analytics Agent - Logistics Q&A Tool

An intelligent analytics system that processes logistics data and provides natural language query capabilities using AI.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas)
- OpenAI API key

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd analytics-agent
   ```

2. **Run the setup script:**
   ```bash
   python setup.py
   ```

3. **Activate the virtual environment:**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Configure environment variables:**
   ```bash
   # Copy template and edit with your settings
   cp .env.template .env
   # Edit .env file with your OpenAI API key and MongoDB settings
   ```

5. **Verify setup:**
   ```bash
   python test_setup.py
   ```

### Manual Setup (Alternative)

If the setup script doesn't work, follow these manual steps:

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

## 📁 Project Structure

```
analytics-agent/
├── src/                    # Source code
│   ├── config/            # Configuration modules
│   │   └── database.py    # MongoDB connection
│   ├── models/            # Data models and schemas
│   │   └── schemas.py     # MongoDB collection schemas
│   └── utils/             # Utility functions
│       └── logger.py      # Logging configuration
├── data/                  # Data files (CSV)
├── logs/                  # Application logs
├── tasks/                 # Project documentation
├── .env                   # Environment variables
├── .env.template          # Environment template
├── requirements.txt       # Python dependencies
├── setup.py              # Setup script
└── test_setup.py         # Setup verification
```

## 🗄️ Database Collections

The system uses MongoDB with the following collections:

- **orders** - Central order data
- **warehouse_logs** - Warehouse operations
- **fleet_logs** - Delivery operations  
- **external_factors** - Weather, traffic, events
- **feedback** - Customer feedback
- **clients** - Client master data
- **warehouses** - Warehouse master data
- **drivers** - Driver master data

## 🔧 Configuration

### Environment Variables (.env)

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=logistics_analytics

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/analytics_agent.log

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
```

### MongoDB Setup Options

**Option 1: Local MongoDB**
```bash
# Install MongoDB locally
brew install mongodb/brew/mongodb-community  # macOS
# or follow MongoDB installation guide for your OS
```

**Option 2: MongoDB Atlas (Cloud)**
```bash
# Update .env with Atlas connection string:
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

## 🧪 Testing

Run the setup verification:
```bash
python test_setup.py
```

This will test:
- ✅ Package imports
- ✅ Environment variables
- ✅ Logging system
- ✅ Database connection
- ✅ Data models
- ✅ Project structure

## 📊 Data Pipeline

After setup, load the CSV data:
```bash
python -m src.data_pipeline
```

## 🔍 Usage Examples

```python
# Database connection
from src.config.database import get_db, get_collection

# Get database
db = get_db()

# Get specific collection
orders = get_collection('orders')

# Logging
from src.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Application started")

# Data models
from src.models.schemas import Order, SchemaValidator
```

## 📋 Development Tasks

See the `tasks/` directory for detailed implementation tasks:

1. [Foundation Setup](tasks/001_foundation_setup.md) ✅
2. [Data Pipeline](tasks/002_data_pipeline.md)
3. [AI Query Engine](tasks/003_ai_query_engine.md)
4. [Insight Generation](tasks/004_insight_generation.md)
5. [Demo Interface](tasks/005_demo_interface.md)

## 🐛 Troubleshooting

### Common Issues

**MongoDB Connection Failed:**
- Ensure MongoDB is running: `brew services start mongodb/brew/mongodb-community`
- Check connection string in `.env`
- For Atlas, verify network access and credentials

**Import Errors:**
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**OpenAI API Errors:**
- Verify API key in `.env`
- Check API key permissions and billing

### Getting Help

1. Run `python test_setup.py` for diagnostics
2. Check logs in `logs/analytics_agent.log`
3. Review task documentation in `tasks/`

## 📄 License

This project is for educational and demonstration purposes.