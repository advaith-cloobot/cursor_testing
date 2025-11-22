from flask import Blueprint, request, jsonify
from models import get_db

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM accounts ORDER BY name')
    
    accounts = []
    for row in cursor.fetchall():
        accounts.append({
            'id': row['id'],
            'name': row['name'],
            'industry': row['industry'],
            'notes': row['notes']
        })
    
    conn.close()
    return jsonify(accounts)

@accounts_bp.route('/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    """Get a single account by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'id': row['id'],
            'name': row['name'],
            'industry': row['industry'],
            'notes': row['notes']
        })
    else:
        return jsonify({'error': 'Account not found'}), 404

@accounts_bp.route('/accounts', methods=['POST'])
def create_account():
    """Create a new account"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Account name is required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO accounts (name, industry, notes)
        VALUES (?, ?, ?)
    ''', (data['name'], data.get('industry', ''), data.get('notes', '')))
    
    account_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': account_id,
        'name': data['name'],
        'industry': data.get('industry', ''),
        'notes': data.get('notes', '')
    }), 201

@accounts_bp.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    """Update an account"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Account name is required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE accounts
        SET name = ?, industry = ?, notes = ?
        WHERE id = ?
    ''', (data['name'], data.get('industry', ''), data.get('notes', ''), account_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Account not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Account updated successfully'}), 200

@accounts_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account (check if used in sources)"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if account is used in sources
    cursor.execute('SELECT COUNT(*) as count FROM sources WHERE account_id = ?', (account_id,))
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete account: it is linked to sources'}), 400
    
    cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Account not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Account deleted successfully'}), 200

