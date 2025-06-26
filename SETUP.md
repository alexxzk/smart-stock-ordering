# 🚀 Smart Stock Ordering - Setup Guide

## Prerequisites

- **Node.js 18+** and **npm**
- **Python 3.11+** and **pip**
- **Firebase project** (for authentication and database)

## 🏗️ Project Structure

```
smart-stock-app/
├── backend/                 # FastAPI + ML backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── ml/             # Machine learning modules
│   │   └── models/         # Data models
│   ├── requirements.txt    # Python dependencies
│   └── config.env.example  # Environment variables
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/         # Page components
│   │   └── contexts/      # React contexts
│   ├── package.json       # Node dependencies
│   └── config.env.example # Environment variables
└── README.md
```

## 🔧 Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Go to Project Settings > Service Accounts
4. Generate a new private key (download JSON file)
5. Copy the values to `backend/config.env`:

```bash
cp backend/config.env.example backend/config.env
# Edit config.env with your Firebase credentials
```

### 3. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## 🎨 Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Firebase

1. In your Firebase project, go to Project Settings > General
2. Add a web app and copy the config
3. Copy the values to `frontend/config.env`:

```bash
cp frontend/config.env.example frontend/config.env
# Edit config.env with your Firebase web app credentials
```

### 3. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The app will be available at: http://localhost:5173

## 📊 Sample Data

### CSV Format for Sales Data

Create a CSV file with the following columns:

```csv
date,sales_amount,orders_count,menu_items_sold
2024-01-01,1200.0,45,"{""coffee"": 20, ""latte"": 15, ""sandwich"": 10}"
2024-01-02,1350.0,52,"{""coffee"": 25, ""latte"": 18, ""sandwich"": 9}"
2024-01-03,1100.0,38,"{""coffee"": 18, ""latte"": 12, ""sandwich"": 8}"
```

### Sample CSV File

```bash
# Create sample data
echo 'date,sales_amount,orders_count,menu_items_sold
2024-01-01,1200.0,45,"{""coffee"": 20, ""latte"": 15, ""sandwich"": 10}"
2024-01-02,1350.0,52,"{""coffee"": 25, ""latte"": 18, ""sandwich"": 9}"
2024-01-03,1100.0,38,"{""coffee"": 18, ""latte"": 12, ""sandwich"": 8}"
2024-01-04,1400.0,55,"{""coffee"": 22, ""latte"": 20, ""sandwich"": 13}"
2024-01-05,1600.0,62,"{""coffee"": 30, ""latte"": 25, ""sandwich"": 7}"
2024-01-06,1800.0,70,"{""coffee"": 35, ""latte"": 30, ""sandwich"": 5}"
2024-01-07,1500.0,58,"{""coffee"": 28, ""latte"": 22, ""sandwich"": 8}"' > sample_sales.csv
```

## 🔐 Authentication Setup

### 1. Enable Email/Password Authentication

1. In Firebase Console, go to Authentication > Sign-in method
2. Enable Email/Password provider
3. Create a test user or enable sign-up

### 2. Test Login

Use the test credentials or create a new user in Firebase Console.

## 🧠 AI Features

### 1. Training the AI Models

The AI models will automatically train when you:
- Upload sales data
- Confirm orders
- Use the system regularly

### 2. AI-Powered Recommendations

The system learns from:
- **Sales patterns** (daily, weekly, seasonal)
- **Order history** (what you actually order)
- **Weather data** (temperature, precipitation)
- **Seasonality** (holidays, weekends)

### 3. Model Accuracy

- Models improve with more data
- Accuracy is shown for each recommendation
- You can override recommendations to improve learning

## 🚀 Deployment

### Backend Deployment (Railway/Render)

1. Push code to GitHub
2. Connect to Railway or Render
3. Set environment variables
4. Deploy

### Frontend Deployment (Vercel/Netlify)

1. Push code to GitHub
2. Connect to Vercel or Netlify
3. Set environment variables
4. Deploy

## 🔧 Troubleshooting

### Common Issues

1. **Firebase Connection Error**
   - Check environment variables
   - Verify service account permissions

2. **ML Model Training Fails**
   - Ensure sufficient data (at least 7 days)
   - Check CSV format

3. **Frontend Build Errors**
   - Clear node_modules and reinstall
   - Check TypeScript errors

### Support

For issues or questions, check the API documentation at `/docs` or review the code comments.

## 📈 Next Steps

1. **Upload your real sales data**
2. **Configure your menu items and suppliers**
3. **Train the AI models with your data**
4. **Start using AI-powered recommendations**

The system will get smarter over time as it learns your ordering patterns! 