from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
import json
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from functools import wraps
import google.generativeai as genai

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# App password (hashed) - Change this password!
# To set custom password, set APP_PASSWORD environment variable
# Default password: "admin123" (change this!)
APP_PASSWORD_HASH = bcrypt.generate_password_hash(
    os.environ.get('APP_PASSWORD', 'admin123')
).decode('utf-8')

# Configuration - Use MongoDB if MONGO_URI is set, otherwise use JSON file
MONGO_URI = os.environ.get('MONGO_URI')
USE_MONGODB = MONGO_URI is not None

# Google Gemini Configuration (optional - feature disabled if not set)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use gemini-2.5-flash (free tier, fast and stable)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    gemini_model = None

if USE_MONGODB:
    # MongoDB Setup
    client = MongoClient(MONGO_URI)
    db = client['people_manager']
    people_collection = db['people']
    print("✓ Connected to MongoDB")
else:
    # JSON File Setup
    DATA_FILE = 'data.json'
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    print("✓ Using JSON file storage")

def read_data():
    """Read data from MongoDB or JSON file"""
    if USE_MONGODB:
        people = list(people_collection.find())
        # Convert ObjectId to string for JSON serialization
        for person in people:
            person['_id'] = str(person['_id'])
            if 'id' not in person:
                person['id'] = person['_id']
        return people
    else:
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []

def write_data(data):
    """Write data to MongoDB or JSON file"""
    if USE_MONGODB:
        # MongoDB handles data differently, so this is not used
        pass
    else:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

def create_person(data):
    """Create a new person in MongoDB or JSON"""
    new_person = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'name': data['name'],
        'details': data.get('details', ''),
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }
    
    if USE_MONGODB:
        result = people_collection.insert_one(new_person)
        new_person['_id'] = str(result.inserted_id)
    else:
        people = read_data()
        people.append(new_person)
        write_data(people)
    
    return new_person

def update_person_data(person_id, data):
    """Update a person in MongoDB or JSON"""
    if USE_MONGODB:
        update_data = {
            'name': data.get('name'),
            'details': data.get('details', ''),
            'updatedAt': datetime.now().isoformat()
        }
        result = people_collection.find_one_and_update(
            {'id': person_id},
            {'$set': update_data},
            return_document=True
        )
        if result:
            result['_id'] = str(result['_id'])
            return result
        return None
    else:
        people = read_data()
        person_index = next((i for i, p in enumerate(people) if p['id'] == person_id), None)
        if person_index is None:
            return None
        
        person = people[person_index]
        person['name'] = data.get('name', person['name'])
        person['details'] = data.get('details', person.get('details', ''))
        person['updatedAt'] = datetime.now().isoformat()
        people[person_index] = person
        write_data(people)
        return person

def delete_person_data(person_id):
    """Delete a person from MongoDB or JSON"""
    if USE_MONGODB:
        result = people_collection.delete_one({'id': person_id})
        return result.deleted_count > 0
    else:
        people = read_data()
        original_length = len(people)
        people = [p for p in people if p['id'] != person_id]
        if len(people) == original_length:
            return False
        write_data(people)
        return True

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if bcrypt.check_password_hash(APP_PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/people', methods=['GET'])
@login_required
def get_people():
    """Get all people"""
    people = read_data()
    return jsonify(people)

@app.route('/api/people/<person_id>', methods=['GET'])
@login_required
def get_person(person_id):
    """Get a specific person by ID"""
    people = read_data()
    person = next((p for p in people if p['id'] == person_id), None)
    
    if person:
        return jsonify(person)
    return jsonify({'error': 'Person not found'}), 404

@app.route('/api/people/search/<query>', methods=['GET'])
@login_required
def search_people(query):
    """Search people by name"""
    people = read_data()
    query_lower = query.lower()
    
    results = [
        person for person in people
        if query_lower in person['name'].lower()
    ]
    
    return jsonify(results)

@app.route('/api/people', methods=['POST'])
@login_required
def add_person():
    """Add a new person"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    new_person = create_person(data)
    return jsonify(new_person), 201

@app.route('/api/people/<person_id>', methods=['PUT'])
@login_required
def update_person(person_id):
    """Update an existing person"""
    data = request.get_json()
    person = update_person_data(person_id, data)
    
    if person is None:
        return jsonify({'error': 'Person not found'}), 404
    
    return jsonify(person)

@app.route('/api/people/<person_id>', methods=['DELETE'])
@login_required
def delete_person(person_id):
    """Delete a person"""
    success = delete_person_data(person_id)
    
    if not success:
        return jsonify({'error': 'Person not found'}), 404
    
    return jsonify({'message': 'Person deleted successfully'})

@app.route('/api/people/<person_id>/summary', methods=['POST'])
@login_required
def generate_summary(person_id):
    """Generate AI summary for a person"""
    if not gemini_model:
        return jsonify({'error': 'AI feature not configured. Please set GEMINI_API_KEY environment variable.'}), 503
    
    people = read_data()
    person = next((p for p in people if p['id'] == person_id), None)
    
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    if not person.get('details'):
        return jsonify({'error': 'No details available to summarize'}), 400
    
    try:
        # Create prompt for the LLM
        prompt = f"""You are a personal assistant helping to summarize contact information.

Given the following raw details about a person named "{person['name']}", please create a clear, concise summary that:
1. Extracts key information (phone, email, address, etc.) if present
2. Summarizes main points from updates chronologically
3. Highlights important facts
4. Keeps it brief and easy to scan (3-5 bullet points max)

Raw Details:
{person['details']}

Please format the response as a clean summary without any introductory phrases like "Here's a summary" or "Based on the information". Just provide the key points directly."""

        # Call Google Gemini API with safety settings
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        response = gemini_model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Check if response has text
        if not response.text:
            return jsonify({'error': 'No summary generated. Please try again.'}), 500
        
        summary = response.text.strip()
        
        return jsonify({
            'summary': summary,
            'generated_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate summary: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

