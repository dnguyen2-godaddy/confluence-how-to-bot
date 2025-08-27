#!/bin/bash

# Dashboard Analyzer Runner Script
# This script activates the virtual environment and runs the dashboard analyzer
# Provides a seamless, single-process AI-powered dashboard documentation experience

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment 'venv' not found!"
        print_status "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created successfully!"
    fi
}

# Function to check if requirements are installed
check_requirements() {
    if [ ! -f "venv/bin/pip" ]; then
        print_error "Virtual environment is corrupted or incomplete!"
        exit 1
    fi
    
    # Check if key packages are installed
    if ! venv/bin/python -c "import boto3, requests, markdown" 2>/dev/null; then
        print_warning "Some required packages are missing. Installing requirements..."
        venv/bin/pip install -r requirements.txt
        print_success "Requirements installed successfully!"
    fi
}

# Function to check AWS credentials
check_aws_credentials() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Please ensure you have configured your AWS credentials."
        print_status "You can copy env.example to .env and configure your settings."
    else
        print_success "Environment configuration found."
    fi
}

# Main execution function
main() {
    echo "🚀 QuickSight Dashboard Image Analyzer"
    echo "======================================"
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "dashboard_analyzer.py" ]; then
        print_error "dashboard_analyzer.py not found in current directory!"
        print_status "Please run this script from the project root directory."
        exit 1
    fi
    
    print_status "Checking virtual environment..."
    check_venv
    
    print_status "Checking requirements..."
    check_requirements
    
    print_status "Checking AWS configuration..."
    check_aws_credentials
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Starting Dashboard Analyzer..."
    echo ""
    
    # Run the dashboard analyzer
    python3 dashboard_analyzer.py
    
    # Check exit status
    if [ $? -eq 0 ]; then
        print_success "Dashboard Analyzer completed successfully!"
    else
        print_error "Dashboard Analyzer encountered an error!"
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --version  Show version information"
    echo "  --check-only   Only check environment without running the program"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run the dashboard analyzer"
    echo "  $0 --check-only       # Check environment only"
    echo "  $0 --help            # Show this help"
}

# Function to check environment only
check_environment() {
    echo "🔍 Environment Check Only"
    echo "========================"
    echo ""
    
    print_status "Checking virtual environment..."
    check_venv
    
    print_status "Checking requirements..."
    check_requirements
    
    print_status "Checking AWS configuration..."
    check_aws_credentials
    
    print_success "Environment check completed successfully!"
    print_status "You can now run: $0"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -v|--version)
        echo "Dashboard Analyzer Runner v1.0.0"
        exit 0
        ;;
    --check-only)
        check_environment
        exit 0
        ;;
    "")
        # No arguments, run normally
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
