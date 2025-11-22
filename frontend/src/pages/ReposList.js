import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { reposAPI } from '../services/api';
import { formatDate } from '../utils/formatDate';
import RepoForm from '../components/RepoForm';
import './Pages.css';

const ReposList = () => {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingRepo, setEditingRepo] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadRepos();
  }, []);

  const loadRepos = async () => {
    try {
      setLoading(true);
      const response = await reposAPI.getAll();
      setRepos(response.data);
    } catch (error) {
      console.error('Failed to load repos:', error);
      alert('Failed to load repositories');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingRepo(null);
    setShowForm(true);
  };

  const handleEdit = (repo) => {
    setEditingRepo(repo);
    setShowForm(true);
  };

  const handleSave = async (data) => {
    try {
      if (editingRepo) {
        await reposAPI.update(editingRepo.id, data);
      } else {
        await reposAPI.create(data);
      }
      setShowForm(false);
      setEditingRepo(null);
      loadRepos();
    } catch (error) {
      console.error('Failed to save repo:', error);
      alert(error.response?.data?.error || 'Failed to save repository');
    }
  };

  const handleDelete = async (repo) => {
    if (!window.confirm(`Are you sure you want to delete "${repo.name}"? This will also delete all its sources.`)) {
      return;
    }

    try {
      await reposAPI.delete(repo.id);
      loadRepos();
    } catch (error) {
      console.error('Failed to delete repo:', error);
      alert(error.response?.data?.error || 'Failed to delete repository');
    }
  };

  const handleOpen = (repo) => {
    navigate(`/repos/${repo.id}`);
  };

  if (loading) {
    return <div className="loading">Loading repositories...</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Knowledge Repositories</h1>
        <button className="primary-button" onClick={handleCreate}>
          Create Repo
        </button>
      </div>

      {repos.length === 0 ? (
        <div className="empty-state">
          <p>No repositories yet. Create your first repository to get started.</p>
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Repo Name</th>
              <th>Description</th>
              <th>#Sources</th>
              <th>Last Updated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {repos.map(repo => (
              <tr key={repo.id}>
                <td>{repo.name}</td>
                <td>{repo.description || '-'}</td>
                <td>{repo.source_count || 0}</td>
                <td>{formatDate(repo.updated_at)}</td>
                <td>
                  <div className="action-buttons">
                    <button onClick={() => handleOpen(repo)} className="action-button">Open</button>
                    <button onClick={() => handleEdit(repo)} className="action-button">Edit</button>
                    <button onClick={() => handleDelete(repo)} className="action-button delete">Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showForm && (
        <RepoForm
          repo={editingRepo}
          onClose={() => {
            setShowForm(false);
            setEditingRepo(null);
          }}
          onSave={handleSave}
        />
      )}
    </div>
  );
};

export default ReposList;

