import os
from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth # <--- New Import
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from dotenv import load_dotenv

# Import your custom modules
from services import ResearchService, StructureService
from capabilities import VINYL_HUNT, Capability


load_dotenv()

# Initialize Backend Services
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
services = {
    "research_service": ResearchService(client=client),
    "structure_service": StructureService(client=client),
}
vinyl_hunt = Capability(recipe=VINYL_HUNT, services=services)

# Initialize Web App
app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    os.getenv("APP_USER"): generate_password_hash(os.getenv("APP_PASSWORD")),
}

users = {
    os.getenv("APP_USER"): generate_password_hash(os.getenv("APP_PASSWORD")),
}

@auth.verify_password
def verify_password(username, password):
    # 2. Check if user exists
    if username in users:
        stored_hash = users.get(username)
        # 3. Use check_password_hash to verify the plain text against the hash
        if check_password_hash(stored_hash, password):
            return username
    return None


# --- HTML/CSS TEMPLATE ---
# Designed to be a cute, dark-mode, mobile-friendly "Field Tool"
@app.route("/", methods=["GET", "POST"])
@auth.login_required
def index():
    data = None
    query = ""
    error = None

    if request.method == "POST":
        query = request.form.get("album")
        try:
            # 1. Run the Capability
            print(f"\n--- Running Vinyl Hunt for: {query} ---")
            result = vinyl_hunt.run(album=query)
            
            # 2. Extract the structured output
            # Assuming result.output is the Pydantic/Dataclass object you showed earlier
            data = result["output"]
            
        except Exception as e:
            error = str(e)

    return render_template("vinyl_hunt.html", data=data, query=query, error=error)

if __name__ == "__main__":
    # Run the Flask app locally on port 5000
    print("Starting Vinyl Hunter UI...")
    port = int(os.environ.get("PORT",8080))
    app.run(debug=False, host="0.0.0.0", port=port)