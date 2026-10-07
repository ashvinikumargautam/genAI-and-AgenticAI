from pathlib import Path
from dotenv import load_dotenv

# Load .env from D:\genAI&AgenticAI\.env
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

# Import server AFTER loading .env
from .server import app
import uvicorn


def main():
    uvicorn.run(app, port=8000, host="127.0.0.1")


if __name__ == "__main__":
    main()