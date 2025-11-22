import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { reposAPI, sourcesAPI } from '../services/api';
import { formatDate } from '../utils/formatDate';
import SourceForm from '../components/SourceForm';
import './Pages.css';

const RepoDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [repo, setRepo] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSourceForm, setShowSourceForm] = useState(false);

  useEffect(() => {
    loadRepo();
    loadSources();
  }, [id]);

  const loadRepo = async () => {
    try {
      const response = await reposAPI.getById(id);
      setRepo(response.data);
    } catch (error) {
      console.error('Failed to load repo:', error);
      alert('Failed to load repository');
      navigate('/');
    }
  };

  const loadSources = async () => {
    try {
      const response = await sourcesAPI.getByRepo(id);
      setSources(response.data);
    } catch (error) {
      console.error('Failed to load sources:', error);
      alert('Failed to load sources');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSource = () => {
    setShowSourceForm(true);
  };

  const handleSaveSource = async (formData) => {
    try {
      await sourcesAPI.create(id, formData);
      setShowSourceForm(false);
      loadSources();
      loadRepo(); // Refresh repo to update source count
    } catch (error) {
      throw error; // Let SourceForm handle the error
    }
  };

  const handleDeleteSource = async (source) => {
    if (!window.confirm(`Are you sure you want to delete "${source.filename}"?`)) {
      return;
    }

    try {
      await sourcesAPI.delete(source.id);
      loadSources();
      loadRepo(); // Refresh repo to update source count
    } catch (error) {
      console.error('Failed to delete source:', error);
      alert(error.response?.data?.error || 'Failed to delete source');
    }
  };

  if (loading) {
    return <div className="loading">Loading repository...</div>;
  }

  if (!repo) {
    return <div className="loading">Repository not found</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <button className="back-button" onClick={() => navigate('/')}>
            ← Back to Repos
          </button>
          <h1>{repo.name}</h1>
          {repo.description && <p className="repo-description">{repo.description}</p>}
          <p className="repo-stats">Sources: {repo.source_count || 0}</p>
        </div>
        <button className="primary-button" onClick={handleAddSource}>
          Add Source
        </button>
      </div>

      {sources.length === 0 ? (
        <div className="empty-state">
          <p>No sources yet. Add your first source to get started.</p>
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Filename</th>
              <th>Artifact Type</th>
              <th>Linked To</th>
              <th>Uploaded At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sources.map(source => (
              <tr key={source.id}>
                <td>{source.filename}</td>
                <td>{source.artifact_type}</td>
                <td>{source.linked_to}</td>
                <td>{formatDate(source.uploaded_at)}</td>
                <td>
                  <button
                    onClick={() => handleDeleteSource(source)}
                    className="action-button delete"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showSourceForm && (
        <SourceForm
          repoId={id}
          onClose={() => setShowSourceForm(false)}
          onSave={handleSaveSource}
        />
      )}
    </div>
  );
};

export default RepoDetail;

