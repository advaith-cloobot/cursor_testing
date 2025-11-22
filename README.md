# Knowledge Repository Management App

A React frontend with Flask backend application for managing knowledge repositories, accounts, and file sources.

## Features

- **Knowledge Repositories**: Create, edit, delete, and manage repositories
- **Accounts**: Global account management (clients/projects)
- **File Sources**: Upload files (.docx, .pdf, .png) and link them to accounts or mark as internal
- **Source Management**: Track artifact types, link sources to accounts or internal bucket

## Project Structure

```
cursor_testing/
├── frontend/          # React app (Create React App)
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   └── utils/         # Utility functions
│   └── package.json
├── backend/           # Flask API
│   ├── app.py         # Main Flask application
│   ├── models.py      # Database models
│   ├── routes/        # API route handlers
│   │   ├── repos.py
│   │   ├── accounts.py
│   │   └── sources.py
│   ├── database.db    # SQLite database (created on first run)
│   ├── uploads/       # Stored uploaded files
│   └── requirements.txt
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the Flask server:
   ```bash
   python app.py
   ```

   The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

   The frontend will run on `http://localhost:3000` and automatically open in your browser.

## API Endpoints

### Repositories
- `GET /api/repos` - List all repositories with source counts
- `GET /api/repos/<id>` - Get repository details
- `POST /api/repos` - Create a new repository
- `PUT /api/repos/<id>` - Update a repository
- `DELETE /api/repos/<id>` - Delete a repository (cascades to sources)

### Accounts
- `GET /api/accounts` - List all accounts
- `GET /api/accounts/<id>` - Get account details
- `POST /api/accounts` - Create a new account
- `PUT /api/accounts/<id>` - Update an account
- `DELETE /api/accounts/<id>` - Delete an account (if not linked to sources)

### Sources
- `GET /api/repos/<repo_id>/sources` - List all sources for a repository
- `POST /api/repos/<repo_id>/sources` - Upload and create a new source
- `PUT /api/sources/<id>` - Update source metadata
- `DELETE /api/sources/<id>` - Delete a source and its file

## Database Schema

### repos
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT NOT NULL)
- `description` (TEXT)
- `updated_at` (TIMESTAMP)

### accounts
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT NOT NULL)
- `industry` (TEXT)
- `notes` (TEXT)

### sources
- `id` (INTEGER PRIMARY KEY)
- `repo_id` (INTEGER NOT NULL, FOREIGN KEY)
- `filename` (TEXT NOT NULL)
- `artifact_type` (TEXT NOT NULL)
- `account_id` (INTEGER, FOREIGN KEY, nullable)
- `is_internal` (INTEGER DEFAULT 0)
- `size_bytes` (INTEGER)
- `mime_type` (TEXT)
- `stored_path` (TEXT NOT NULL)
- `uploaded_at` (TIMESTAMP)

## Artifact Types

- SOW
- Proposal
- DesignDocument
- ProcessMap
- DiscoveryNotes
- Other

## File Types Supported

- `.docx` - Microsoft Word documents
- `.pdf` - PDF documents
- `.png` - PNG images

## Test Cases

The application supports the following test scenarios:

1. **Create a New Repo and See It in the List**
   - Create a repo with name and description
   - Verify it appears in the list with source count = 0

2. **Create an Account and Use It While Uploading a Source**
   - Create an account
   - Upload a source and link it to the account
   - Verify the account appears in the "Linked To" column

3. **Upload a Source as "Internal" and Verify No Account Required**
   - Upload a source and mark it as Internal
   - Verify no account selection is required
   - Verify "Internal" appears in the "Linked To" column

4. **Delete a Repo and Confirm Its Sources Disappear**
   - Delete a repo with sources
   - Verify the repo and all its sources are removed

5. **Upload a Process Map Image and Verify Storage**
   - Upload a .png file with ProcessMap artifact type
   - Verify the file is stored and metadata is correct

## Development Notes

- The database is automatically created on first run
- Uploaded files are stored in `backend/uploads/` directory
- CORS is enabled for the React development server
- Maximum file size is 16MB

## Technologies Used

- **Frontend**: React, React Router, Axios
- **Backend**: Flask, SQLite, Flask-CORS
- **File Handling**: Werkzeug
