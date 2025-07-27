# 🚀 Heroku Deployment Guide

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Ensure your project is in a Git repository
4. **Groq API Key**: Get your API key from [console.groq.com](https://console.groq.com)

## 🎯 Quick Deploy (One-Click)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Raykarr/AI-Insurance-Document-Analyzer)

## 📋 Manual Deployment Steps

### 1. Prepare Your Repository

```bash
# Clone your repository
git clone https://github.com/Raykarr/AI-Insurance-Document-Analyzer.git
cd AI-Insurance-Document-Analyzer

# Ensure all files are committed
git add .
git commit -m "Prepare for Heroku deployment"
git push origin main
```

### 2. Create Heroku App

```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Set the stack to heroku-22
heroku stack:set heroku-22
```

### 3. Configure Environment Variables

```bash
# Set your Groq API key
heroku config:set GROQ_API_KEY=your_groq_api_key_here

# Set other environment variables if needed
heroku config:set PYTHON_VERSION=3.11.7
```

### 4. Deploy Backend

```bash
# Navigate to backend directory
cd backend

# Deploy to Heroku
git subtree push --prefix backend heroku main

# Or if you're in the root directory
git subtree push --prefix backend heroku main
```

### 5. Verify Deployment

```bash
# Check your app status
heroku ps

# View logs
heroku logs --tail

# Test the health endpoint
curl https://your-app-name.herokuapp.com/health
```

## 🔧 Configuration Files

### Backend Configuration

The following files are already configured:

- `backend/Procfile` - Tells Heroku how to run your app
- `backend/runtime.txt` - Specifies Python version
- `backend/requirements.txt` - Lists Python dependencies
- `app.json` - Heroku app configuration

### Frontend Configuration

For the frontend, you have several options:

1. **Deploy to Vercel** (Recommended for frontend)
2. **Deploy to Netlify**
3. **Deploy to Heroku** (separate app)

## 🌐 Frontend Deployment

### Option 1: Vercel (Recommended)

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set build settings:
   - Framework Preset: Vite
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
4. Add environment variable: `VITE_API_BASE_URL=https://your-backend-app.herokuapp.com`

### Option 2: Netlify

1. Go to [netlify.com](https://netlify.com)
2. Import your GitHub repository
3. Set build settings:
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`
4. Add environment variable: `VITE_API_BASE_URL=https://your-backend-app.herokuapp.com`

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   heroku logs --tail
   
   # Check if all dependencies are in requirements.txt
   pip freeze > requirements.txt
   ```

2. **API Key Issues**
   ```bash
   # Verify environment variables
   heroku config
   
   # Set API key again
   heroku config:set GROQ_API_KEY=your_key_here
   ```

3. **Port Issues**
   - Ensure your app uses `$PORT` environment variable
   - Check the Procfile configuration

4. **Database Issues**
   - SQLite won't work on Heroku (ephemeral filesystem)
   - Consider using PostgreSQL add-on:
     ```bash
     heroku addons:create heroku-postgresql:mini
     ```

### Performance Optimization

1. **Enable Dyno Autoscaling**
   ```bash
   heroku ps:scale web=1
   ```

2. **Monitor Performance**
   ```bash
   heroku addons:create papertrail:choklad
   ```

## 🔐 Security Considerations

1. **Environment Variables**: Never commit API keys to Git
2. **CORS**: Update CORS settings for production
3. **Rate Limiting**: Consider adding rate limiting
4. **HTTPS**: Heroku provides SSL certificates automatically

## 📊 Monitoring

```bash
# View real-time logs
heroku logs --tail

# Check app status
heroku ps

# Monitor dyno usage
heroku ps:scale
```

## 🚀 Post-Deployment

1. **Test all endpoints**
2. **Update frontend API URL**
3. **Set up monitoring**
4. **Configure custom domain** (optional)

## 📞 Support

If you encounter issues:

1. Check Heroku logs: `heroku logs --tail`
2. Verify environment variables: `heroku config`
3. Test locally with Heroku environment: `heroku local web`
4. Check Heroku documentation: [devcenter.heroku.com](https://devcenter.heroku.com) 