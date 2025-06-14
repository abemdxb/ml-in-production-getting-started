# Complete Python Environment Reset Plan

This document outlines a comprehensive plan to completely reset your Python environment, removing all conda and pip packages, and transitioning to using uv for future package management.

## Why Reset?

- Current base environment has 595 packages (extremely high)
- Running outdated conda version (22.9.0)
- Complex interdependencies between packages
- Potential conflicts between conda and pip packages
- Need for a clean slate before transitioning to uv

## Phase 1: Backup and Documentation

Before making any changes, back up important information:

```powershell
# List all conda environments
conda env list | Out-File -FilePath my_environments_list.txt

# Export important environments
conda env export -n cs224n | Out-File -FilePath cs224n_backup.yml
# Repeat for other important environments

# List global pip packages
pip list --user | Out-File -FilePath global_pip_packages.txt

# List conda base pip packages
conda activate base
pip list | Out-File -FilePath conda_base_pip_packages.txt

# Check pip config
pip config list -v | Out-File -FilePath pip_config_backup.txt
```

## Phase 2: Clean Up Existing Files

Remove all conda cleanup-related files:

```powershell
# Navigate to your project directory
Set-Location -Path "C:\Users\abemd\Documents\ML Experiments\ML_in_Prod\ml-in-production-getting-started"

# Remove cleanup files
Remove-Item -Path clean_conda_base.py -ErrorAction SilentlyContinue
Remove-Item -Path conda_cleanup_commands_*.sh -ErrorAction SilentlyContinue
Remove-Item -Path conda_cleanup_summary.md -ErrorAction SilentlyContinue
Remove-Item -Path conda_environment_management.md -ErrorAction SilentlyContinue
Remove-Item -Path environment_backup.yml -ErrorAction SilentlyContinue
Remove-Item -Path global_packages.txt -ErrorAction SilentlyContinue
Remove-Item -Path python_environment_recovery.md -ErrorAction SilentlyContinue
Remove-Item -Path test_base_environment.bat -ErrorAction SilentlyContinue
Remove-Item -Path test_environment.py -ErrorAction SilentlyContinue
Remove-Item -Path test_plot.png -ErrorAction SilentlyContinue
```

## Phase 3: Exit All Environments

Ensure you're not in any virtual environments:

```powershell
# If in a conda environment
conda deactivate

# If in a venv
deactivate
```

## Phase 4: Complete Uninstallation (Updated)

### 4.1 Preparation

1. Close VSCode completely
2. Close any terminals or applications that might be using Python
3. Open Windows PowerShell as Administrator (right-click on PowerShell and select "Run as Administrator")

### 4.2 Remove Global Pip Packages

```powershell
# List all user-level pip packages to verify what needs to be removed
pip list --user

# Uninstall all user-level pip packages
pip freeze --user | ForEach-Object { $_.split('==')[0] } | ForEach-Object { pip uninstall -y $_ }

# Clear pip cache
pip cache purge
```

### 4.3 Deactivate and Clean Conda

```powershell
# Deactivate any active conda environment
conda deactivate

# List all conda environments to verify what needs to be removed
conda env list

# Remove all conda environments except base
conda env list | Select-String -Pattern "^(?!base)" | ForEach-Object { $_.ToString().Trim().Split(" ")[0] } | Where-Object { $_ -ne "" } | ForEach-Object { conda env remove -n $_ }

# Clean conda packages and caches
conda clean --all -y
```

### 4.4 Remove Conda Initialization

```powershell
# Check if conda is initialized in PowerShell
Get-Content $PROFILE | Select-String -Pattern "conda initialize"

# If found, remove conda initialization from PowerShell profile
# (Make a backup first)
Copy-Item $PROFILE "$PROFILE.backup" -ErrorAction SilentlyContinue
Get-Content $PROFILE | Where-Object { $_ -notmatch "conda initialize" } | Set-Content "$PROFILE.temp" -ErrorAction SilentlyContinue
Move-Item "$PROFILE.temp" $PROFILE -Force -ErrorAction SilentlyContinue
```

### 4.5 Uninstall Standard Python (Added Step)

1. Use Control Panel > Programs > Uninstall a program
2. Select "Python 3.12" and uninstall
3. Follow the uninstallation wizard completely

### 4.6 Uninstall Anaconda/Miniconda

