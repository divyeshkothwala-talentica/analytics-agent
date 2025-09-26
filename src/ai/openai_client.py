"""
OpenAI API client for natural language query processing
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API client with retry logic and error handling"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.max_retries = int(os.getenv('OPENAI_MAX_RETRIES', '3'))
        self.retry_delay = float(os.getenv('OPENAI_RETRY_DELAY', '1.0'))
        
        # Token usage tracking
        self.total_tokens_used = 0
        self.total_cost = 0.0
        
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate approximate cost based on token usage
        
        Args:
            usage: Token usage dict with prompt_tokens and completion_tokens
            
        Returns:
            Estimated cost in USD
        """
        # GPT-4 pricing (as of 2024)
        prompt_cost_per_1k = 0.03
        completion_cost_per_1k = 0.06
        
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        
        cost = (prompt_tokens / 1000 * prompt_cost_per_1k + 
                completion_tokens / 1000 * completion_cost_per_1k)
        
        return cost
    
    def _make_request_with_retry(self, messages: List[Dict[str, str]], 
                                temperature: float = 0.1,
                                max_tokens: Optional[int] = None) -> ChatCompletion:
        """Make OpenAI API request with retry logic
        
        Args:
            messages: List of message dicts for the conversation
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            ChatCompletion response
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Track usage
                if response.usage:
                    usage_dict = {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                    
                    self.total_tokens_used += usage_dict['total_tokens']
                    cost = self._calculate_cost(usage_dict)
                    self.total_cost += cost
                    
                    logger.debug(f"API call - Tokens: {usage_dict['total_tokens']}, "
                               f"Cost: ${cost:.4f}, Total cost: ${self.total_cost:.4f}")
                
                return response
                
            except Exception as e:
                last_exception = e
                logger.warning(f"OpenAI API request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        logger.error(f"All OpenAI API retries failed. Last error: {last_exception}")
        raise last_exception
    
    def parse_natural_language_query(self, user_query: str, 
                                   available_collections: List[str]) -> Dict[str, Any]:
        """Parse natural language query to extract structured information
        
        Args:
            user_query: User's natural language question
            available_collections: List of available MongoDB collections
            
        Returns:
            Dict with parsed query components
        """
        system_prompt = f"""You are an expert at parsing natural language queries for logistics and supply chain analytics.

Available data collections: {', '.join(available_collections)}

Parse the user's query and extract the following information in JSON format:
{{
    "intent": "analysis_type (why, compare, predict, trend, top_reasons, correlation)",
    "time_range": {{
        "type": "relative/absolute/none",
        "value": "yesterday/last_week/specific_date/etc",
        "start_date": "YYYY-MM-DD or null",
        "end_date": "YYYY-MM-DD or null"
    }},
    "location_filters": ["city_name", "warehouse_id", "route", etc],
    "entity_focus": {{
        "type": "client/driver/order/warehouse/general",
        "id": "specific_id or null",
        "name": "specific_name or null"
    }},
    "metrics": ["delays", "failures", "cancellations", "ratings", "efficiency", etc],
    "collections_needed": ["orders", "fleet_logs", etc],
    "filters": {{
        "status": ["failed", "delayed", etc],
        "priority": ["high", "urgent", etc],
        "other": {{}}
    }},
    "aggregation_type": "count/average/sum/group_by/correlation",
    "confidence": 0.0-1.0
}}

