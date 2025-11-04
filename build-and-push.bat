@echo off
REM Build and Push Docker Image Script for Windows
REM Usage: build-and-push.bat <your-dockerhub-username>

if "%1"=="" (
    echo Error: Docker Hub username required
    echo Usage: build-and-push.bat ^<your-dockerhub-username^>
    exit /b 1
)

set USERNAME=%1
set IMAGE_NAME=sculptor
set TAG=latest

echo 🐳 Building Docker image...
docker build -t %USERNAME%/%IMAGE_NAME%:%TAG% .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Build successful!
    echo.
    echo 🚀 Pushing to Docker Hub...
    docker push %USERNAME%/%IMAGE_NAME%:%TAG%
    
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Push successful!
        echo.
        echo 📦 Your image is now available at:
        echo    %USERNAME%/%IMAGE_NAME%:%TAG%
        echo.
        echo 🚂 To deploy on Railway:
        echo    1. Go to railway.app
        echo    2. Create new project
        echo    3. Deploy from Docker image
        echo    4. Enter: %USERNAME%/%IMAGE_NAME%:%TAG%
        echo    5. Add environment variables
        echo.
    ) else (
        echo ❌ Push failed!
        exit /b 1
    )
) else (
    echo ❌ Build failed!
    exit /b 1
)
