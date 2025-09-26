# Task 003: AI Query Engine & Natural Language Processing

## Objective
Implement OpenAI GPT-powered query engine that converts natural language questions into MongoDB aggregation queries and correlates data across multiple collections.

## Technical Requirements

### 1. OpenAI Integration (`src/ai/openai_client.py`)
- Configure OpenAI API client
- Design prompt templates for query generation
- Implement retry logic and error handling
- Manage token usage and costs

### 2. Query Parser (`src/ai/query_parser.py`)
Analyze natural language questions to extract:
- **Time Range**: "yesterday", "last week", "August", "festival period"
- **Location Filters**: "city X", "warehouse B", "route specific"
- **Entity Focus**: "client X", "driver Y", "specific order"
- **Analysis Type**: "why", "compare", "predict", "top reasons"
- **Metrics**: "delays", "failures", "cancellations", "ratings"

### 3. MongoDB Query Generator (`src/ai/query_generator.py`)
Convert parsed queries into MongoDB aggregation pipelines:

#### Sample Query Patterns:
```python
# Pattern 1: Time-based failure analysis
{
  "$match": {
    "dates.order_date": {"$gte": start_date, "$lte": end_date},
    "status": "Failed"
  }
}

# Pattern 2: Cross-collection correlation
{
  "$lookup": {
    "from": "external_factors",
    "localField": "order_id",
    "foreignField": "order_id",
    "as": "external_data"
  }
}

# Pattern 3: Aggregation with grouping
{
  "$group": {
    "_id": "$failure_reason",
    "count": {"$sum": 1},
    "avg_amount": {"$avg": "$amount"}
  }
}
```

### 4. Data Correlation Engine (`src/ai/correlator.py`)
Implement correlation logic for:
- **Temporal Correlations**: Link delivery delays with weather/traffic
- **Geographical Correlations**: City-specific failure patterns
- **Operational Correlations**: Warehouse efficiency vs delivery success
- **Customer Correlations**: Feedback sentiment vs delivery performance

### 5. Query Optimization (`src/ai/optimizer.py`)
- Cache frequently used aggregations
- Optimize query execution order
- Implement query result pagination
- Monitor query performance

### 6. Sample Query Handlers
Implement handlers for the 6 use cases:

#### Use Case 1: "Why were deliveries delayed in city X yesterday?"
```python
def analyze_city_delays(city, date):
    # Aggregate orders by city and date
    # Join with fleet_logs for delay reasons
    # Join with external_factors for context
    # Return structured analysis
```

#### Use Case 2: "Why did Client X's orders fail in the past week?"
```python
def analyze_client_failures(client_id, days=7):
    # Filter orders by client and timeframe
    # Analyze failure reasons
    # Correlate with warehouse and delivery data
    # Return client-specific insights
```

## Deliverables
- ✅ OpenAI API integration with proper error handling
- ✅ Natural language query parser
- ✅ MongoDB query generation engine
- ✅ Data correlation algorithms
- ✅ Query optimization and caching
- ✅ Handlers for all 6 sample use cases

## Success Criteria
- Natural language queries correctly parsed (>90% accuracy)
- Generated MongoDB queries execute successfully
- Query response time < 5 seconds for complex correlations
- Correlation accuracy validated against sample data
- All 6 use cases return meaningful results

## Estimated Time: 6-8 hours