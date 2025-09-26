#!/bin/bash

# Logistics Analytics Q&A Tool - Demo Runner Script
# This script provides easy access to all demo interfaces

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

# Function to check if virtual environment is activated
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_color $YELLOW "⚠️  Virtual environment not detected. Activating..."
        if [[ -f "venv/bin/activate" ]]; then
            source venv/bin/activate
            print_color $GREEN "✅ Virtual environment activated"
        else
            print_color $RED "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
            exit 1
        fi
    else
        print_color $GREEN "✅ Virtual environment active: $VIRTUAL_ENV"
    fi
}

# Function to check dependencies
check_dependencies() {
    print_color $BLUE "🔍 Checking dependencies..."
    
    if ! python -c "import flask, openai, pymongo" 2>/dev/null; then
        print_color $YELLOW "⚠️  Installing missing dependencies..."
        pip install -r requirements.txt
    fi
    
    print_color $GREEN "✅ Dependencies verified"
}

# Function to show usage
show_usage() {
    print_color $BLUE "🚚 Logistics Analytics Q&A Tool - Demo Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Available Commands:"
    echo "  cli              Start interactive CLI interface"
    echo "  web              Start web interface (default port 5000)"
    echo "  demo             Run automated demo script"
    echo "  validate         Run comprehensive validation tests"
    echo "  generate-data    Generate demo data"
    echo "  pipeline         Run data pipeline"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 cli           # Start CLI interface"
    echo "  $0 web           # Start web server on port 5000"
    echo "  $0 demo          # Run full automated demo"
    echo "  $0 validate      # Run all validation tests"
    echo ""
}

# Function to run CLI
run_cli() {
    print_color $GREEN "🖥️  Starting CLI Interface..."
    python main.py cli
}

# Function to run web interface
run_web() {
    local port=${1:-5000}
    print_color $GREEN "🌐 Starting Web Interface on port $port..."
    print_color $BLUE "📱 Open your browser to: http://localhost:$port"
    
    if command -v open &> /dev/null; then
        # macOS
        sleep 2 && open "http://localhost:$port" &
    elif command -v xdg-open &> /dev/null; then
        # Linux
        sleep 2 && xdg-open "http://localhost:$port" &
    fi
    
    python main.py web --port $port
}

# Function to run demo
run_demo() {
    print_color $GREEN "🎬 Starting Automated Demo..."
    python main.py demo
}

# Function to run validation
run_validation() {
    print_color $GREEN "🧪 Running Validation Tests..."
    python test_demo_validation.py --export validation_results.json
    
    if [[ $? -eq 0 ]]; then
        print_color $GREEN "✅ All validation tests passed!"
        print_color $BLUE "📄 Results exported to validation_results.json"
    else
        print_color $RED "❌ Some validation tests failed. Check output above."
        exit 1
    fi
}

# Function to generate data
generate_data() {
    print_color $GREEN "📊 Generating Demo Data..."
    python main.py generate-data --output-dir demo_data
    print_color $GREEN "✅ Demo data generated in demo_data/ directory"
}

# Function to run pipeline
run_pipeline() {
    print_color $GREEN "⚙️  Running Data Pipeline..."
    python main.py pipeline
}

# Function to check system status
check_status() {
    print_color $BLUE "🔍 System Status Check..."
    
    # Check MongoDB
    if command -v mongod &> /dev/null; then
        if pgrep mongod > /dev/null; then
            print_color $GREEN "✅ MongoDB is running"
        else
            print_color $YELLOW "⚠️  MongoDB not running. Start with: mongod"
        fi
    else
        print_color $YELLOW "⚠️  MongoDB not installed"
    fi
    
    # Check .env file
    if [[ -f ".env" ]]; then
        print_color $GREEN "✅ .env file found"
        if grep -q "OPENAI_API_KEY" .env; then
            print_color $GREEN "✅ OpenAI API key configured"
        else
            print_color $YELLOW "⚠️  OpenAI API key not found in .env"
        fi
    else
        print_color $YELLOW "⚠️  .env file not found. Copy from env_template.txt"
    fi
    
    # Check data files
    if ls *.csv 1> /dev/null 2>&1; then
        csv_count=$(ls -1 *.csv | wc -l)
        print_color $GREEN "✅ Found $csv_count CSV data files"
    else
        print_color $YELLOW "⚠️  No CSV data files found. Run pipeline first."
    fi
}

# Main script logic
main() {
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Show header
    print_color $BLUE "🚚 Logistics Analytics Q&A Tool"
    print_color $BLUE "================================"
    
    # Check environment
    check_venv
    check_dependencies
    
    # Handle command
    case "${1:-help}" in
        "cli")
            run_cli
            ;;
        "web")
            run_web ${2:-5000}
            ;;
        "demo")
            run_demo
            ;;
        "validate")
            run_validation
            ;;
        "generate-data")
            generate_data
            ;;
        "pipeline")
            run_pipeline
            ;;
        "status")
            check_status
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function with all arguments
main "$@"
