from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

# Initialize data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def read_data():
    """Read data from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def write_data(data):
    """Write data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

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
    
    people = read_data()
    
    new_person = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'name': data['name'],
        'details': data.get('details', ''),
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }
    
    people.append(new_person)
    write_data(people)
    
    return jsonify(new_person), 201

@app.route('/api/people/<person_id>', methods=['PUT'])
def update_person(person_id):
    """Update an existing person"""
    data = request.get_json()
    people = read_data()
    
    person_index = next((i for i, p in enumerate(people) if p['id'] == person_id), None)
    
    if person_index is None:
        return jsonify({'error': 'Person not found'}), 404
    
    person = people[person_index]
    person['name'] = data.get('name', person['name'])
    person['details'] = data.get('details', person.get('details', ''))
    person['updatedAt'] = datetime.now().isoformat()
    
    people[person_index] = person
    write_data(people)
    
    return jsonify(person)

@app.route('/api/people/<person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete a person"""
    people = read_data()
    original_length = len(people)
    
    people = [p for p in people if p['id'] != person_id]
    
    if len(people) == original_length:
        return jsonify({'error': 'Person not found'}), 404
    
    write_data(people)
    return jsonify({'message': 'Person deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

