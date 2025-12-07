import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { notesAPI } from '../services/api';

function NoteEditorPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    title: '',
    content: '',
    note_type: 'private',
    is_draft: false,
    workspace: '',
    tag_names: [],
  });

  const [tagInput, setTagInput] = useState('');

  // Fetch workspaces for dropdown
  const { data: workspaces } = useQuery({
    queryKey: ['workspaces'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/workspaces/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      return data.results || data;
    },
  });

  const { data: note } = useQuery({
    queryKey: ['note', id],
    queryFn: () => notesAPI.getNote(id).then(res => res.data),
    enabled: isEdit,
  });

  useEffect(() => {
    if (note) {
      setFormData({
        title: note.title,
        content: note.content,
        note_type: note.note_type,
        is_draft: note.is_draft,
        workspace: note.workspace,
        tag_names: note.tags.map(t => t.name),
      });
    }
  }, [note]);

  const saveMutation = useMutation({
    mutationFn: (data) => 
      isEdit ? notesAPI.updateNote(id, data) : notesAPI.createNote(data),
    onSuccess: () => {
      navigate('/my-notes');
    },
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tag_names.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tag_names: [...prev.tag_names, tagInput.trim()],
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag) => {
    setFormData(prev => ({
      ...prev,
      tag_names: prev.tag_names.filter(t => t !== tag),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    saveMutation.mutate(formData);
  };

  const handleSaveDraft = () => {
    saveMutation.mutate({ ...formData, is_draft: true });
  };

  return (
    <div className="note-editor-page">
      <h1>{isEdit ? 'Edit Note' : 'Create Note'}</h1>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Title *</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="Enter note title"
          />
        </div>

        <div className="form-group">
          <label>Content *</label>
          <textarea
            name="content"
            value={formData.content}
            onChange={handleChange}
            required
            rows="15"
            placeholder="Write your note content here..."
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Workspace *</label>
            <select 
              name="workspace" 
              value={formData.workspace} 
              onChange={handleChange}
              required
            >
              <option value="">Select a workspace</option>
              {workspaces?.map(ws => (
                <option key={ws.id} value={ws.id}>
                  {ws.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Type</label>
            <select name="note_type" value={formData.note_type} onChange={handleChange}>
              <option value="private">Private</option>
              <option value="public">Public</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              name="is_draft"
              checked={formData.is_draft}
              onChange={handleChange}
            />
            Save as Draft
          </label>
        </div>

        <div className="form-group">
          <label>Tags</label>
          <div className="tag-input">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
              placeholder="Add tag and press Enter"
            />
            <button type="button" onClick={handleAddTag}>Add</button>
          </div>
          <div className="tags">
            {formData.tag_names.map(tag => (
              <span key={tag} className="tag">
                {tag}
                <button type="button" onClick={() => handleRemoveTag(tag)}>×</button>
              </span>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <button 
            type="button" 
            onClick={() => navigate('/my-notes')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button 
            type="button" 
            onClick={handleSaveDraft}
            className="btn btn-outline"
            disabled={saveMutation.isPending}
          >
            Save as Draft
          </button>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={saveMutation.isPending}
          >
            {isEdit ? 'Update' : 'Create'} Note
          </button>
        </div>

        {saveMutation.isError && (
          <div className="error">
            Error saving note: {saveMutation.error.message}
          </div>
        )}
      </form>
    </div>
  );
}

export default NoteEditorPage;