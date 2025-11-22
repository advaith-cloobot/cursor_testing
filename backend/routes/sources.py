from flask import Blueprint, request, jsonify, current_app
from models import get_db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

sources_bp = Blueprint('sources', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_mime_type(filename):
    """Get MIME type based on file extension"""
    ext = filename.rsplit('.', 1)[1].lower()
    mime_types = {
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'pdf': 'application/pdf',
        'png': 'image/png'
    }
    return mime_types.get(ext, 'application/octet-stream')

@sources_bp.route('/repos/<int:repo_id>/sources', methods=['GET'])
def get_sources(repo_id):
    """Get all sources for a repo"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, a.name as account_name
        FROM sources s
        LEFT JOIN accounts a ON s.account_id = a.id
        WHERE s.repo_id = ?
        ORDER BY s.uploaded_at DESC
    ''', (repo_id,))
    
    sources = []
    for row in cursor.fetchall():
        linked_to = 'Internal' if row['is_internal'] else (row['account_name'] or 'Unknown')
        sources.append({
            'id': row['id'],
            'repo_id': row['repo_id'],
            'filename': row['filename'],
            'artifact_type': row['artifact_type'],
            'account_id': row['account_id'],
            'is_internal': bool(row['is_internal']),
            'size_bytes': row['size_bytes'],
            'mime_type': row['mime_type'],
            'uploaded_at': row['uploaded_at'],
            'linked_to': linked_to
        })
    
    conn.close()
    return jsonify(sources)

@sources_bp.route('/repos/<int:repo_id>/sources', methods=['POST'])
def create_source(repo_id):
    """Upload and create a new source"""
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    artifact_type = request.form.get('artifact_type')
    account_id = request.form.get('account_id')
    is_internal = request.form.get('is_internal', 'false').lower() == 'true'
    
    # Validation
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Only .docx, .pdf, .png are allowed'}), 400
    
    if not artifact_type:
        return jsonify({'error': 'Artifact type is required'}), 400
    
    # Validate account/internal exclusivity
    if is_internal and account_id:
        return jsonify({'error': 'Cannot set both account_id and is_internal'}), 400
    
    if not is_internal and not account_id:
        return jsonify({'error': 'Must specify either account_id or is_internal'}), 400
    
    # Verify repo exists
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM repos WHERE id = ?', (repo_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Repo not found'}), 404
    
    # Verify account exists if provided
    if account_id:
        cursor.execute('SELECT id FROM accounts WHERE id = ?', (account_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Account not found'}), 404
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    original_filename = secure_filename(file.filename)
    filename_parts = original_filename.rsplit('.', 1)
    stored_filename = f"{timestamp}_{filename_parts[0]}.{filename_parts[1]}"
    stored_path = stored_filename
    
    # Save file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_path)
    file.save(file_path)
    
    # Get file size
    size_bytes = os.path.getsize(file_path)
    mime_type = get_mime_type(file.filename)
    
    # Insert into database
    cursor.execute('''
        INSERT INTO sources (repo_id, filename, artifact_type, account_id, is_internal, size_bytes, mime_type, stored_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (repo_id, original_filename, artifact_type, account_id if not is_internal else None, 1 if is_internal else 0, size_bytes, mime_type, stored_path))
    
    source_id = cursor.lastrowid
    
    # Update repo updated_at
    cursor.execute('UPDATE repos SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (repo_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': source_id,
        'repo_id': repo_id,
        'filename': original_filename,
        'artifact_type': artifact_type,
        'account_id': account_id if not is_internal else None,
        'is_internal': is_internal,
        'size_bytes': size_bytes,
        'mime_type': mime_type,
        'uploaded_at': datetime.now().isoformat()
    }), 201

@sources_bp.route('/sources/<int:source_id>', methods=['DELETE'])
def delete_source(source_id):
    """Delete a source and its file"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get source info
    cursor.execute('SELECT stored_path FROM sources WHERE id = ?', (source_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'error': 'Source not found'}), 404
    
    # Delete file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], row['stored_path'])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete source
    cursor.execute('DELETE FROM sources WHERE id = ?', (source_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Source deleted successfully'}), 200

@sources_bp.route('/sources/<int:source_id>', methods=['PUT'])
def update_source(source_id):
    """Update source metadata"""
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get current source
    cursor.execute('SELECT * FROM sources WHERE id = ?', (source_id,))
    source = cursor.fetchone()
    
    if not source:
        conn.close()
        return jsonify({'error': 'Source not found'}), 404
    
    # Validate account/internal exclusivity
    account_id = data.get('account_id')
    is_internal = data.get('is_internal', False)
    
    if is_internal and account_id:
        conn.close()
        return jsonify({'error': 'Cannot set both account_id and is_internal'}), 400
    
    if not is_internal and not account_id:
        conn.close()
        return jsonify({'error': 'Must specify either account_id or is_internal'}), 400
    
    # Verify account exists if provided
    if account_id:
        cursor.execute('SELECT id FROM accounts WHERE id = ?', (account_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Account not found'}), 404
    
    # Update source
    artifact_type = data.get('artifact_type', source['artifact_type'])
    cursor.execute('''
        UPDATE sources
        SET artifact_type = ?, account_id = ?, is_internal = ?
        WHERE id = ?
    ''', (artifact_type, account_id if not is_internal else None, 1 if is_internal else 0, source_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Source updated successfully'}), 200

