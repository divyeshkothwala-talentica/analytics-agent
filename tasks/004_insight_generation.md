# Task 004: Insight Generation & Human-Readable Output

## Objective
Transform raw MongoDB query results into human-readable insights with actionable recommendations using OpenAI GPT for narrative generation.

## Technical Requirements

### 1. Result Processor (`src/insights/processor.py`)
Process MongoDB aggregation results:
- **Statistical Analysis**: Calculate percentages, trends, comparisons
- **Pattern Detection**: Identify recurring issues, seasonal patterns
- **Anomaly Detection**: Flag unusual spikes or drops in metrics
- **Ranking**: Top failure reasons, worst performing routes/warehouses

### 2. Insight Templates (`src/insights/templates.py`)
Create structured templates for different analysis types:

#### Delay Analysis Template
```python
{
  "summary": "Primary delay causes and impact",
  "key_findings": [
    {
      "finding": "Traffic congestion caused 45% of delays",
      "impact": "Average delay: 2.3 hours",
      "affected_orders": 156
    }
  ],
  "trends": "Delays increased 23% compared to previous period",
  "recommendations": [
    "Reschedule deliveries to avoid peak traffic hours",
    "Consider alternative routes for high-congestion areas"
  ]
}
```

#### Client Analysis Template
```python
{
  "client_overview": "Client performance summary",
  "failure_breakdown": {
    "stockout": {"count": 12, "percentage": 40},
    "address_issues": {"count": 8, "percentage": 27},
    "weather_delays": {"count": 10, "percentage": 33}
  },
  "financial_impact": "₹45,670 in failed deliveries",
  "action_items": [
    "Improve inventory management for this client",
    "Verify delivery addresses before dispatch"
  ]
}
```

### 3. Narrative Generator (`src/insights/narrator.py`)
Use OpenAI GPT to generate human-readable explanations:

#### Prompt Engineering for Insights
```python
def generate_narrative(data, query_type):
    prompt = f"""
    You are a logistics analytics expert. Based on the following data analysis,
    provide a clear, actionable explanation for operations managers.
    
    Query: {query_type}
    Data: {data}
    
    Generate a response that includes:
    1. Executive Summary (2-3 sentences)
    2. Key Findings (bullet points)
    3. Root Cause Analysis
    4. Actionable Recommendations
    5. Expected Impact of Recommendations
    
    Use business language, avoid technical jargon.
    """
```

### 4. Visualization Data Prep (`src/insights/visualizer.py`)
Prepare data for simple charts and graphs:
- **Time Series**: Delivery performance over time
- **Pie Charts**: Failure reason distribution
- **Bar Charts**: City/warehouse comparisons
- **Heatmaps**: Peak failure times/locations

### 5. Report Generator (`src/insights/reporter.py`)
Generate structured reports:
- **Executive Dashboard**: High-level KPIs and trends
- **Operational Reports**: Detailed analysis with drill-down
- **Comparative Analysis**: Period-over-period comparisons
- **Predictive Insights**: Based on historical patterns

### 6. Recommendation Engine (`src/insights/recommender.py`)
Generate actionable recommendations based on analysis:

#### Recommendation Categories
- **Operational**: Route optimization, scheduling changes
- **Resource**: Staffing adjustments, warehouse capacity
- **Process**: Address verification, inventory management
- **Strategic**: Client onboarding, service improvements

#### Sample Recommendations
```python
def generate_recommendations(analysis_results):
    recommendations = []
    
    if analysis_results['top_failure'] == 'traffic_congestion':
        recommendations.append({
            "category": "operational",
            "action": "Implement dynamic routing based on real-time traffic",
            "expected_impact": "Reduce delays by 30-40%",
            "implementation_effort": "Medium",
            "timeline": "2-3 weeks"
        })
    
    return recommendations
```

### 7. Output Formatters (`src/insights/formatters.py`)
Support multiple output formats:
- **JSON**: For API responses
- **Markdown**: For documentation
- **Plain Text**: For CLI output
- **HTML**: For web interface

## Deliverables
- ✅ Result processing and statistical analysis
- ✅ Structured insight templates
- ✅ OpenAI-powered narrative generation
- ✅ Visualization data preparation
- ✅ Comprehensive report generation
- ✅ Actionable recommendation engine
- ✅ Multiple output format support

## Success Criteria
- Generated insights are accurate and actionable
- Narrative explanations are clear and business-focused
- Recommendations are specific and implementable
- Output formats are consistent and professional
- Processing time < 10 seconds for complex reports

## Estimated Time: 5-6 hours