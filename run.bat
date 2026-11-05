@echo off
chcp 65001 > nul
echo ===================================================
echo     AI PDF Audiobook Generator - Sách Nói Tự Động
echo ===================================================
echo.
cd /d "%~dp0"

set "UV_PATH=%LOCALAPPDATA%\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe"

if exist "%UV_PATH%" (
    echo Đang khởi động ứng dụng với uv...
    "%UV_PATH%" run streamlit run app.py
) else (
    where uv >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        uv run streamlit run app.py
    ) else (
        echo Đang chạy bằng python thông thường...
        python -m streamlit run app.py
    )
)

pause
