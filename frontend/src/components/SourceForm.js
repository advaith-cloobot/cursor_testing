import React, { useState, useEffect } from 'react';
import { accountsAPI } from '../services/api';
import './Modal.css';

const ARTIFACT_TYPES = [
  'SOW',
  'Proposal',
  'DesignDocument',
  'ProcessMap',
  'DiscoveryNotes',
  'Other'
];

const SourceForm = ({ repoId, onClose, onSave }) => {
  const [file, setFile] = useState(null);
  const [artifactType, setArtifactType] = useState('');
  const [linkType, setLinkType] = useState('internal');
  const [accountId, setAccountId] = useState('');
  const [accounts, setAccounts] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await accountsAPI.getAll();
      setAccounts(response.data);
    } catch (err) {
      console.error('Failed to load accounts:', err);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const ext = selectedFile.name.split('.').pop().toLowerCase();
      if (!['docx', 'pdf', 'png'].includes(ext)) {
        setError('Only .docx, .pdf, and .png files are allowed');
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!artifactType) {
      setError('Please select an artifact type');
      return;
    }

    if (linkType === 'account' && !accountId) {
      setError('Please select an account');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('artifact_type', artifactType);
      formData.append('is_internal', linkType === 'internal');
      if (linkType === 'account') {
        formData.append('account_id', accountId);
      }

      await onSave(formData);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload source');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add Source</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="file">File *</label>
            <input
              type="file"
              id="file"
              accept=".docx,.pdf,.png"
              onChange={handleFileChange}
              required
            />
            {file && <div className="file-info">Selected: {file.name}</div>}
          </div>
          <div className="form-group">
            <label htmlFor="artifact_type">Artifact Type *</label>
            <select
              id="artifact_type"
              value={artifactType}
              onChange={(e) => setArtifactType(e.target.value)}
              required
            >
              <option value="">Select artifact type</option>
              {ARTIFACT_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Linked To *</label>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  value="internal"
                  checked={linkType === 'internal'}
                  onChange={(e) => setLinkType(e.target.value)}
                />
                Internal
              </label>
              <label>
                <input
                  type="radio"
                  value="account"
                  checked={linkType === 'account'}
                  onChange={(e) => setLinkType(e.target.value)}
                />
                Account
              </label>
            </div>
            {linkType === 'account' && (
              <select
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                style={{ marginTop: '10px', width: '100%' }}
                required
              >
                <option value="">Select account</option>
                {accounts.map(account => (
                  <option key={account.id} value={account.id}>{account.name}</option>
                ))}
              </select>
            )}
          </div>
          {error && <div className="error-message">{error}</div>}
          <div className="modal-actions">
            <button type="button" onClick={onClose} disabled={loading}>Cancel</button>
            <button type="submit" disabled={loading}>
              {loading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SourceForm;

