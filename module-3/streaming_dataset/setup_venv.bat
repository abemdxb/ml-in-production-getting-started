@echo off
echo Setting up virtual environment for StreamingDataset...

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r module-3\streaming_dataset\custom_requirements.txt

echo Virtual environment setup complete!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the custom StreamingDataset example:
echo   python module-3\streaming_dataset\custom_example.py --input-path data\raw\dataset.csv --output-dir data\custom_streaming
echo.
echo To deactivate the virtual environment when done:
echo   deactivate
