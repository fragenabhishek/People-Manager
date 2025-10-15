# Deployment Guide - People Manager

Your app now supports **TWO storage options**:
1. **JSON File** (local development)
2. **MongoDB** (cloud deployment - FREE)

---

## **Option 1: Deploy to Render.com + MongoDB Atlas (RECOMMENDED)**

This is completely FREE and gives you persistent database storage.

### **Step 1: Create MongoDB Atlas Database (FREE)**

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up for a free account
3. Create a **FREE M0 Cluster**:
   - Choose **AWS** as provider
   - Select a region close to you
   - Cluster name: `people-manager`
4. Create Database User:
   - Click **"Database Access"** in left menu
   - Click **"Add New Database User"**
   - Username: `admin` (or your choice)
   - Password: Generate a strong password (SAVE THIS!)
   - User Privileges: **Read and write to any database**
5. Whitelist IP Address:
   - Click **"Network Access"** in left menu
   - Click **"Add IP Address"**
   - Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - Confirm
6. Get Connection String:
   - Click **"Database"** in left menu
   - Click **"Connect"** on your cluster
   - Choose **"Connect your application"**
   - Copy the connection string
   - It looks like: `mongodb+srv://admin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
   - Replace `<password>` with your actual password

### **Step 2: Deploy to Render.com (FREE)**

1. Go to https://render.com and sign up (use GitHub login)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `https://github.com/fragenabhishek/People-Manager`
4. Configure:
   - **Name**: `people-manager` (or your choice)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: **Free**
5. Add Environment Variable:
   - Click **"Advanced"**
   - Click **"Add Environment Variable"**
   - **Key**: `MONGO_URI`
   - **Value**: Paste your MongoDB connection string from Step 1
   - Format: `mongodb+srv://USERNAME:PASSWORD@YOUR_CLUSTER.mongodb.net/people_manager`
   - Replace USERNAME, PASSWORD, and YOUR_CLUSTER with your actual MongoDB credentials
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. Your app will be live at: `https://people-manager-xxxx.onrender.com`

✅ **Done! Your app is now live with persistent database storage!**

---

## **Option 2: Deploy to PythonAnywhere (FREE - Simpler)**

This option keeps using JSON file storage (files persist on PythonAnywhere).

1. Go to https://www.pythonanywhere.com and sign up for free
2. Go to **"Web"** tab
3. Click **"Add a new web app"**
4. Choose **"Flask"**
5. Python version: **3.10**
6. Upload your files or clone from GitHub
7. Configure WSGI file to point to your app
8. Reload web app

**Pros**: Simpler setup, no database configuration
**Cons**: Limited to 512MB storage, less scalable

---

## **Option 3: Deploy to Railway.app (FREE)**

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"**
4. Choose **"Deploy from GitHub repo"**
5. Select your repository
6. Add MongoDB:
   - Click **"New"** → **"Database"** → **"Add MongoDB"**
   - Railway will auto-generate `MONGO_URI` environment variable
7. Your app deploys automatically

**Pros**: Easy setup, auto MongoDB
**Cons**: Free tier has time limits (500 hours/month)

---

## **Option 4: Deploy to Replit (EASIEST - FREE)**

1. Go to https://replit.com
2. Click **"Create Repl"**
3. Choose **"Import from GitHub"**
4. Paste your repo URL
5. Click **"Run"**
6. Your app is live instantly!

**Note**: Data won't persist on Replit free tier unless you upgrade or use external database.

---

## **Testing Your Deployment**

After deployment, your app will have a URL like:
- Render: `https://people-manager-xxxx.onrender.com`
- Railway: `https://people-manager-production-xxxx.up.railway.app`
- PythonAnywhere: `https://yourusername.pythonanywhere.com`

Open the URL in your browser and test:
1. ✅ Add a new person
2. ✅ Search for the person
3. ✅ Click on name to view details
4. ✅ Edit the person
5. ✅ Delete the person
6. ✅ Close browser and reopen - data should still be there!

---

## **Environment Variables Explained**

- **`MONGO_URI`** (optional): If set, app uses MongoDB. If not set, uses JSON file.
- **`PORT`** (auto-set by hosting platform): Port number for the web server.

---

## **Troubleshooting**

### **MongoDB connection fails**
- Check that your password in connection string doesn't have special characters
- If it does, URL encode it: https://www.urlencoder.org/
- Verify IP whitelist includes 0.0.0.0/0

### **App crashes on Render**
- Check logs in Render dashboard
- Verify all dependencies are in requirements.txt
- Check that MONGO_URI is set correctly

### **Data not persisting**
- If using MongoDB: Check connection string
- If using JSON: Only PythonAnywhere supports file persistence on free tier

---

## **Recommended Choice**

🏆 **Render.com + MongoDB Atlas** (Option 1)
- ✅ Completely FREE
- ✅ Persistent database
- ✅ Auto-deploys from GitHub
- ✅ Professional setup
- ✅ Scales easily

---

## **Cost Breakdown**

| Platform | Storage | Cost | Persistence |
|----------|---------|------|-------------|
| Render + MongoDB Atlas | Database | $0 | ✅ YES |
| Railway | Database | $0* | ✅ YES |
| PythonAnywhere | File | $0 | ✅ YES |
| Replit | None | $0 | ❌ NO |

*Railway: 500 hours/month free, then $5/month

---

## **Next Steps After Deployment**

1. Share your live URL with friends!
2. Add custom domain (optional, some platforms offer free subdomains)
3. Enable HTTPS (automatic on most platforms)
4. Monitor usage in platform dashboard
5. Set up continuous deployment (auto-deploy on git push)

---

Need help? Check platform documentation or ask for assistance!

