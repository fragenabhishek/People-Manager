# People Manager

A modern web application built with Python Flask to manage people's information with a beautiful and intuitive interface.

## Features

- ✨ **Add New People**: Store information including name, initials, email, phone, and description
- 🔍 **Search Functionality**: Search people by name, initials, or description
- ✏️ **Update Records**: Edit existing person's information
- 🗑️ **Delete Records**: Remove people from the database
- 💾 **Persistent Storage**: Data stored in JSON format
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations

## Installation

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure Python 3.7+ is installed

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Adding a Person
1. Click the "Add New Person" button
2. Fill in the form with:
   - Initial (required) - e.g., "JD"
   - Full Name (required) - e.g., "John Doe"
   - Email (optional)
   - Phone (optional)
   - Description (optional)
3. Click "Save Person"

### Searching for People
- Type in the search bar at the top
- Results will filter in real-time
- Search works across name, initials, and description

### Editing a Person
1. Click the "Edit" button on any person card
2. Modify the information
3. Click "Save Person"

### Deleting a Person
1. Click the "Delete" button on any person card
2. Confirm the deletion

## Project Structure

```
people-manager/
│
├── app.py                 # Flask backend (REST API)
├── data.json             # Data storage (auto-generated)
├── requirements.txt      # Python dependencies
├── README.md            # This file
│
├── templates/
│   └── index.html       # Main HTML template
│
└── static/
    ├── style.css        # Styles and design
    └── script.js        # Frontend JavaScript
```

## API Endpoints

- `GET /api/people` - Get all people
- `GET /api/people/<id>` - Get specific person
- `GET /api/people/search/<query>` - Search people
- `POST /api/people` - Add new person
- `PUT /api/people/<id>` - Update person
- `DELETE /api/people/<id>` - Delete person

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Storage**: JSON file-based database

## Features Highlights

### Backend (Python Flask)
- RESTful API design
- JSON-based data persistence
- Error handling
- CORS support for API calls

### Frontend
- Responsive design
- Modern gradient UI
- Smooth animations
- Real-time search
- Modal forms for add/edit

## Customization

You can customize the appearance by editing `static/style.css`:
- Change color scheme (modify CSS variables in `:root`)
- Adjust card layouts
- Modify animations
- Update gradients

## Future Enhancements

Potential features to add:
- Database integration (SQLite, PostgreSQL)
- User authentication
- Profile pictures
- Export to CSV/PDF
- Advanced filtering
- Dark mode toggle
- Tags/Categories

## License

MIT License - Feel free to use and modify as needed!

