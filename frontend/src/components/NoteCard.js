import React from 'react';
import { Link } from 'react-router-dom';

function NoteCard({ note, showVoting }) {
  return (
    <div className="note-card">
      <Link to={`/notes/${note.id}`} className="note-card-link">
        <h3>{note.title}</h3>
        <div className="note-card-meta">
          <span className="workspace">{note.workspace_name}</span>
          {note.company_name && <span className="company">{note.company_name}</span>}
          {note.is_draft && <span className="badge draft">Draft</span>}
          <span className="badge type">{note.note_type}</span>
        </div>
        <div className="tags">
          {note.tags?.slice(0, 3).map(tag => (
            <span key={tag.id} className="tag">{tag.name}</span>
          ))}
          {note.tags?.length > 3 && <span className="tag">+{note.tags.length - 3}</span>}
        </div>
        {showVoting && (
          <div className="vote-info">
            <span className="upvotes">↑ {note.upvotes || 0}</span>
            <span className="downvotes">↓ {note.downvotes || 0}</span>
          </div>
        )}
        <div className="note-date">
          {new Date(note.created_at).toLocaleDateString()}
        </div>
      </Link>
    </div>
  );
}

export default NoteCard;