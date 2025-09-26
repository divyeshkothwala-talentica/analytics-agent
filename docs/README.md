# Logistics Analytics Q&A Tool - User Guide

## Overview

The Logistics Analytics Q&A Tool is an AI-powered system that allows you to ask questions about your logistics data in natural language and get intelligent insights and recommendations.

## Quick Start

### 1. CLI Interface (Command Line)

```bash
# Navigate to the project directory
cd analytics-agent

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the CLI interface
python src/cli/main.py
```

### 2. Web Interface

```bash
# Start the web server
python src/web/app.py

# Open your browser to http://localhost:5000
```

### 3. Demo Script

```bash
# Run automated demo
python src/demo/demo_script.py

# Run specific scenario
python src/demo/demo_script.py --scenario "City Delay Analysis"

# Run non-interactive demo
python src/demo/demo_script.py --non-interactive
```

## Sample Queries

### City Delay Analysis
- "Why were deliveries delayed in Mumbai yesterday?"
- "What caused delivery delays in Delhi last week?"
- "Analyze delivery delays in Bangalore on Monday"

### Client Failure Analysis
- "Why did Client ABC's orders fail in the past week?"
- "What are the main issues with Client XYZ's deliveries?"
- "Analyze failure patterns for Client 123 this month"

### Warehouse Performance
- "Top reasons for delivery failures linked to Warehouse B in August?"
- "Analyze Warehouse A's performance this quarter"
- "What's causing issues at Warehouse C?"

### City Comparison
- "Compare delivery failure causes between Mumbai and Delhi last month"
- "How do Chennai and Bangalore delivery rates compare?"
- "Analyze performance differences between Pune and Hyderabad"

### Seasonal Analysis
- "Likely causes of delivery failures during festival period"
- "How does monsoon season affect delivery performance?"
- "Analyze delivery patterns during Diwali week"

### Capacity Planning
- "Impact of onboarding Client Y with 20,000 extra monthly orders?"
- "Can we handle 50% more orders in Mumbai?"
- "What's our capacity limit for next quarter?"

## Features

### Natural Language Processing
- Ask questions in plain English
- No need to learn query syntax
- Intelligent parsing of intent and context

### Real-time Analytics
- Process data from multiple collections
- Generate insights within seconds
- Correlate data across different sources

### Performance Monitoring
- Track query execution times
- Monitor system resource usage
- Cost tracking for AI API usage

### Multiple Interfaces
- Interactive CLI for power users
- Web interface for easy access
- Automated demo scripts for presentations

## Data Collections

The system analyzes data from these collections:

- **Orders**: Order details, status, delivery information
- **Fleet Logs**: Vehicle tracking, driver data, route information
- **Warehouse Logs**: Warehouse operations, processing times
- **Feedback**: Customer ratings and comments
- **External Factors**: Weather, traffic, events data

## Query Types Supported

### Analysis Queries ("Why", "What")
- Root cause analysis
- Pattern identification
- Trend analysis

### Comparison Queries ("Compare", "Versus")
- Performance comparisons
- Metric benchmarking
- Regional analysis

### Prediction Queries ("Impact", "Predict")
- Capacity planning
- Resource requirements
- Performance forecasting

### Trend Queries ("Show trends", "Over time")
- Historical analysis
- Seasonal patterns
- Performance evolution

## Tips for Better Results

### Be Specific
✅ Good: "Why were deliveries delayed in Mumbai yesterday?"
❌ Avoid: "Show me delays"

### Include Context
✅ Good: "Compare Client A and Client B performance last month"
❌ Avoid: "Compare clients"

### Use Time Ranges
✅ Good: "Analyze warehouse efficiency in Q2"
❌ Avoid: "Analyze warehouse"

### Mention Metrics
✅ Good: "Top 5 failure reasons for Warehouse B"
❌ Avoid: "Tell me about Warehouse B"

## CLI Commands

### Basic Commands
- `help` - Show available commands
- `examples` - Display sample queries
- `stats` - Show performance statistics
- `history` - View query history
- `clear` - Clear screen
- `quit` - Exit application

### Configuration
- `debug` - Toggle debug mode
- `suggest` - Toggle auto-suggestions

## Web Interface Features

### Home Page
- Query input form
- Sample query suggestions
- Recent query history

### Examples Page
- Categorized sample queries
- Query tips and best practices

### History Page
- Session query history
- Performance statistics
- Re-run previous queries

### Stats Page
- Real-time performance metrics
- System resource usage
- AI API usage and costs

## Performance Optimization

### Query Performance
- Queries typically complete in 2-15 seconds
- Complex correlations may take longer
- Results are cached for faster repeated queries

### System Requirements
- Minimum 4GB RAM recommended
- MongoDB database connection required
- OpenAI API key required

### Cost Management
- Monitor AI API usage in stats
- Typical cost: $0.01-0.05 per query
- Use caching to reduce repeated API calls

## Troubleshooting

### Common Issues

**"System not initialized"**
- Check MongoDB connection
- Verify OpenAI API key in .env file
- Ensure all dependencies are installed

**"Query timeout"**
- Try a more specific query
- Check database performance
- Reduce query complexity

**"No results found"**
- Verify data exists for the time period
- Check spelling of cities/clients
- Try broader search criteria

**High API costs**
- Enable query caching
- Use more specific queries
- Monitor usage in stats page

### Getting Help

1. Check the examples page for query patterns
2. Use the `help` command in CLI
3. Review the troubleshooting section
4. Check system logs for detailed errors

## Advanced Usage

### Custom Scenarios
Create custom demo scenarios in `src/demo/use_cases.py`

### Data Generation
Generate test data using `src/demo/data_generator.py`

### Performance Monitoring
Export performance metrics using the monitor API

### API Integration
Use the Flask API endpoints for custom integrations

## Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017/logistics_analytics

# Optional
OPENAI_MODEL=gpt-4
FLASK_DEBUG=False
FLASK_SECRET_KEY=your_secret_key
```

### Database Setup
Ensure MongoDB is running and accessible with the collections loaded from the data pipeline.

## Support

For technical issues or questions:
1. Check this documentation
2. Review the code comments
3. Check the GitHub repository for updates
4. Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: {{ datetime.now().strftime('%Y-%m-%d') }}  
**License**: MIT
