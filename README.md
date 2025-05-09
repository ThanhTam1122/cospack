# Shipping Application

A cross-platform application for managing shipping operations, built with PySide6 for the UI and FastAPI for the backend.

## Features

- Modern PySide6-based user interface
- FastAPI backend with automatic API documentation
- SQL Server database support
- Cross-platform compatibility (Windows, macOS, Linux)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for local development with SQL Server)
- SQL Server ODBC Driver (required for database connectivity)

### Installing SQL Server ODBC Driver

#### Linux
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

#### Windows
Download and install the [Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

#### macOS
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools
```

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd shipping
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start the SQL Server using Docker:
   ```bash
   docker-compose up -d
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Building Executables

The application can be built into a standalone executable using PyInstaller.

### Building the Executable

1. Make sure you have activated your virtual environment and installed all dependencies:
   ```bash
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the build script:

    pattern.1 from the beginning
    ```bash
    python build_executable.py --onefile --no-confirm
    ```
    or
    ```bash
    pyinstaller --noconfirm --windowed --clean --onefile --name "CosPacks" main.py 
    ```
   
    pattern.2 from created spec file
    ```bash
    pyinstaller CosPacks.spec --noconfirm
    ```

   Options:
   - `--onefile`: Build a single executable file (recommended)
   - `--no-confirm`: Skip confirmation prompts
   - `--debug`: Enable debug mode in the built application

3. The executable will be created in the `dist` directory along with the startup scripts.

### Running the Built Application

- **Windows**: Double-click `run_shipping_app.bat` in the `dist` directory
   sudo dpkg --add-architecture i386
   sudo apt update
   sudo apt install wine64 wine32

   export WINEPREFIX=~/wineprefix
   winecfg
   
   wget https://www.python.org/ftp/python/3.9.10/python-3.9.10-amd64.exe
   wine python-3.9.10-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

   wine python build_executable.py
- **macOS/Linux**: Run `./run_shipping_app.sh` in the `dist` directory

The executable contains both the PySide UI and FastAPI backend, which will start automatically when you run the application.

## Configuration

The application can be configured using environment variables or a `.env` file.

### Environment Variables

- `ENV`: Set to `development` or `production` (default: development)
- `DEBUG`: Enable or disable debug mode (default: False)

### Database Configuration

#### Development (Docker/SQL Server)
- `DEV_SQL_SERVER`: SQL Server host (default: localhost)
- `DEV_SQL_PORT`: SQL Server port (default: 1433)
- `DEV_SQL_DB`: Database name (default: shipping_db)
- `DEV_SQL_USER`: SQL Server username (default: sa)
- `DEV_SQL_PASSWORD`: SQL Server password (default: YourStrong@Passw0rd)

#### Production (Remote Server)
- `PROD_SQL_SERVER`: SQL Server host (default: db.example.com)
- `PROD_SQL_PORT`: SQL Server port (default: 1433)
- `PROD_SQL_DB`: Database name (default: shipping_db)
- `PROD_SQL_USER`: SQL Server username (default: sa)
- `PROD_SQL_PASSWORD`: SQL Server password (default: YourStrong@Passw0rd)

## License

[Your License] 