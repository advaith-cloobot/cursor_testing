import React, { useState, useEffect } from 'react';
import { accountsAPI } from '../services/api';
import AccountForm from '../components/AccountForm';
import './Pages.css';

const AccountsList = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const response = await accountsAPI.getAll();
      setAccounts(response.data);
    } catch (error) {
      console.error('Failed to load accounts:', error);
      alert('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingAccount(null);
    setShowForm(true);
  };

  const handleEdit = (account) => {
    setEditingAccount(account);
    setShowForm(true);
  };

  const handleSave = async (data) => {
    try {
      if (editingAccount) {
        await accountsAPI.update(editingAccount.id, data);
      } else {
        await accountsAPI.create(data);
      }
      setShowForm(false);
      setEditingAccount(null);
      loadAccounts();
    } catch (error) {
      console.error('Failed to save account:', error);
      alert(error.response?.data?.error || 'Failed to save account');
    }
  };

  const handleDelete = async (account) => {
    if (!window.confirm(`Are you sure you want to delete "${account.name}"?`)) {
      return;
    }

    try {
      await accountsAPI.delete(account.id);
      loadAccounts();
    } catch (error) {
      console.error('Failed to delete account:', error);
      alert(error.response?.data?.error || 'Failed to delete account');
    }
  };

  if (loading) {
    return <div className="loading">Loading accounts...</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Accounts</h1>
        <button className="primary-button" onClick={handleCreate}>
          Create Account
        </button>
      </div>

      {accounts.length === 0 ? (
        <div className="empty-state">
          <p>No accounts yet. Create your first account to get started.</p>
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Account Name</th>
              <th>Industry</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {accounts.map(account => (
              <tr key={account.id}>
                <td>{account.name}</td>
                <td>{account.industry || '-'}</td>
                <td>{account.notes || '-'}</td>
                <td>
                  <div className="action-buttons">
                    <button onClick={() => handleEdit(account)} className="action-button">Edit</button>
                    <button onClick={() => handleDelete(account)} className="action-button delete">Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showForm && (
        <AccountForm
          account={editingAccount}
          onClose={() => {
            setShowForm(false);
            setEditingAccount(null);
          }}
          onSave={handleSave}
        />
      )}
    </div>
  );
};

export default AccountsList;