1. Use Control Panel > Programs > Uninstall a program
2. Select Anaconda/Miniconda and uninstall
3. Follow the uninstallation wizard completely

### 4.7 Manual Cleanup (Critical Step - Updated with Your Specific Paths)

After the uninstallers complete, manually delete these directories:

```powershell
# Remove main Miniconda directory (your specific path)
Remove-Item -Recurse -Force -Path "C:\Users\abemd\miniconda3" -ErrorAction SilentlyContinue

# Remove standard Python directory (your specific path)
Remove-Item -Recurse -Force -Path "C:\Users\abemd\AppData\Local\Programs\Python\Python312" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force -Path "C:\Users\abemd\AppData\Local\Programs\Python\Launcher" -ErrorAction SilentlyContinue

# Remove conda configuration directories
Remove-Item -Recurse -Force -Path "C:\Users\abemd\.conda" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force -Path "C:\Users\abemd\AppData\Local\conda" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force -Path "C:\Users\abemd\AppData\Roaming\conda" -ErrorAction SilentlyContinue

# Remove Python user scripts
Remove-Item -Recurse -Force -Path "C:\Users\abemd\AppData\Roaming\Python" -ErrorAction SilentlyContinue

# Remove .condarc file if it exists
Remove-Item -Force -Path "C:\Users\abemd\.condarc" -ErrorAction SilentlyContinue
```

### 4.8 Clean Up Pip Directories

```powershell
# Remove pip configuration files
Remove-Item -Force -Path "C:\Users\abemd\AppData\Roaming\pip\pip.ini" -ErrorAction SilentlyContinue

# Clean up pip cache
Remove-Item -Recurse -Force -Path "C:\Users\abemd\AppData\Local\pip\Cache" -ErrorAction SilentlyContinue
```

### 4.9 Clean Up Environment Variables (Updated)

1. Open System Properties:
   ```powershell
   rundll32 sysdm.cpl,EditEnvironmentVariables
   ```

2. In the Environment Variables window:
   - Check both "User variables" and "System variables" sections
   - Remove ALL of these PATH entries:
     * C:\Users\abemd\miniconda3
     * C:\Users\abemd\miniconda3\Library\mingw-w64\bin
     * C:\Users\abemd\miniconda3\Library\usr\bin
     * C:\Users\abemd\miniconda3\Library\bin
     * C:\Users\abemd\miniconda3\Scripts
     * C:\Users\abemd\miniconda3\bin
     * C:\Users\abemd\miniconda3\condabin
     * C:\Users\abemd\AppData\Local\Programs\Python\Python312
     * C:\Users\abemd\AppData\Local\Programs\Python\Python312\Scripts
     * C:\Users\abemd\AppData\Local\Programs\Python\Launcher
     * C:\Users\abemd\AppData\Roaming\Python\Python312\Scripts
   - Remove any CONDA_* environment variables
   - Remove any PIP_* environment variables
   - Remove any PYTHON* environment variables

### 4.10 Restart Computer

Restart your computer to ensure all changes take effect and no processes are still using the deleted files.

### 4.11 Verification

After restarting, open a new PowerShell window and verify:

```powershell
# These should all return "not recognized" errors if uninstallation was successful
conda --version
python --version
pip --version

# Also verify no Python paths remain
where.exe python
$env:PATH -split ";" | Where-Object { $_ -like "*python*" -or $_ -like "*conda*" }
```

After completing these steps, you can proceed with Phase 5 for a fresh installation.


## Phase 5: Fresh Installation

### 5.1 Install Miniconda

1. Download the latest Miniconda installer from: https://docs.conda.io/en/latest/miniconda.html
2. Run the installer with these settings:
   - Install for "Just Me" (not all users)
   - Choose a directory path without spaces (default is fine)
   - **Important**: Do NOT add Miniconda to the PATH environment variable
   - **Important**: Do NOT register Miniconda as the default Python

### 5.2 Initialize Miniconda for Both PowerShell and Git Bash

```powershell
# Open a new PowerShell window (not in VSCode)
# Initialize for PowerShell
& "$env:USERPROFILE\miniconda3\Scripts\conda.exe" init powershell

# Initialize for Git Bash (this is critical to make conda work in Git Bash)
& "$env:USERPROFILE\miniconda3\Scripts\conda.exe" init bash

# Configure conda
conda config --set auto_activate_base false
conda config --set channel_priority strict
```

### 5.3 Set Up Minimal Base Environment

