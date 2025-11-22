from flask import Blueprint, request, jsonify
from models import get_db

repos_bp = Blueprint('repos', __name__)

@repos_bp.route('/repos', methods=['GET'])
def get_repos():
    """Get all repos with source counts"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, COUNT(s.id) as source_count
        FROM repos r
        LEFT JOIN sources s ON r.id = s.repo_id
        GROUP BY r.id
        ORDER BY r.updated_at DESC
    ''')
    
    repos = []
    for row in cursor.fetchall():
        repos.append({
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'updated_at': row['updated_at'],
            'source_count': row['source_count']
        })
    
    conn.close()
    return jsonify(repos)

@repos_bp.route('/repos/<int:repo_id>', methods=['GET'])
def get_repo(repo_id):
    """Get a single repo by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, COUNT(s.id) as source_count
        FROM repos r
        LEFT JOIN sources s ON r.id = s.repo_id
        WHERE r.id = ?
        GROUP BY r.id
    ''', (repo_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'updated_at': row['updated_at'],
            'source_count': row['source_count']
        })
    else:
        return jsonify({'error': 'Repo not found'}), 404

@repos_bp.route('/repos', methods=['POST'])
def create_repo():
    """Create a new repo"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Repo name is required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO repos (name, description)
        VALUES (?, ?)
    ''', (data['name'], data.get('description', '')))
    
    repo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': repo_id,
        'name': data['name'],
        'description': data.get('description', ''),
        'source_count': 0
    }), 201

@repos_bp.route('/repos/<int:repo_id>', methods=['PUT'])
def update_repo(repo_id):
    """Update a repo"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Repo name is required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE repos
        SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (data['name'], data.get('description', ''), repo_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Repo not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Repo updated successfully'}), 200

@repos_bp.route('/repos/<int:repo_id>', methods=['DELETE'])
def delete_repo(repo_id):
    """Delete a repo and cascade delete its sources"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get sources to delete their files
    cursor.execute('SELECT stored_path FROM sources WHERE repo_id = ?', (repo_id,))
    sources = cursor.fetchall()
    
    # Delete files
    import os
    from flask import current_app
    for source in sources:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], source['stored_path'])
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Delete repo (sources will be cascade deleted)
    cursor.execute('DELETE FROM repos WHERE id = ?', (repo_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Repo not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Repo deleted successfully'}), 200

