# UV Best Practices Guide (Git Bash)

This guide provides best practices for using the `uv` package manager in Git Bash within VSCode on Windows. UV is a fast Python package installer and resolver designed to be a drop-in replacement for pip with significantly improved performance.

## Installation

The recommended way to install UV is using pipx, which creates an isolated environment for Python applications:

```bash
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
5. [Git Bash-Specific Tips](#git-bash-specific-tips)

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

In Git Bash:
```bash
source .venv/Scripts/activate
```

Note: Git Bash uses Unix-style paths with forward slashes, even on Windows.

### Checking Current Environment

When a virtual environment is activated, Git Bash modifies your prompt to show the active environment name. You'll see something like `(.venv) username@hostname MINGW64 ~/path/to/project`.

You can also check the current environment by examining the `VIRTUAL_ENV` environment variable:

```bash
echo $VIRTUAL_ENV
```

This will display the full path to the active virtual environment, or nothing if no environment is active.

To see all environment-related variables:

```bash
env | grep -E "PYTHON|VIRTUAL"
```

You can also check which Python executable is being used:

```bash
which python
```

When an environment is active, this should point to the Python in your virtual environment.

### Deactivating Environments

From an activated environment:
```bash
deactivate
```

### Listing Environments

UV doesn't have a built-in command to list environments (unlike conda). Instead, you can use Git Bash commands:

```bash
# List all .venv directories in your projects folder
find "/c/path/to/projects" -type d -name ".venv" 

# List all virtual environments with their parent directory (project name)
find "/c/path/to/projects" -type d -name ".venv" | while read -r env_path; do
  project_dir=$(dirname "$env_path")
  project_name=$(basename "$project_dir")
  echo "Project: $project_name, Path: $env_path"
done
```

Note: In Git Bash, Windows paths are accessed using the `/c/` prefix instead of `C:\`. For paths with spaces, always enclose them in quotes (`"/c/path with spaces/projects"`) to avoid the shell interpreting spaces as argument separators.

### Deleting Environments

In Git Bash, delete the environment directory:

```bash
rm -rf .venv
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

```bash
# Extract pip dependencies from conda YAML
python -c "import yaml; f=open('environment.yml'); data=yaml.safe_load(f); print('\n'.join(data.get('dependencies', {}).get('pip', [])))" > requirements.txt
```

2. Extract conda dependencies and convert them to pip format:

```bash
# Extract conda dependencies
python -c "import yaml; f=open('environment.yml'); data=yaml.safe_load(f); deps=[d for d in data.get('dependencies', []) if isinstance(d, str)]; print('\n'.join(deps))" > conda_deps.txt
```

3. Create a new UV environment and install the requirements:

```bash
# Create new environment
uv venv

# Activate it
source .venv/Scripts/activate

# Install requirements
uv pip install -r requirements.txt
```

4. For conda-specific packages, you may need to find pip equivalents.

### Example: Converting cs224n Environment

For the specific `cs224n_backup.yml` file:

1. Create a new UV environment:

```bash
mkdir cs224n_project
cd cs224n_project
uv venv
source .venv/Scripts/activate
```

2. Install the core packages from the YAML file:

```bash
uv pip install numpy pandas matplotlib scikit-learn torch torchvision torchaudio
```

3. Add any additional packages as needed for your specific project.

## Common Commands Reference

| Task | Git Bash Command |
|------|---------|
| Create environment | `uv venv` |
| Activate environment | `source .venv/Scripts/activate` |
| Install package | `uv pip install package_name` |
| Install from requirements | `uv pip install -r requirements.txt` |
| List installed packages | `uv pip list` |
| Uninstall package | `uv pip uninstall package_name` |
| Update package | `uv pip install --upgrade package_name` |
| Check package info | `uv pip show package_name` |
| Search for package | `uv pip search package_name` |
| Export requirements | `uv pip freeze > requirements.txt` |

## Git Bash-Specific Tips

1. **Path Conversion**: Git Bash uses Unix-style paths. Windows paths are accessed with `/c/` instead of `C:\`.

2. **Environment Variables**: Set environment variables using the export command:
   ```bash
   export PYTHONPATH=/c/path/to/your/project
   ```

3. **Running Scripts**: When running Python scripts, use:
   ```bash
   python script.py
   # or
   ./script.py  # if the script has a shebang line and executable permissions
   ```

4. **File Permissions**: If you need to make a script executable:
   ```bash
   chmod +x script.py
   ```

5. **Command Chaining**: Use Unix-style command chaining:
   ```bash
   # AND operator (run second command only if first succeeds)
   command1 && command2
   
   # OR operator (run second command only if first fails)
   command1 || command2
   
   # Pipe output from one command to another
   command1 | command2
   ```

6. **Tab Completion**: Git Bash supports tab completion for commands and file paths.

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

9. **Shell Scripts**: For complex operations, create shell scripts (.sh files) that can be run in Git Bash.
