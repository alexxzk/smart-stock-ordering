# 🚀 Frontend Deployment Guide

## **Current Status: Local Development**
- Frontend: http://localhost:5173 (Vite dev server)
- Backend: http://localhost:8000 (FastAPI dev server)

## **Goal: Production Deployment with Custom Domain**
- Frontend: https://yourdomain.com
- Backend: https://api.yourdomain.com (or subdomain)

---

## 🌐 **Option 1: Deploy to Vercel (Recommended)**

### **Step 1: Prepare Frontend for Production**

1. **Build the production version:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Update API configuration:**
   - Change API base URL from `localhost:8000` to your deployed backend URL
   - Update in `src/services/apiService.ts`

### **Step 2: Deploy to Vercel**

1. **Go to Vercel**: https://vercel.com/
2. **Sign up/Login** with GitHub
3. **Import your repository**
4. **Configure build settings:**
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### **Step 3: Environment Variables**

Add these in Vercel dashboard:
```
VITE_API_BASE_URL=https://your-backend.railway.app
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
```

### **Step 4: Deploy**

- Vercel will automatically deploy when you push to GitHub
- Get a URL like: `https://your-app.vercel.app`

---

## 🌐 **Option 2: Deploy to Railway (Full Stack)**

### **Step 1: Deploy Backend**
1. Follow the backend deployment guide
2. Get backend URL: `https://your-backend.railway.app`

### **Step 2: Deploy Frontend to Railway**
1. Create new Railway project
2. Connect your GitHub repository
3. Configure as static site
4. Set build command: `npm run build`
5. Set output directory: `dist`

---

## 🏷️ **Custom Domain Setup**

### **Step 1: Buy a Domain**
- GoDaddy, Namecheap, Google Domains, etc.
- Example: `mycafe.com`

### **Step 2: Configure DNS**

**For Vercel Frontend:**
```
Type: CNAME
Name: @
Value: your-app.vercel.app
```

**For Railway Backend:**
```
Type: CNAME
Name: api
Value: your-backend.railway.app
```

### **Step 3: Add Domain to Vercel**
1. Go to Vercel dashboard
2. Click "Settings" → "Domains"
3. Add your domain: `mycafe.com`
4. Follow DNS configuration instructions

### **Step 4: SSL Certificate**
- Vercel automatically provides SSL
- Your site will be: `https://mycafe.com`

---

## 🔧 **Configuration Updates**

### **Update API Service**
```typescript
// src/services/apiService.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.mycafe.com';

export const apiService = {
  baseURL: API_BASE_URL,
  // ... rest of service
};
```

### **Update Firebase Config**
```typescript
// src/config/firebase.ts
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  // ... other config
};
```

---

## 📊 **Cost Comparison**

### **Vercel (Frontend)**
- **Free Tier**: 100GB bandwidth/month
- **Pro**: $20/month for unlimited bandwidth
- **Custom Domains**: Free

### **Railway (Backend)**
- **Free Tier**: $5 credit/month
- **Pay-as-you-go**: ~$5-20/month for small apps
- **Custom Domains**: Free

### **Domain**
- **Registration**: $10-15/year
- **SSL Certificate**: Free (provided by hosting)

---

## 🎯 **Recommended Setup for MVP**

1. **Backend**: Railway (FastAPI)
2. **Frontend**: Vercel (React)
3. **Domain**: Your custom domain
4. **Total Cost**: ~$15-25/month

---

## 🚀 **Quick Start Commands**

```bash
# 1. Build frontend for production
cd frontend
npm run build

# 2. Test production build locally
npm run preview

# 3. Deploy to Vercel (after connecting GitHub)
# Vercel will auto-deploy on git push

# 4. Update environment variables in Vercel dashboard
```

---

## 🔍 **Testing Your Deployment**

1. **Frontend**: https://your-app.vercel.app
2. **Backend API**: https://your-backend.railway.app/health
3. **Custom Domain**: https://mycafe.com

---

## 🆘 **Troubleshooting**

### **Common Issues:**
1. **CORS Errors**: Update backend CORS origins
2. **API Connection**: Check environment variables
3. **Build Failures**: Check for TypeScript errors
4. **Domain Issues**: Verify DNS configuration

### **Useful Commands:**
```bash
# Check build locally
npm run build

# Test production build
npm run preview

# Check for TypeScript errors
npx tsc --noEmit
```

---

## 📞 **Next Steps**

1. **Deploy backend to Railway**
2. **Deploy frontend to Vercel**
3. **Buy and configure custom domain**
4. **Test all functionality**
5. **Set up monitoring and analytics**

Your app will then be accessible worldwide at your custom domain! 🌍 