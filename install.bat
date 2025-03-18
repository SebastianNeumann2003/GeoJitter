@echo off
setlocal

:: Try to find a Python installation
where py >nul 2>nul && set PYTHON_CMD=py || (
    where python >nul 2>nul && set PYTHON_CMD=python || (
        where python3 >nul 2>nul && set PYTHON_CMD=python3 || (
            echo Could not find a valid Python installation
            exit /b 1
        )
    )
)

:: Create virtual environment
%PYTHON_CMD% -m venv netgeo_venv && (
    :: Activate virtual environment
    call netgeo_venv\Scripts\activate && (
        :: Install dependencies
        %PYTHON_CMD% -m pip install -r requirements.txt && (
            echo Install complete
            exit /b 0
        ) || echo Failed to install requirements
    ) || echo Failed to activate virtual environment
) || echo Failed to create virtual environment

exit /b 1
