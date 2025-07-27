@echo off
REM 🚀 Hugging Face Spaces Build Script (Windows)
REM This script builds the frontend and prepares for deployment

echo 🚀 Building for Hugging Face Spaces...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

REM Navigate to frontend directory
echo [INFO] Building frontend...
cd frontend

REM Install dependencies
echo [INFO] Installing frontend dependencies...
npm install

REM Build the frontend
echo [INFO] Building frontend for production...
npm run build

echo [SUCCESS] Frontend built successfully!

REM Copy the built frontend to the huggingface-spaces directory
echo [INFO] Copying built frontend...
cd ..
if not exist "huggingface-spaces\frontend\dist" mkdir "huggingface-spaces\frontend\dist"
xcopy "frontend\dist\*" "huggingface-spaces\frontend\dist\" /E /Y

echo [SUCCESS] Build completed successfully!
echo.
echo 🎉 Your app is ready for Hugging Face Spaces deployment!
echo.
echo Next steps:
echo 1. Push your code to GitHub
echo 2. Create a new Space on Hugging Face
echo 3. Connect your GitHub repository
echo 4. Set the GROQ_API_KEY environment variable
echo 5. Deploy!
echo.
pause 