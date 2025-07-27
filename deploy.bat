@echo off
REM 🚀 AI Insurance Document Analyzer - Heroku Deployment Script (Windows)
REM This script automates the deployment process to Heroku

echo 🚀 Starting Heroku deployment...

REM Check if Heroku CLI is installed
heroku --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Heroku CLI is not installed. Please install it first:
    echo https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Check if user is logged in to Heroku
heroku auth:whoami >nul 2>&1
if errorlevel 1 (
    echo [WARNING] You are not logged in to Heroku. Please login first:
    heroku login
)

REM Get app name from user
set /p APP_NAME="Enter your Heroku app name (or press Enter to auto-generate): "

if "%APP_NAME%"=="" (
    echo [INFO] Creating Heroku app with auto-generated name...
    for /f "tokens=*" %%i in ('heroku create --json ^| findstr "name"') do (
        set APP_NAME=%%i
    )
    set APP_NAME=%APP_NAME:"name":"=%
    set APP_NAME=%APP_NAME:"=%
    echo [SUCCESS] Created app: %APP_NAME%
) else (
    echo [INFO] Creating Heroku app: %APP_NAME%
    heroku create %APP_NAME%
)

REM Set stack to heroku-22
echo [INFO] Setting stack to heroku-22...
heroku stack:set heroku-22 --app %APP_NAME%

REM Check if GROQ_API_KEY is provided
if "%GROQ_API_KEY%"=="" (
    echo [WARNING] GROQ_API_KEY environment variable not set.
    set /p GROQ_API_KEY="Enter your Groq API key: "
)

REM Set environment variables
echo [INFO] Setting environment variables...
heroku config:set GROQ_API_KEY="%GROQ_API_KEY%" --app %APP_NAME%
heroku config:set PYTHON_VERSION=3.11.7 --app %APP_NAME%

REM Add PostgreSQL if not already added
echo [INFO] Checking for PostgreSQL addon...
heroku addons --app %APP_NAME% | findstr "postgresql" >nul
if errorlevel 1 (
    echo [INFO] Adding PostgreSQL addon...
    heroku addons:create heroku-postgresql:mini --app %APP_NAME%
) else (
    echo [SUCCESS] PostgreSQL already configured
)

REM Deploy the backend
echo [INFO] Deploying backend to Heroku...
git subtree push --prefix backend heroku main

REM Wait for deployment to complete
echo [INFO] Waiting for deployment to complete...
timeout /t 10 /nobreak >nul

REM Check if deployment was successful
echo [INFO] Checking deployment status...
heroku ps --app %APP_NAME% | findstr "up" >nul
if errorlevel 1 (
    echo [ERROR] Deployment failed. Check logs with: heroku logs --tail --app %APP_NAME%
    pause
    exit /b 1
) else (
    echo [SUCCESS] Backend deployed successfully!
    
    REM Get the app URL
    for /f "tokens=*" %%i in ('heroku info --app %APP_NAME% ^| findstr "Web URL"') do (
        set APP_URL=%%i
    )
    set APP_URL=%APP_URL:Web URL:=%
    echo [SUCCESS] Your backend is available at: %APP_URL%
    
    REM Test the health endpoint
    echo [INFO] Testing health endpoint...
    curl -s "%APP_URL%/health" | findstr "healthy" >nul
    if errorlevel 1 (
        echo [WARNING] Health check failed. Check logs with: heroku logs --tail --app %APP_NAME%
    ) else (
        echo [SUCCESS] Health check passed!
    )
)

REM Frontend deployment instructions
echo.
echo [INFO] 🎉 Backend deployment complete!
echo.
echo [INFO] Next steps for frontend deployment:
echo.
echo 1. Deploy frontend to Vercel:
echo    - Go to https://vercel.com
echo    - Import your GitHub repository
echo    - Set build command: cd frontend ^&^& npm install ^&^& npm run build
echo    - Set output directory: frontend/dist
echo    - Add environment variable: VITE_API_BASE_URL=%APP_URL%
echo.
echo 2. Or deploy to Netlify:
echo    - Go to https://netlify.com
echo    - Import your GitHub repository
echo    - Set build command: cd frontend ^&^& npm install ^&^& npm run build
echo    - Set publish directory: frontend/dist
echo    - Add environment variable: VITE_API_BASE_URL=%APP_URL%
echo.
echo 3. Monitor your app:
echo    - View logs: heroku logs --tail --app %APP_NAME%
echo    - Check status: heroku ps --app %APP_NAME%
echo    - Open app: heroku open --app %APP_NAME%
echo.

echo [SUCCESS] Deployment script completed! 🚀
pause 