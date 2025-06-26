# ☕ Smart Stock Ordering App for Cafés & Restaurants

An AI-powered inventory management system that forecasts demand and generates smart supplier orders.

## 🎯 Features

- **📊 Sales Forecasting**: Upload CSV data and predict future demand using Prophet/RandomForest
- **🥘 Ingredient Planning**: Convert sales forecasts into ingredient requirements
- **📦 Smart Ordering**: Generate supplier orders based on pack sizes and minimum quantities
- **📧 Invoice Integration**: Extract data from supplier invoices via Gmail API (optional)
- **📱 Responsive Dashboard**: Clean, professional UI for easy management

## 🏗️ Tech Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (navigation)
- Recharts (data visualization)
- React Hook Form (form handling)

### Backend
- FastAPI (Python web framework)
- Prophet/RandomForest (ML forecasting)
- Firebase Auth (authentication)
- Firestore (database)
- Pandas (data processing)

## 📁 Project Structure

```
smart-stock-app/
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   └── package.json
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── ml/             # Machine learning modules
│   └── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Firebase project

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📊 CSV Format

Upload CSV files with the following columns:
- `date`: YYYY-MM-DD format
- `sales_amount`: Total daily sales
- `orders_count`: Number of orders
- `menu_items_sold`: JSON string of items and quantities

## 🔮 Future Roadmap

- [ ] User onboarding flow
- [ ] Multiple venue support
- [ ] Stripe billing integration
- [ ] Automated order placement
- [ ] Supplier API integrations
- [ ] Mobile app
- [ ] Advanced analytics dashboard

## 📝 License

MIT License - feel free to use this for your café or restaurant! 