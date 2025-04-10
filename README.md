# Shipping Application

A cross-platform application for managing shipping operations, built with PyQt5 for the UI and FastAPI for the backend.

## Features

- Modern PyQt5-based user interface
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
   ```bash
   python build_executable.py --onefile --no-confirm
   ```

   Options:
   - `--onefile`: Build a single executable file (recommended)
   - `--no-confirm`: Skip confirmation prompts
   - `--debug`: Enable debug mode in the built application

3. The executable will be created in the `dist` directory along with the startup scripts.

### Running the Built Application

- **Windows**: Double-click `run_shipping_app.bat` in the `dist` directory
- **macOS/Linux**: Run `./run_shipping_app.sh` in the `dist` directory

The executable contains both the PyQt UI and FastAPI backend, which will start automatically when you run the application.

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