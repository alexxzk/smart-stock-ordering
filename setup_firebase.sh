#!/bin/bash

echo "🔥 Firebase Setup for Smart Stock Ordering 🔥"
echo "=============================================="
echo ""

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

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Detected macOS system"
else
    print_warning "This script is optimized for macOS. Some commands may need adjustment for other systems."
fi

echo ""
print_status "Step 1: Prerequisites Check"
echo "--------------------------------"

# Check if Node.js is installed
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js is installed: $NODE_VERSION"
else
    print_error "Node.js is not installed. Please install Node.js first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python is installed: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed. Please install Python 3 first."
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

# Check if git is installed
if command -v git &> /dev/null; then
    print_success "Git is installed"
else
    print_warning "Git is not installed. Some features may not work properly."
fi

echo ""
print_status "Step 2: Firebase Project Setup"
echo "-----------------------------------"

echo ""
echo "📋 Manual Steps Required:"
echo "1. Go to https://console.firebase.google.com/"
echo "2. Click 'Create a project'"
echo "3. Name your project (e.g., 'smart-stock-ordering')"
echo "4. Enable Google Analytics (recommended)"
echo "5. Choose analytics account or create new one"
echo ""

read -p "Have you created your Firebase project? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Please create your Firebase project first, then run this script again."
    exit 1
fi

echo ""
print_status "Step 3: Enable Firebase Services"
echo "-------------------------------------"

echo ""
echo "📋 Enable these services in Firebase Console:"
echo "1. Authentication → Get Started → Enable Email/Password"
echo "2. Firestore Database → Create Database → Start in test mode"
echo "3. Storage → Get Started (optional, for file uploads)"
echo ""

read -p "Have you enabled the required services? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Please enable the required services first, then run this script again."
    exit 1
fi

echo ""
print_status "Step 4: Get Firebase Configuration"
echo "---------------------------------------"

echo ""
echo "📋 Backend Configuration (Service Account):"
echo "1. Go to Project Settings → Service Accounts"
echo "2. Click 'Generate new private key'"
echo "3. Download the JSON file"
echo "4. Copy the contents to: backend/config/firebase_config.json"
echo ""

read -p "Have you downloaded the service account key? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Please download the service account key first."
    exit 1
fi

echo ""
echo "📋 Frontend Configuration:"
echo "1. Go to Project Settings → General"
echo "2. Scroll to 'Your apps' section"
echo "3. Click the web icon (</>) to add a web app"
echo "4. Name it 'Smart Stock Frontend'"
echo "5. Copy the config object"
echo "6. Update: frontend/src/config/firebase.ts"
echo ""

read -p "Have you added the web app and copied the config? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Please add the web app and copy the config first."
    exit 1
fi

echo ""
print_status "Step 5: Environment Variables Setup"
echo "----------------------------------------"

# Create backend .env file
if [ ! -f "backend/.env" ]; then
    print_status "Creating backend .env file..."
    cp backend/env.example backend/.env
    print_success "Created backend/.env"
    print_warning "Please update backend/.env with your Firebase configuration"
else
    print_success "Backend .env file already exists"
fi

# Create frontend .env file
if [ ! -f "frontend/.env" ]; then
    print_status "Creating frontend .env file..."
    cp frontend/env.example frontend/.env
    print_success "Created frontend/.env"
    print_warning "Please update frontend/.env with your Firebase configuration"
else
    print_success "Frontend .env file already exists"
fi

echo ""
print_status "Step 6: Install Dependencies"
echo "--------------------------------"

# Install backend dependencies
print_status "Installing backend dependencies..."
cd backend
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "Backend dependencies installed"
    else
        print_error "Failed to install backend dependencies"
        exit 1
    fi
else
    print_warning "requirements.txt not found in backend directory"
fi
cd ..

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
if [ -f "package.json" ]; then
    npm install
    if [ $? -eq 0 ]; then
        print_success "Frontend dependencies installed"
    else
        print_error "Failed to install frontend dependencies"
        exit 1
    fi
else
    print_warning "package.json not found in frontend directory"
fi
cd ..

echo ""
print_status "Step 7: Deploy Firestore Security Rules"
echo "---------------------------------------------"

echo ""
echo "📋 Deploy Firestore Security Rules:"
echo "1. Install Firebase CLI: npm install -g firebase-tools"
echo "2. Login: firebase login"
echo "3. Initialize: firebase init firestore"
echo "4. Deploy rules: firebase deploy --only firestore:rules"
echo ""

read -p "Do you want to install Firebase CLI and deploy rules now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing Firebase CLI..."
    npm install -g firebase-tools
    
    print_status "Logging into Firebase..."
    firebase login
    
    print_status "Initializing Firebase project..."
    firebase init firestore
    
    print_status "Deploying Firestore security rules..."
    firebase deploy --only firestore:rules
fi

echo ""
print_status "Step 8: Test the Setup"
echo "----------------------------"

echo ""
echo "📋 Testing Steps:"
echo "1. Start backend: cd backend && python -m uvicorn app.main:app --reload --port 8000"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Test Firebase connection: http://localhost:8000/test-firestore"
echo "4. Test frontend: http://localhost:5173"
echo ""

read -p "Do you want to test the setup now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting backend server..."
    cd backend
    python3 -m uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    print_status "Starting frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    print_success "Servers started!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:5173"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop the servers"
    
    # Wait for user to stop
    wait
fi

echo ""
print_success "🎉 Firebase setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Update your Firebase configuration files"
echo "2. Test the application"
echo "3. Review the privacy compliance features"
echo "4. Set up production environment"
echo ""
echo "📚 Documentation:"
echo "- Firebase Console: https://console.firebase.google.com/"
echo "- Firestore Rules: firestore.rules"
echo "- Privacy Policy: frontend/src/components/PrivacyPolicy.tsx"
echo "- Security Guide: FIREBASE_SECURITY_GUIDE.md"
echo ""
print_success "Happy coding! 🚀" 