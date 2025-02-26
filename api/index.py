from app.server import app

# This is required for Vercel to properly handle the Flask app
if __name__ == "__main__":
    app.run()