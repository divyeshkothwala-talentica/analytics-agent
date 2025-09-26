#!/usr/bin/env python3
"""
Interactive CLI for the Logistics Analytics Q&A Tool
"""

import sys
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai.query_engine import AIQueryEngine
from src.demo.monitor import PerformanceMonitor
from src.demo.use_cases import UseCaseHandler
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger('cli', level=logging.INFO)


class AnalyticsCLI:
    """Interactive CLI for analytics queries"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.query_engine = None
        self.monitor = PerformanceMonitor()
        self.use_case_handler = UseCaseHandler()
        self.session_queries = []
        
        # CLI state
        self.running = True
        self.show_debug = False
        self.auto_suggest = True
        
        print("🔧 Initializing Analytics Engine...")
        try:
            self.query_engine = AIQueryEngine()
            print("✅ Analytics Engine ready!")
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            print("Please check your .env file and database connection.")
            sys.exit(1)
    
    def display_banner(self):
        """Display the welcome banner"""
        print("\n" + "=" * 80)
        print("🚚 LOGISTICS ANALYTICS Q&A TOOL")
        print("=" * 80)
        print("Ask questions about your logistics data in natural language!")
        print("\nCommands:")
        print("  help     - Show available commands")
        print("  examples - Show sample queries")
        print("  stats    - Show performance statistics")
        print("  debug    - Toggle debug mode")
        print("  clear    - Clear screen")
        print("  quit     - Exit the application")
        print("\n" + "-" * 80)
    
    def display_help(self):
        """Display help information"""
        print("\n📖 HELP - Available Commands:")
        print("  help       - Show this help message")
        print("  examples   - Show sample queries you can try")
        print("  stats      - Show performance and usage statistics")
        print("  debug      - Toggle debug mode (shows technical details)")
        print("  suggest    - Toggle auto-suggestions")
        print("  history    - Show query history for this session")
        print("  clear      - Clear the screen")
        print("  quit/exit  - Exit the application")
        print("\n💡 Sample Question Types:")
        print("  • Why were deliveries delayed in [city] yesterday?")
        print("  • Compare delivery failures between [city1] and [city2]")
        print("  • What are the top reasons for warehouse failures?")
        print("  • Show delivery performance trends this month")
        print("  • Analyze customer satisfaction correlation")
    
    def display_examples(self):
        """Display example queries"""
        examples = self.use_case_handler.get_sample_queries()
        
        print("\n🎯 SAMPLE QUERIES - Try these examples:")
        print("-" * 50)
        
        for i, (category, queries) in enumerate(examples.items(), 1):
            print(f"\n{i}. {category.replace('_', ' ').title()}:")
            for query in queries[:3]:  # Show first 3 queries per category
                print(f"   • {query}")
        
        print("\n💡 Tip: You can modify these queries with your own cities, dates, or criteria!")
    
    def display_stats(self):
        """Display performance statistics"""
        if not self.query_engine:
            print("❌ Analytics engine not initialized")
            return
        
        stats = self.query_engine.get_performance_stats()
        monitor_stats = self.monitor.get_session_stats()
        
        print("\n📊 PERFORMANCE STATISTICS")
        print("-" * 40)
        
        # OpenAI Usage
        openai_stats = stats.get('openai_usage', {})
        print(f"🤖 AI Usage:")
        print(f"   Tokens used: {openai_stats.get('total_tokens_used', 0):,}")
        print(f"   Estimated cost: ${openai_stats.get('total_cost_usd', 0):.4f}")
        print(f"   Model: {openai_stats.get('model', 'unknown')}")
        
        # Query Performance
        optimizer_stats = stats.get('optimizer_stats', {})
        print(f"\n⚡ Query Performance:")
        print(f"   Cache hits: {optimizer_stats.get('cache_hits', 0)}")
        print(f"   Cache misses: {optimizer_stats.get('cache_misses', 0)}")
        print(f"   Avg query time: {optimizer_stats.get('avg_execution_time_ms', 0):.1f}ms")
        
        # Session Stats
        print(f"\n📈 Session Statistics:")
        print(f"   Queries processed: {len(self.session_queries)}")
        print(f"   Session duration: {monitor_stats.get('session_duration', 0):.1f}s")
        print(f"   Success rate: {monitor_stats.get('success_rate', 0):.1f}%")
        
        # Available Collections
        collections = stats.get('available_collections', [])
        print(f"\n💾 Available Data:")
        print(f"   Collections: {', '.join(collections)}")
    
    def display_history(self):
        """Display query history"""
        if not self.session_queries:
            print("\n📝 No queries in this session yet.")
            return
        
        print(f"\n📝 QUERY HISTORY ({len(self.session_queries)} queries)")
        print("-" * 50)
        
        for i, query_info in enumerate(self.session_queries[-10:], 1):  # Show last 10
            timestamp = query_info['timestamp'].strftime("%H:%M:%S")
            query = query_info['query'][:60] + "..." if len(query_info['query']) > 60 else query_info['query']
            status = "✅" if query_info['success'] else "❌"
            duration = query_info.get('duration', 0)
            
            print(f"{i:2d}. [{timestamp}] {status} {query} ({duration:.1f}s)")
    
    def suggest_queries(self, user_input: str) -> Optional[str]:
        """Suggest similar queries based on input"""
        if not self.auto_suggest or len(user_input) < 3:
            return None
        
        suggestions = self.use_case_handler.get_query_suggestions(user_input)
        if suggestions:
            print(f"\n💡 Did you mean: {suggestions[0]}")
            return suggestions[0]
        
        return None
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a user query and return results"""
        start_time = time.time()
        
        print(f"\n🔍 Analyzing your question...")
        print(f"📊 Querying data across collections...")
        print(f"🤖 Generating insights...")
        
        # Start monitoring
        self.monitor.start_query(user_query)
        
        try:
            # Process the query
            result = self.query_engine.process_natural_language_query(user_query)
            
            # End monitoring
            duration = time.time() - start_time
            self.monitor.end_query(result.get('success', False), duration)
            
            # Store in session history
            self.session_queries.append({
                'timestamp': datetime.now(),
                'query': user_query,
                'success': result.get('success', False),
                'duration': duration,
                'result_count': result.get('result_count', 0)
            })
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.monitor.end_query(False, duration)
            
            self.session_queries.append({
                'timestamp': datetime.now(),
                'query': user_query,
                'success': False,
                'duration': duration,
                'error': str(e)
            })
            
            return {
                'success': False,
                'error': str(e),
                'query': user_query
            }
    
    def display_results(self, result: Dict[str, Any]):
        """Display query results in a formatted way"""
        print("\n" + "=" * 60)
        print("📋 ANALYSIS RESULTS")
        print("=" * 60)
        
        if not result.get('success'):
            print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
            return
        
        # Executive Summary
        explanation = result.get('explanation', 'No explanation available')
        print(f"\n📊 Executive Summary:")
        print(f"{explanation}")
        
        # Key Metrics
        result_count = result.get('result_count', 0)
        processing_time = result.get('metadata', {}).get('processing_time_ms', 0)
        
        print(f"\n📈 Key Metrics:")
        print(f"• Results found: {result_count}")
        print(f"• Processing time: {processing_time:.1f}ms")
        
        # Show some raw data if in debug mode
        if self.show_debug and result.get('results'):
            print(f"\n🔧 Debug Information:")
            print(f"• Primary collection: {result.get('metadata', {}).get('primary_collection', 'unknown')}")
            print(f"• Pipeline stages: {len(result.get('metadata', {}).get('pipeline', []))}")
            
            # Show first few results
            results = result.get('results', [])
            if results:
                print(f"\n📄 Sample Results (first 3):")
                for i, item in enumerate(results[:3], 1):
                    print(f"{i}. {item}")
        
        # Correlations if available
        correlations = result.get('correlations')
        if correlations:
            print(f"\n🔗 Correlations Found:")
            if isinstance(correlations, dict):
                for key, value in correlations.items():
                    if isinstance(value, (list, dict)) and value:
                        print(f"• {key.replace('_', ' ').title()}: Available")
    
    def handle_command(self, command: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = command.lower().strip()
        
        if command in ['help', 'h']:
            self.display_help()
            return True
        
        elif command in ['examples', 'ex']:
            self.display_examples()
            return True
        
        elif command in ['stats', 'statistics']:
            self.display_stats()
            return True
        
        elif command in ['debug']:
            self.show_debug = not self.show_debug
            print(f"🔧 Debug mode: {'ON' if self.show_debug else 'OFF'}")
            return True
        
        elif command in ['suggest']:
            self.auto_suggest = not self.auto_suggest
            print(f"💡 Auto-suggestions: {'ON' if self.auto_suggest else 'OFF'}")
            return True
        
        elif command in ['history', 'hist']:
            self.display_history()
            return True
        
        elif command in ['clear', 'cls']:
            os.system('clear' if os.name == 'posix' else 'cls')
            self.display_banner()
            return True
        
        elif command in ['quit', 'exit', 'q']:
            self.running = False
            return True
        
        return False
    
    def run(self):
        """Main CLI loop"""
        self.display_banner()
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if self.handle_command(user_input):
                    continue
                
                # Suggest similar queries if enabled
                if self.auto_suggest:
                    self.suggest_queries(user_input)
                
                # Process the query
                result = self.process_query(user_input)
                
                # Display results
                self.display_results(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                if self.show_debug:
                    import traceback
                    traceback.print_exc()
        
        # Show session summary
        self.show_session_summary()
    
    def show_session_summary(self):
        """Show session summary before exit"""
        if self.session_queries:
            successful = sum(1 for q in self.session_queries if q['success'])
            total = len(self.session_queries)
            
            print(f"\n📊 Session Summary:")
            print(f"   Queries processed: {total}")
            print(f"   Success rate: {successful}/{total} ({successful/total*100:.1f}%)")
            
            if self.query_engine:
                stats = self.query_engine.get_performance_stats()
                openai_stats = stats.get('openai_usage', {})
                cost = openai_stats.get('total_cost_usd', 0)
                if cost > 0:
                    print(f"   Estimated cost: ${cost:.4f}")
        
        print("\n👋 Thank you for using the Logistics Analytics Tool!")


def main():
    """Main entry point"""
    try:
        cli = AnalyticsCLI()
        cli.run()
    except Exception as e:
        print(f"❌ Failed to start CLI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
