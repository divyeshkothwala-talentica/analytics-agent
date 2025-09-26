# Analytics Agent - Technical Tasks Overview

## Project Summary
Building a Q&A tool with AI to analyze delivery failures and delays in logistics operations using natural language queries.

## Technology Stack
- **Backend**: Python 3.8+
- **Database**: MongoDB
- **AI/ML**: OpenAI GPT API
- **Interface**: CLI + Optional Flask Web App
- **Data Processing**: Pandas, PyMongo

## Task Execution Order

### 🏗️ [Task 001: Foundation Setup](./001_foundation_setup.md)
**Duration**: 2-3 hours  
**Dependencies**: None  
**Deliverables**: Environment setup, MongoDB configuration, project structure

### 📊 [Task 002: Data Pipeline](./002_data_pipeline.md)
**Duration**: 4-5 hours  
**Dependencies**: Task 001  
**Deliverables**: CSV to MongoDB ingestion, schema design, data correlation

### 🤖 [Task 003: AI Query Engine](./003_ai_query_engine.md)
**Duration**: 6-8 hours  
**Dependencies**: Task 002  
**Deliverables**: Natural language processing, MongoDB query generation, OpenAI integration

### 💡 [Task 004: Insight Generation](./004_insight_generation.md)
**Duration**: 5-6 hours  
**Dependencies**: Task 003  
**Deliverables**: Result processing, narrative generation, actionable recommendations

### 🖥️ [Task 005: Demo Interface](./005_demo_interface.md)
**Duration**: 4-5 hours  
**Dependencies**: Task 004  
**Deliverables**: CLI/Web interface, use case implementations, demo scenarios

## Total Timeline
**Estimated Duration**: 21-27 hours (3-4 working days)

## Sample Use Cases to Implement
1. Why were deliveries delayed in city X yesterday?
2. Why did Client X's orders fail in the past week?
3. Explain the top reasons for delivery failures linked to Warehouse B in August?
4. Compare delivery failure causes between City A and City B last month?
5. What are the likely causes of delivery failures during the festival period?
6. Impact analysis of onboarding Client Y with 20,000 extra monthly orders?

## Key Success Metrics
- ✅ Natural language queries processed accurately (>90%)
- ✅ Query response time < 15 seconds
- ✅ All 6 use cases implemented and working
- ✅ MongoDB queries optimized for performance
- ✅ Actionable insights generated with recommendations
- ✅ Demo runs smoothly without errors

## Data Sources
- `orders.csv` - Central order data (14,939 records)
- `warehouse_logs.csv` - Warehouse operations (10,001 records)
- `fleet_logs.csv` - Delivery operations (10,001 records)
- `external_factors.csv` - Weather, traffic, events (10,001 records)
- `feedback.csv` - Customer feedback (10,001 records)
- `clients.csv` - Client master data (749 records)
- `warehouses.csv` - Warehouse master data (51 records)
- `drivers.csv` - Driver master data (2,001 records)

## Architecture Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CSV Files     │───▶│   Data Pipeline  │───▶│    MongoDB      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│ User Interface  │◀───│  Insight Engine  │◀────────────┘
│   (CLI/Web)     │    │   (OpenAI GPT)   │
└─────────────────┘    └──────────────────┘
```

## Getting Started
1. Execute tasks in numerical order (001 → 005)
2. Each task has detailed technical requirements and success criteria
3. Validate deliverables before moving to next task
4. Test integration points between tasks

## Notes
- This is a POC-grade implementation
- Focus on functionality over production-ready features
- Optimize for demo effectiveness and clear results
- Document any assumptions or limitations encountered