@echo off
REM SPARC Radial-Dependent RAR Analysis - Windows Quick Start

echo.
echo ======================================================================
echo SPARC RADIAL-DEPENDENT RAR ANALYSIS
echo Testing SDH+ vs ΛCDM with existing data
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import numpy, pandas, matplotlib, scipy, seaborn, yaml" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Run the analysis
echo.
echo Starting analysis...
echo.
python run_analysis.py

if errorlevel 1 (
    echo.
    echo ERROR: Analysis failed!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo ANALYSIS COMPLETE
echo ======================================================================
echo.
echo Results saved to:
echo   - output/tables/radial_fits_results.csv
echo   - output/tables/interpretation.json
echo   - output/plots/radial_rar_analysis.png
echo.
pause