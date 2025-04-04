# Shipping Application

A cross-platform application for managing shipping operations, built with PyQt5 for the UI and FastAPI for the backend.

## Features

- Modern PyQt5-based user interface
- FastAPI backend with automatic API documentation
- MySQL database support
- Cross-platform compatibility (Windows, macOS, Linux)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for local development with MySQL)

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

3. Start the MySQL database using Docker:
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

#### Development (Docker/MySQL)
- `DEV_MYSQL_USER`: MySQL username (default: root)
- `DEV_MYSQL_PASSWORD`: MySQL password (default: root_password)
- `DEV_MYSQL_HOST`: MySQL host (default: localhost)
- `DEV_MYSQL_PORT`: MySQL port (default: 3306)
- `DEV_MYSQL_DB`: MySQL database name (default: shipping_db)

#### Production (Remote Server)
- `PROD_MYSQL_USER`: MySQL username (default: shipping_user)
- `PROD_MYSQL_PASSWORD`: MySQL password (default: shipping_password)
- `PROD_MYSQL_HOST`: MySQL host (default: db.example.com)
- `PROD_MYSQL_PORT`: MySQL port (default: 3306)
- `PROD_MYSQL_DB`: MySQL database name (default: shipping_db)

## License

[Your License] 