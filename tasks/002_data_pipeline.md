# Task 002: Data Pipeline & MongoDB Schema Implementation

## Objective
Design and implement data ingestion pipeline to load CSV data into MongoDB with optimized schema for analytics queries.

## Technical Requirements

### 1. Schema Design
Design MongoDB collections with proper indexing and relationships:

#### Orders Collection
```json
{
  "_id": ObjectId,
  "order_id": Number (indexed),
  "client_id": Number (indexed),
  "customer_info": {
    "name": String,
    "phone": String,
    "address": {
      "line1": String,
      "line2": String,
      "city": String (indexed),
      "state": String (indexed),
      "pincode": String
    }
  },
  "dates": {
    "order_date": Date,
    "promised_delivery": Date,
    "actual_delivery": Date
  },
  "status": String (indexed),
  "payment_mode": String,
  "amount": Number,
  "failure_reason": String (indexed),
  "created_at": Date
}
```

#### Warehouse Logs Collection
```json
{
  "_id": ObjectId,
  "log_id": Number,
  "order_id": Number (indexed),
  "warehouse_id": Number (indexed),
  "timing": {
    "picking_start": Date,
    "picking_end": Date,
    "dispatch_time": Date
  },
  "processing_time_minutes": Number,
  "notes": String,
  "issues": [String] // Extracted from notes
}
```

#### Fleet Logs Collection
```json
{
  "_id": ObjectId,
  "fleet_log_id": Number,
  "order_id": Number (indexed),
  "driver_id": Number (indexed),
  "vehicle_number": String,
  "route_code": String,
  "gps_delay_notes": String,
  "timing": {
    "departure": Date,
    "arrival": Date
  },
  "delivery_time_hours": Number,
  "delay_reasons": [String], // Extracted from notes
  "created_at": Date
}
```

### 2. Data Ingestion Pipeline
Create Python modules for:

#### CSV Reader (`src/data/csv_reader.py`)
- Read and validate CSV files
- Handle data type conversions
- Clean and normalize data
- Extract structured information from unstructured fields (notes, feedback)

#### Data Transformer (`src/data/transformer.py`)
- Convert CSV rows to MongoDB documents
- Calculate derived fields (processing times, delays)
- Extract keywords from text fields
- Standardize date formats

#### MongoDB Loader (`src/data/loader.py`)
- Batch insert documents to MongoDB
- Create indexes for query optimization
- Handle duplicate data
- Validate data integrity

### 3. Data Correlation Engine
Create correlation mappings:
- Link orders with warehouse operations
- Connect fleet logs with external factors
- Associate customer feedback with delivery issues
- Time-based correlation for delay analysis

### 4. Data Validation & Quality Checks
- Verify data completeness
- Check referential integrity
- Validate date sequences
- Identify data anomalies

## Deliverables
- ✅ MongoDB schema with proper indexing
- ✅ CSV to MongoDB data pipeline
- ✅ Data transformation and cleaning logic
- ✅ Correlation mapping between collections
- ✅ Data validation and quality checks
- ✅ Sample data loaded and verified

## Success Criteria
- All CSV data successfully loaded into MongoDB
- Indexes created for optimal query performance
- Data relationships properly established
- Query response time < 2 seconds for basic aggregations
- Data integrity validation passes

## Estimated Time: 4-5 hours