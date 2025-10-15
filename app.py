from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Configuration - Use MongoDB if MONGO_URI is set, otherwise use JSON file
MONGO_URI = os.environ.get('MONGO_URI')
USE_MONGODB = MONGO_URI is not None

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

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/people', methods=['GET'])
def get_people():
    """Get all people"""
    people = read_data()
    return jsonify(people)

@app.route('/api/people/<person_id>', methods=['GET'])
def get_person(person_id):
    """Get a specific person by ID"""
    people = read_data()
    person = next((p for p in people if p['id'] == person_id), None)
    
    if person:
        return jsonify(person)
    return jsonify({'error': 'Person not found'}), 404

@app.route('/api/people/search/<query>', methods=['GET'])
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
def add_person():
    """Add a new person"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    new_person = create_person(data)
    return jsonify(new_person), 201

@app.route('/api/people/<person_id>', methods=['PUT'])
def update_person(person_id):
    """Update an existing person"""
    data = request.get_json()
    person = update_person_data(person_id, data)
    
    if person is None:
        return jsonify({'error': 'Person not found'}), 404
    
    return jsonify(person)

@app.route('/api/people/<person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete a person"""
    success = delete_person_data(person_id)
    
    if not success:
        return jsonify({'error': 'Person not found'}), 404
    
    return jsonify({'message': 'Person deleted successfully'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