Focus on extracting actionable information that can be converted to MongoDB queries."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Parse this query: {user_query}"}
        ]
        
        try:
            response = self._make_request_with_retry(messages, temperature=0.1)
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            import json
            parsed_data = json.loads(content)
            
            logger.info(f"Successfully parsed query: {user_query}")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {content}")
            raise ValueError(f"Invalid JSON response from OpenAI: {e}")
        except Exception as e:
            logger.error(f"Error parsing natural language query: {e}")
            raise
    
    def generate_mongodb_query(self, parsed_query: Dict[str, Any], 
                              collection_schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate MongoDB aggregation pipeline from parsed query
        
        Args:
            parsed_query: Parsed query components from parse_natural_language_query
            collection_schemas: Schema information for collections
            
        Returns:
            MongoDB aggregation pipeline as list of stage dicts
        """
        system_prompt = f"""You are an expert MongoDB query generator for logistics analytics.

Collection schemas:
{collection_schemas}

Generate a MongoDB aggregation pipeline based on the parsed query. Return ONLY a valid JSON array of aggregation stages.

Key guidelines:
1. Use $match for filtering
2. Use $lookup for joining collections
3. Use $group for aggregations
4. Use $sort for ordering results
5. Use $limit for performance
6. Handle date ranges properly with $gte and $lte
7. Use $project to shape final output
8. Consider performance - add $match early in pipeline

Example pipeline structure:
[
    {{"$match": {{"field": "value"}}}},
    {{"$lookup": {{"from": "collection", "localField": "field", "foreignField": "field", "as": "joined_data"}}}},
    {{"$group": {{"_id": "$field", "count": {{"$sum": 1}}}}}},
    {{"$sort": {{"count": -1}}}},
    {{"$limit": 100}}
]"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate MongoDB pipeline for: {parsed_query}"}
        ]
        
        try:
            response = self._make_request_with_retry(messages, temperature=0.1)
            content = response.choices[0].message.content.strip()
            
            # Clean up response - remove markdown code blocks if present
            if '```json' in content:
                # Extract JSON from markdown code blocks
                start_marker = content.find('```json') + 7
                end_marker = content.find('```', start_marker)
                if end_marker != -1:
                    content = content[start_marker:end_marker].strip()
            elif content.startswith('```'):
                # Handle generic code blocks
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
            
            # Remove any remaining markdown artifacts
            content = content.strip()
            
            # Parse JSON
            import json
            pipeline = json.loads(content)
            
            if not isinstance(pipeline, list):
                raise ValueError("Pipeline must be a list of aggregation stages")
            
            logger.info(f"Generated MongoDB pipeline with {len(pipeline)} stages")
            return pipeline
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse pipeline JSON: {e}")
            logger.error(f"Raw response: {content}")
            raise ValueError(f"Invalid JSON pipeline from OpenAI: {e}")
        except Exception as e:
            logger.error(f"Error generating MongoDB query: {e}")
            raise
    
    def explain_results(self, query: str, results: List[Dict[str, Any]], 
                       context: Dict[str, Any]) -> str:
        """Generate natural language explanation of query results
        
        Args:
            query: Original user query
            results: Query results from MongoDB
            context: Additional context about the analysis
            
        Returns:
            Natural language explanation of results
        """
        system_prompt = """You are an expert logistics analyst. Explain query results in clear, business-friendly language.

Guidelines:
1. Start with a direct answer to the user's question
2. Highlight key insights and patterns
3. Provide specific numbers and percentages
4. Suggest actionable recommendations when appropriate
5. Keep explanations concise but comprehensive
6. Use business terminology, not technical jargon"""

        # Limit results size for API call
        results_sample = results[:10] if len(results) > 10 else results
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
Original query: {query}
Results: {results_sample}
Context: {context}
Total results count: {len(results)}

Please explain these results in business terms.
"""}
        ]
        
        try:
            response = self._make_request_with_retry(messages, temperature=0.3, max_tokens=500)
            explanation = response.choices[0].message.content
            
            logger.info("Generated explanation for query results")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"Analysis completed with {len(results)} results. Unable to generate detailed explanation."
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics
        
        Returns:
            Dict with token usage and cost information
        """
        return {
            'total_tokens_used': self.total_tokens_used,
            'total_cost_usd': round(self.total_cost, 4),
            'model': self.model
        }
    
    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.total_tokens_used = 0
        self.total_cost = 0.0
        logger.info("Usage statistics reset")
