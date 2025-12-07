import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notesAPI } from '../services/api';

function NoteDetailPage() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const [showHistory, setShowHistory] = useState(false);

  const { data: note, isLoading, error } = useQuery({
    queryKey: ['note', id],
    queryFn: () => notesAPI.getNote(id).then(res => res.data),
  });

  const { data: history } = useQuery({
    queryKey: ['noteHistory', id],
    queryFn: () => notesAPI.getNoteHistory(id).then(res => res.data),
    enabled: showHistory,
  });

  const voteMutation = useMutation({
    mutationFn: ({ noteId, voteType }) => notesAPI.voteNote(noteId, voteType),
    onSuccess: () => {
      queryClient.invalidateQueries(['note', id]);
    },
  });

  const restoreMutation = useMutation({
    mutationFn: ({ noteId, historyId }) => notesAPI.restoreNote(noteId, historyId),
    onSuccess: () => {
      queryClient.invalidateQueries(['note', id]);
      queryClient.invalidateQueries(['noteHistory', id]);
      setShowHistory(false);
    },
  });

  const handleVote = (voteType) => {
    voteMutation.mutate({ noteId: id, voteType });
  };

  const handleRestore = (historyId) => {
    if (window.confirm('Are you sure you want to restore this version?')) {
      restoreMutation.mutate({ noteId: id, historyId });
    }
  };

  if (isLoading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error.message}</div>;

  return (
    <div className="note-detail-page">
      <div className="note-header">
        <div>
          <h1>{note.title}</h1>
          <div className="note-meta">
            <span>By {note.created_by_name}</span>
            <span>in {note.workspace_name}</span>
            <span>{new Date(note.created_at).toLocaleDateString()}</span>
            {note.is_draft && <span className="badge">Draft</span>}
            <span className="badge">{note.note_type}</span>
          </div>
        </div>
        <div className="note-actions">
          {note.note_type === 'public' && !note.is_draft && (
            <div className="voting">
              <button 
                onClick={() => handleVote('upvote')}
                disabled={voteMutation.isPending}
              >
                ↑ {note.upvotes}
              </button>
              <button 
                onClick={() => handleVote('downvote')}
                disabled={voteMutation.isPending}
              >
                ↓ {note.downvotes}
              </button>
            </div>
          )}
          <Link to={`/notes/${id}/edit`} className="btn">Edit</Link>
          <button 
            onClick={() => setShowHistory(!showHistory)} 
            className="btn"
          >
            {showHistory ? 'Hide' : 'Show'} History
          </button>
        </div>
      </div>

      <div className="tags">
        {note.tags.map(tag => (
          <span key={tag.id} className="tag">{tag.name}</span>
        ))}
      </div>

      <div className="note-content">
        {note.content}
      </div>

      {showHistory && (
        <div className="history-section">
          <h2>Version History</h2>
          {history && history.length > 0 ? (
            <div className="history-list">
              {history.map(h => (
                <div key={h.id} className="history-item">
                  <div className="history-header">
                    <span>{new Date(h.changed_at).toLocaleString()}</span>
                    <span>by {h.changed_by_name}</span>
                    <button 
                      onClick={() => handleRestore(h.id)}
                      className="btn btn-sm"
                      disabled={restoreMutation.isPending}
                    >
                      Restore
                    </button>
                  </div>
                  <div className="history-content">
                    <h4>{h.title}</h4>
                    <p>{h.content.substring(0, 200)}...</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No history available</p>
          )}
        </div>
      )}
    </div>
  );
}

export default NoteDetailPage;