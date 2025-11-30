from flask import Flask, jsonify, request
from configparser import ConfigParser
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- Global Initialization and Configuration ---
# 1. Initialize Flask App
app = Flask(__name__)

# 2. Firestore Setup (Adapted for Robust Local/Cloud Environment Detection)
db = None
CONFIG_COLLECTION_PATH = ""
CONFIG_DOC_ID = "extracted_config_data"

try:
    APP_ID = os.environ.get('__app_id', 'default-app-id')
    firebase_config_str = os.environ.get('__firebase_config')
    
    # Check if we are running in an environment that provides Firebase configuration
    # If '__firebase_config' is present, we attempt server-side initialization.
    if firebase_config_str:
        firebase_config = json.loads(firebase_config_str)
        
        if not firebase_admin._apps:
            # We must use ApplicationDefault credentials for server-side auth.
            # This requires gcloud auth application-default login or being on GCP/GKE.
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, firebase_config)
            
        db = firestore.client()
        # MANDATORY PATH for public/shared data in this environment
        CONFIG_COLLECTION_PATH = f"artifacts/{APP_ID}/public/data/configuration_management"
        print("✅ Firestore successfully connected and initialized.")
    else:
        # If no config is provided by the environment, skip initialization
        print("🟡 Running in local/unsecured mode. Database connection is disabled.")
        print("[NOTE] To enable database functionality, run this script in an environment with the required Firebase configuration.")


except Exception as e:
    # This catches runtime errors during initialization (e.g., failed credential lookup)
    print(f"❌ Failed to initialize Firebase Admin SDK. Database connection is disabled. Error: {e}")
    db = None

# --- Core Parsing Logic (No Changes needed here) ---

def parse_config_file(file_path: str = 'app_config.ini') -> dict:
    """
    Reads the INI configuration file and extracts all key-value pairs 
    into a structured dictionary. Handles file reading errors gracefully.
    """
    config = ConfigParser()
    extracted_data = {}
    
    try:
        # Attempt to read the configuration file
        # NOTE: For local testing, ensure 'app_config.ini' is in the same directory.
        files_read = config.read(file_path)
        
        if not files_read:
            raise FileNotFoundError(f"Configuration file not found or empty: {file_path}")

        # Iterate through all sections and items
        for section in config.sections():
            extracted_data[section] = {}
            for key, value in config.items(section):
                extracted_data[section][key] = value

        return extracted_data
        
    except FileNotFoundError as e:
        print(f"[ERROR] Configuration File Error: {e}")
        return {}
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during parsing: {e}")
        return {}

# --- Database Operations ---

def save_config_to_db(config_data: dict) -> bool:
    """
    Saves the extracted configuration data to Firestore.
    """
    if not db:
        print("[DB ERROR] Firestore not initialized. Cannot save data.")
        return False
        
    try:
        # Set the document in the public collection path
        doc_ref = db.collection(CONFIG_COLLECTION_PATH).document(CONFIG_DOC_ID)
        doc_ref.set({"config": config_data})
        print(f"✅ Configuration successfully saved to Firestore at: {CONFIG_COLLECTION_PATH}/{CONFIG_DOC_ID}")
        return True
    except Exception as e:
        print(f"[DB ERROR] Could not save data to Firestore: {e}")
        return False

# --- Flask Routes (API Endpoints) ---

@app.route('/parse-and-save', methods=['POST'])
def parse_and_save_config():
    """
    API endpoint to trigger the configuration parsing and database save.
    """
    config_data = parse_config_file('app_config.ini') # Use the local config file
    
    if not config_data:
        return jsonify({"status": "error", "message": "Failed to parse configuration file. Check if 'app_config.ini' exists."}), 500
        
    # Attempt to save only if DB is initialized
    if db:
        save_success = save_config_to_db(config_data)
        message = "Configuration parsed and saved to database."
    else:
        # Treat as success if data parsed but DB is offline, and return the parsed data
        save_success = True 
        message = "Configuration parsed successfully but database is offline."
        
    if save_success:
        return jsonify({
            "status": "success", 
            "message": message,
            "data": config_data
        }), 200
    else:
        return jsonify({
            "status": "error", 
            "message": "Configuration parsed but failed to save to database."
        }), 500

@app.route('/get-config', methods=['GET'])
def get_config():
    """
    API endpoint to fetch the last saved configuration from the database.
    """
    if not db:
        return jsonify({"status": "error", "message": "Database not initialized. Cannot fetch data."}), 500
        
    try:
        doc_ref = db.collection(CONFIG_COLLECTION_PATH).document(CONFIG_DOC_ID)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            return jsonify({
                "status": "success", 
                "data": data.get("config", {}) # Extract the nested config dictionary
            }), 200
        else:
            return jsonify({"status": "error", "message": "Configuration data not found in database. Run POST first."}), 404
            
    except Exception as e:
        print(f"[DB ERROR] Could not fetch data from Firestore: {e}")
        return jsonify({"status": "error", "message": f"An error occurred fetching data: {e}"}), 500

# --- Execution Block ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3306))
    app.run(host='0.0.0.0', port=port, debug=False)