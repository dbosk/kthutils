# Copilot Instructions for kthutils

## Project Overview

`kthutils` is a Python package that provides various utilities for automation at KTH (Royal Institute of Technology). It includes both a Python API and a command-line interface for managing KTH systems.

## Key Modules

- **kthutils.ug**: Access the UG editor through Python for managing user groups
- **kthutils.participants**: Read expected course participants
- **kthutils.iprange**: Read IP ranges for computers in lab rooms
- **kthutils.forms**: Read forms data (CSV) from KTH Forms
- **kthutils.credentials**: Handle authentication credentials
- **kthutils.cli**: Command-line interface using Typer

## Technology Stack

### Literate Programming
- This project uses **noweb** for literate programming
- Source files have `.nw` extension (noweb format)
- Python and shell scripts are extracted from `.nw` files during build
- Documentation is generated from the same `.nw` files

### Build System
- Uses **Makefiles** for building at multiple levels (root, doc, src, tests)
- Run `make` in the root directory to build everything
- Python files are generated from `.nw` files using `notangle`
- Documentation is built using LaTeX with pythontex

### Package Management
- Uses **Poetry** for dependency management
- Python 3.8+ required
- Run `poetry install` to install dependencies
- Run `poetry build` to build the package

### Dependencies
- weblogin: For web authentication
- typer: For CLI implementation
- typerconf: Configuration management for Typer
- cachetools: For caching
- openpyxl: For Excel file handling
- ladok3: For Ladok3 integration
- rich: For rich terminal output

## Development Workflow

### Building the Project
```bash
# Build everything (generates Python files from .nw, builds documentation)
make all

# Build only the source modules
make -C src/kthutils all

# Build documentation
make -C doc all
```

### Testing
```bash
# Run tests using pytest
make -C tests all

# Run tests with debug mode
make -C tests all DEBUG=1
```

### Cleaning
```bash
# Clean generated files
make clean

# Clean everything including distribution files
make distclean
```

## Code Conventions

### Literate Programming Style
- When modifying functionality, edit the `.nw` files in `src/kthutils/`, not the generated `.py` files
- Code chunks use the format `<<chunk name>>=` followed by code
- Reference other chunks with `<<chunk name>>`
- Add documentation before code chunks to explain the implementation

### Python Style
- Use type hints where appropriate
- Follow PEP 8 conventions
- Use descriptive variable names
- Document functions with docstrings

### CLI Design
- CLI is organized hierarchically (e.g., `kthutils ug members add`)
- Uses Typer for command definition
- Each module provides its own `cli` Typer instance
- Main CLI in `cli.py` combines all subcommand modules

## File Structure

```
.
├── src/kthutils/          # Source code (.nw files and generated Python)
│   ├── cli.nw            # Main CLI interface
│   ├── ug.nw             # UG editor module
│   ├── participants.nw   # Participants module
│   ├── iprange.nw        # IP range module
│   ├── forms.nw          # Forms module
│   └── Makefile          # Build rules for source
├── doc/                   # Documentation (LaTeX)
├── tests/                 # Test files
├── makefiles/             # Shared makefile includes
├── pyproject.toml        # Poetry configuration
└── Makefile              # Root makefile
```

## Common Tasks

### Adding a New Module
1. Create a new `.nw` file in `src/kthutils/`
2. Add it to `MODULES` in `src/kthutils/Makefile`
3. Add extraction rules if needed
4. Import and register in `cli.nw` if it has CLI commands
5. Add documentation chapter in `doc/kthutils.tex`

### Modifying Existing Code
1. Edit the `.nw` file, not the generated `.py` file
2. Rebuild with `make -C src/kthutils`
3. Test the changes
4. Update documentation if needed

### Publishing
```bash
make publish  # Builds, publishes to PyPI, creates GitHub release
```

## Authentication
- Modules that interact with KTH systems require authentication
- Use `kthutils.credentials.get_credentials()` to obtain credentials
- Credentials are typically KTH username and password

## Important Notes
- Generated `.py` files should not be edited directly
- Always work with `.nw` (noweb) source files
- Run `make` after modifying `.nw` files to regenerate Python code
- The project uses literate programming to keep code and documentation together
