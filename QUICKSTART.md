# 🚀 Quick Deployment Guide

## Fastest Way to Deploy (5 minutes)

### Option 1: Render.com + MongoDB Atlas (Recommended)

#### 1. Setup MongoDB (2 minutes)
```
1. Go to https://mongodb.com/cloud/atlas/register
2. Create FREE M0 cluster
3. Create database user: username + password
4. Network Access: Allow 0.0.0.0/0
5. Get connection string (format):
   mongodb+srv://USERNAME:PASSWORD@YOUR-CLUSTER.mongodb.net/people_manager
   (Replace USERNAME, PASSWORD, and YOUR-CLUSTER with your actual values)
```

#### 2. Deploy to Render (3 minutes)
```
1. Go to https://render.com
2. New+ → Web Service
3. Connect GitHub: fragenabhishek/People-Manager
4. Settings:
   - Build: pip install -r requirements.txt
   - Start: gunicorn app:app
   - Add env var: MONGO_URI = <your connection string>
5. Create Web Service
6. Wait ~5 minutes
7. Done! 🎉
```

---

### Option 2: Railway.app (Even Easier!)

```
1. Go to https://railway.app
2. Login with GitHub
3. New Project → Deploy from GitHub
4. Select: fragenabhishek/People-Manager
5. Add MongoDB database (auto-configured)
6. Done! 🎉
```

---

### Option 3: PythonAnywhere (No Database Setup)

```
1. Go to https://pythonanywhere.com
2. Sign up for free
3. Web tab → Add new web app → Flask
4. Upload files or clone from GitHub
5. Configure WSGI
6. Reload
7. Done! 🎉
```

---

## Environment Variables

Only ONE variable needed:

| Variable | Required? | Description |
|----------|-----------|-------------|
| `MONGO_URI` | Optional | If not set, uses JSON file storage |

---

## Verify Deployment

Visit your deployed URL and test:
- ✅ Add person
- ✅ Search person
- ✅ View details (click name)
- ✅ Edit person
- ✅ Delete person
- ✅ Refresh page - data persists!

---

## Free Tier Limits

| Platform | Storage | Uptime | Data Persistence |
|----------|---------|--------|------------------|
| Render + MongoDB | 512MB | 100% | ✅ YES |
| Railway | 100MB | 500h/mo | ✅ YES |
| PythonAnywhere | 512MB | 100% | ✅ YES |

---

## Need Help?

See full guide: [DEPLOYMENT.md](DEPLOYMENT.md)

