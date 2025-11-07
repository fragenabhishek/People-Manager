# People Manager

A simple and modern web application built with Python Flask to manage people's information.

🌐 **Live Demo**: [https://people-manager-kebr.onrender.com/](https://people-manager-kebr.onrender.com/)

## Features

- ✨ **Add People**: Store name and details/summary for each person
- 🔍 **Search**: Search people by name in real-time
- 👁️ **View Details**: Click on any person's name to view their details
- ✏️ **Update**: Edit person's information with timestamped updates
- 🗑️ **Delete**: Remove people from the database
- 🧠 **AI Person Blueprint**: Generate comprehensive personality profiles including:
  - Key contact information
  - Who they are and their background
  - Personality traits and communication style
  - How to approach and interact with them
  - Relationship timeline and important moments
  - Quick insights and key takeaways
- 💬 **Central AI Q&A**: Ask questions about any person from one powerful interface:
  - "Who did I meet this week?"
  - "Who should I follow up with?"
  - "Who are my AI/ML contacts?"
  - "When did I meet Sarah?"
  - Searches across all your contacts intelligently
- 💾 **Cloud Storage**: Data stored in MongoDB Atlas (cloud database) or JSON file (local)
- 🔐 **Password Protected**: Secure login system
- 🎨 **Modern UI**: Clean, minimalist design with smooth animations

## Quick Start (Local Development)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/fragenabhishek/People-Manager.git
   cd People-Manager
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   python app.py
   ```

4. **Open your browser**:
   ```
   http://localhost:5000
   ```

The app will use JSON file storage locally. To use MongoDB, set the `MONGO_URI` environment variable.

## Usage

### Adding a Person
1. Click "Add New Person"
2. Enter name (required) and details/summary (optional)
3. Click "Save Person"

### Viewing Details
- Click on any person's name to expand and view their details

### Searching
- Type in the search bar to find people by name
- Results update in real-time

### Editing
1. Click "Edit" on any person card
2. Modify the information
3. Click "Save Person"

### Deleting
1. Click "Delete" on any person card
2. Confirm deletion

## Project Structure

```
people-manager/
├── app.py              # Flask backend + MongoDB support
├── requirements.txt    # Python dependencies
├── render.yaml         # Render.com deployment config
├── data.json          # Local JSON storage (fallback)
├── templates/
│   └── index.html     # Main UI
└── static/
    ├── script.js      # Frontend logic
    └── style.css      # Styling
```

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### People Management
- `GET /` - Main UI (requires authentication)
- `GET /api/people` - Get all people
- `GET /api/people/<id>` - Get specific person
- `GET /api/people/search/<query>` - Search by name
- `POST /api/people` - Add new person
- `PUT /api/people/<id>` - Update person
- `DELETE /api/people/<id>` - Delete person

### AI Features (requires GEMINI_API_KEY)
- `POST /api/people/<id>/summary` - Generate comprehensive person blueprint
- `POST /api/ask` - **Central Q&A** - Ask questions about any person or across all contacts

## Technologies Used

- **Backend**: Python 3.11, Flask 3.0
- **Database**: MongoDB Atlas (cloud) / JSON file (local)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Hosting**: Render.com (free tier)
- **Server**: Gunicorn

## Technical Highlights

- RESTful API design
- Dual storage support (MongoDB + JSON fallback)
- Click-to-expand details UI pattern
- Real-time search
- Responsive design
- Modern gradient aesthetics

## Deployment

The app is deployed on Render.com with MongoDB Atlas. It automatically detects the environment:

- **With MONGO_URI**: Uses MongoDB cloud database
- **Without MONGO_URI**: Uses local JSON file storage

To deploy your own:
1. Fork this repository
2. Create a MongoDB Atlas cluster (free tier)
3. Create a new web service on Render.com
4. Connect your GitHub repo
5. Add environment variable: `MONGO_URI` with your MongoDB connection string
6. Deploy!

## Environment Variables

- `MONGO_URI` (optional) - MongoDB connection string
- `PORT` (auto-set by Render) - Server port

## License

MIT License - Feel free to use and modify!

