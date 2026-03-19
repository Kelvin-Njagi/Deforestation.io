@echo off
echo ================================================
echo ?? Deforestation Monitoring System
echo ================================================
echo.

REM Create directories if they don't exist
if not exist logs mkdir logs
if not exist uploads mkdir uploads
if not exist reports mkdir reports
if not exist temp mkdir temp

echo ? Directories ready
echo.
echo ?? Starting application...
echo.

streamlit run app.py

pause
