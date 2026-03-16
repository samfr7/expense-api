"""
Application entry point.
Run with:  python run.py  OR  flask run
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
