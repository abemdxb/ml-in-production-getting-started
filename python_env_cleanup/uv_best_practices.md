# UV Best Practices Guide (PowerShell)

This guide provides best practices for using the `uv` package manager in PowerShell within VSCode on Windows. UV is a fast Python package installer and resolver designed to be a drop-in replacement for pip with significantly improved performance.

## Installation

The recommended way to install UV is using pipx, which creates an isolated environment for Python applications:

```powershell
# Install pipx if you don't have it
python -m pip install --user pipx
python -m pipx ensurepath

# Close and reopen your terminal for PATH changes to take effect

# Install UV using pipx
pipx install uv

# Verify installation
uv --version
```

This approach keeps UV isolated from your Python environments, making it more reliable and easier to manage.

## Table of Contents

1. [Environment Management](#environment-management)
2. [Package Management](#package-management)
3. [Converting from Conda to UV](#converting-from-conda-to-uv)
4. [Common Commands Reference](#common-commands-reference)
5. [PowerShell-Specific Tips](#powershell-specific-tips)

## Environment Management

### Creating Virtual Environments

Create a new virtual environment in the current directory:

```bash
uv venv
```

This creates a `.venv` directory in your current project folder. To specify a different location or name:

```bash
uv venv /path/to/env
```

### Activating Environments

In PowerShell:
```powershell
.\.venv\Scripts\activate.ps1
```

### Checking Current Environment

When a virtual environment is activated, PowerShell modifies your prompt to show the active environment name. You'll see something like `(.venv) PS C:\path\to\project>`.

You can also check the current environment by examining the `VIRTUAL_ENV` environment variable:

```powershell
$env:VIRTUAL_ENV
```

This will display the full path to the active virtual environment, or nothing if no environment is active.

To see all environment-related variables:

```powershell
Get-ChildItem env: | Where-Object { $_.Name -like "PYTHON*" -or $_.Name -like "VIRTUAL*" }
```

### Deactivating Environments

From an activated environment:
```powershell
deactivate
```

### Listing Environments

UV doesn't have a built-in command to list environments (unlike conda). Instead, you can use PowerShell commands:

```powershell
# List all .venv directories in your projects folder
Get-ChildItem -Path "C:\path\to\projects" -Recurse -Directory -Filter ".venv" | ForEach-Object { $_.FullName }

# List all virtual environments with their parent directory (project name)
Get-ChildItem -Path "C:\path\to\projects" -Recurse -Directory -Filter ".venv" | ForEach-Object { 
    $projectDir = Split-Path -Parent $_.FullName
    $projectName = Split-Path -Leaf $projectDir
    [PSCustomObject]@{
        ProjectName = $projectName
        EnvPath = $_.FullName
    }
}
```

Note: Always enclose paths in quotes (`"C:\path\to\projects"`) when they might contain spaces to avoid PowerShell interpreting spaces as argument separators.

### Deleting Environments

In PowerShell, delete the environment directory:

```powershell
Remove-Item -Recurse -Force .venv
```

## Package Management

### Installing Packages

Install packages into the current environment:

```bash
uv pip install package_name
```

Install packages with specific versions:

```bash
uv pip install package_name==1.2.3
```

Install from requirements.txt:

```bash
uv pip install -r requirements.txt
```

### Listing Installed Packages

List all installed packages:

```bash
uv pip list
```

### Updating Packages

Update a specific package:

```bash
uv pip install --upgrade package_name
```

Update all packages (using pip-tools):

```bash
# First install pip-tools
uv pip install pip-tools

# Then use pip-compile to update requirements
pip-compile --upgrade
```

### Uninstalling Packages

Uninstall a package:

```bash
uv pip uninstall package_name
```

## Converting from Conda to UV

### From Conda Environment YAML to UV

If you have a conda environment YAML file (like `cs224n_backup.yml`), you can convert it to a format usable by UV:

1. Extract the pip dependencies from the conda YAML file:

```powershell
# Extract pip dependencies from conda YAML
python -c "import yaml; f=open('environment.yml'); data=yaml.safe_load(f); print('\n'.join(data.get('dependencies', {}).get('pip', [])))" > requirements.txt
```

2. Extract conda dependencies and convert them to pip format:

```powershell
# Extract conda dependencies
python -c "import yaml; f=open('environment.yml'); data=yaml.safe_load(f); deps=[d for d in data.get('dependencies', []) if isinstance(d, str)]; print('\n'.join(deps))" > conda_deps.txt
```

3. Create a new UV environment and install the requirements:

```powershell
# Create new environment
uv venv

# Activate it
.\.venv\Scripts\activate.ps1

# Install requirements
uv pip install -r requirements.txt
```

4. For conda-specific packages, you may need to find pip equivalents.

### Example: Converting cs224n Environment

For the specific `cs224n_backup.yml` file:

1. Create a new UV environment:

```powershell
New-Item -ItemType Directory -Path cs224n_project
Set-Location -Path cs224n_project
uv venv
.\.venv\Scripts\activate.ps1
```

2. Install the core packages from the YAML file:

```powershell
uv pip install numpy pandas matplotlib scikit-learn torch torchvision torchaudio
```

3. Add any additional packages as needed for your specific project.

## Common Commands Reference

| Task | PowerShell Command |
|------|---------|
| Create environment | `uv venv` |
| Activate environment | `.\.venv\Scripts\activate.ps1` |
| Install package | `uv pip install package_name` |
| Install from requirements | `uv pip install -r requirements.txt` |
| List installed packages | `uv pip list` |
| Uninstall package | `uv pip uninstall package_name` |
| Update package | `uv pip install --upgrade package_name` |
| Check package info | `uv pip show package_name` |
| Search for package | `uv pip search package_name` |
| Export requirements | `uv pip freeze > requirements.txt` |

## Best Practices

1. **One Environment Per Project**: Create a separate virtual environment for each project to avoid dependency conflicts.

2. **Version Control**: 
   - Include `requirements.txt` in version control
   - Add `.venv/` to your `.gitignore` file

3. **Documentation**: Document environment setup steps in a README.md file in your project.

4. **Reproducibility**: Use `uv pip freeze > requirements.txt` to capture exact package versions.

5. **Environment Activation**: Always activate the virtual environment before working on a project.

6. **Project Organization**: Keep a consistent project structure:
   ```
   project_name/
   ├── .venv/
   ├── requirements.txt
   ├── README.md
   ├── src/
   │   └── ...
   └── tests/
       └── ...
   ```

7. **Performance**: UV is significantly faster than pip, especially for large dependency trees.

8. **Cleanup**: Regularly review and remove unused environments to save disk space.