```powershell
# Open a new PowerShell window
conda activate base

# Update core packages
conda update -y conda

# Install only essential packages
conda install -y python=3.11 pip setuptools wheel

# Update pip
pip install --upgrade pip
```

## Phase 6: Install uv

Install uv in your base environment:

```powershell
# In base environment
pip install uv

# Verify installation
uv --version
```

## Phase 7: Set Up Project Structure for uv

### 7.1 Create Project Directory Structure

```powershell
# Create a projects directory
New-Item -ItemType Directory -Path "$env:USERPROFILE\python_projects" -Force
```

### 7.2 Set Up Your First uv Project

```powershell
# Navigate to your project
Set-Location -Path "C:\Users\abemd\Documents\ML Experiments\ML_in_Prod\ml-in-production-getting-started"

# Create a new environment with uv
uv venv

# Activate the environment
.\.venv\Scripts\activate.ps1

# Install dependencies
uv pip install -r requirements.txt  # If you have requirements.txt
# Or install specific packages
uv pip install numpy pandas matplotlib scikit-learn
```

## Phase 8: Recreate Important Environments (Optional)

For each important conda environment, create a uv equivalent:

```powershell
# Example for cs224n environment
New-Item -ItemType Directory -Path "$env:USERPROFILE\python_projects\cs224n" -Force
Set-Location -Path "$env:USERPROFILE\python_projects\cs224n"

# Create new environment
uv venv

# Activate
.\.venv\Scripts\activate.ps1

# Install packages (from your backup)
# Extract package names from cs224n_backup.yml and install with uv
uv pip install tensorflow torch transformers nltk
```

## Phase 9: Set Up Best Practices

### 9.1 uv Cheat Sheet

```powershell
# Common uv commands
uv venv                                          # Create virtual environment in current directory
uv pip install PACKAGE                           # Install a package
uv pip install -r requirements.txt               # Install from requirements file
uv pip freeze | Out-File -FilePath requirements.txt  # Save current packages to requirements
```

### 9.2 Project-Specific Environments

- Always create a separate environment for each project
- Use `.venv` in the project directory (uv's default)
- Include a requirements.txt or pyproject.toml in each project

### 9.3 Environment Activation Helpers

#### For Git Bash

Add this to your .bashrc file for easier activation in Git Bash:

```bash
# Function to activate the virtual environment in the current directory
activate() {
  if [ -d ".venv" ]; then
    source .venv/Scripts/activate
  else
    echo "No .venv directory found in current directory"
  fi
}
```

#### For PowerShell

Add this to your PowerShell profile ($PROFILE) for easier activation in PowerShell:

```powershell
# Function to activate the virtual environment in the current directory
function Activate-Venv {
  if (Test-Path -Path ".\.venv") {
    .\.venv\Scripts\activate.ps1
  } else {
    Write-Host "No .venv directory found in current directory" -ForegroundColor Red
  }
}

# Create an alias for easier use
Set-Alias -Name activate -Value Activate-Venv
```

## Phase 10: Verify and Test

Test your new setup:

```powershell
# Create a test project
New-Item -ItemType Directory -Path "$env:USERPROFILE\python_projects\test" -Force
Set-Location -Path "$env:USERPROFILE\python_projects\test"

# Create environment and install packages
uv venv
.\.venv\Scripts\activate.ps1
uv pip install numpy matplotlib

# Test with a simple script
"import numpy as np; print(np.__version__)" | Out-File -FilePath test.py -Encoding utf8
python test.py
```

## Potential Issues and Solutions

### Issue: Can't uninstall some pip packages
Solution: Use `pip uninstall --break-system-packages` if needed for stubborn packages

### Issue: Conda won't uninstall completely
Solution: Manually delete the Anaconda directory and all related files

### Issue: PATH still contains conda references
Solution: Restart your computer after cleaning environment variables

## Why uv?

uv offers several advantages over conda and traditional pip:

1. **Speed**: uv is significantly faster than conda/pip for package installation
2. **Simplicity**: Cleaner, more straightforward approach to environment management
3. **Compatibility**: Works with standard Python virtual environments
4. **Modern design**: Written in Rust with performance in mind
5. **Deterministic builds**: Better dependency resolution

## References

- [uv Documentation](https://github.com/astral-sh/uv)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Miniconda Documentation](https://docs.conda.io/en/latest/miniconda.html)
