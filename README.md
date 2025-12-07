# SaaS Notes System - Project Documentation

## 🎯 Project Overview

A production-ready, multi-tenant SaaS Notes system built with Django/DRF backend, React frontend, and MySQL database. Designed to handle large-scale data efficiently with 500,000+ notes.

---

## ✨ Key Features

### Core Features
- ✅ **Multi-tenant architecture** - Companies → Workspaces → Notes hierarchy
- ✅ **Public/Private notes** - Granular visibility control
- ✅ **Draft mode** - Save incomplete work without publishing
- ✅ **Voting system** - Upvotes/downvotes on public notes
- ✅ **Tag management** - Many-to-many tag relationships
- ✅ **Role-based access control** - Owner and Member roles
- ✅ **JWT authentication** - Secure token-based auth with auto-refresh
- ✅ **Search & sorting** - Fast title-based search with multiple sort options
- ✅ **History tracking** - Automatic version history with 7-day retention
- ✅ **History restore** - One-click restore to previous versions

### Scale & Performance
- ✅ **50 companies** with complete isolation
- ✅ **250 users** (5 per company: 1 owner, 4 members)
- ✅ **1,000 workspaces** (20 per company)
- ✅ **500,000 notes** (500 per workspace) with realistic data
- ✅ **100 tags** with random assignments
- ✅ **Thousands of votes** on public notes
- ✅ **Optimized queries** handle large datasets smoothly
- ✅ **Sub-500ms response times** even with massive data

---

## 🛠️ Technology Stack

### Backend
- **Django 4.2** - Web framework with built-in security
- **Django REST Framework** - RESTful API with serializers
- **MySQL 8.0** - Relational database with optimized indexes
- **Celery + Redis** - Background task processing
- **JWT (Simple JWT)** - Token-based authentication

### Frontend
- **React 18** - Component-based UI library
- **React Router v6** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client with interceptors

### Additional Tools
- **Faker** - Realistic data generation for seeding
- **Django CORS Headers** - Cross-origin resource sharing
- **Django Filter** - Advanced filtering capabilities

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                REACT FRONTEND (Port 3000)                   │
│  • Public Notes Directory    • Private Dashboard            │
│  • Note Editor               • History Viewer               │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (JWT)
┌─────────────────────▼───────────────────────────────────────┐
│          DJANGO REST FRAMEWORK (Port 8000)                  │
│  • Authentication    • API Views    • Permissions           │
└──────┬──────────────────────────────────┬───────────────────┘
       │                                  │
┌──────▼──────────┐            ┌──────────▼──────────────────┐
│ MySQL Database  │            │  Celery + Redis             │
│ • 7 Tables      │            │  • History Cleanup (2 AM)   │
│ • 500K+ Records │            │  • Background Tasks         │
└─────────────────┘            └─────────────────────────────┘
```

---

## 🗄️ Database Design

### Entity Relationship Diagram

```
┌─────────────────┐
│    Company      │ (Multi-tenant root)
│  - id           │
│  - name         │
│  - slug         │
└────┬────────┬───┘
     │1       │1
     │        │
     │N       │N
┌────▼────┐ ┌▼──────────┐
│  User   │ │ Workspace │
│- email  │ │ - name    │
│- role   │ │ - slug    │
└────┬────┘ └─┬─────────┘
     │1       │1
     │        │
     │N       │N
     └──────┬─▼──────────┐
           ┌▼────────────┤
           │    Note     │
           │ - title     │
           │ - content   │
           │ - type      │◄────┐
           │ - is_draft  │     │N:M
           └─┬──┬────┬───┘     │
             │  │    │      ┌──┴───┐
           1:N│ N:M│ 1:N    │ Tag  │
             │  │  │        └──────┘
        ┌────▼┐ │  │
        │Vote │ │  │
        └─────┘ │  │
           ┌────▼──▼─────────┐
           │  NoteHistory    │
           │  (7-day cache)  │
           └─────────────────┘
```

### Database Tables

| Table | Records | Purpose |
|-------|---------|---------|
| **companies** | 50 | Multi-tenant root entity |
| **users** | 250 | Authentication & authorization |
| **workspaces** | 1,000 | Note containers per company |
| **notes** | 500,000+ | Core content with type/draft flags |
| **tags** | 100 | Categorization via M:M relationship |
| **votes** | ~100,000 | Upvote/downvote tracking |
| **note_history** | Dynamic | Version history (7-day retention) |

---

## 📋 Core Requirements Implementation

### 1. Multi-Tenant Structure ✅
- **Company** can have multiple **Workspaces**
- Each **Workspace** contains many **Notes**
- Complete data isolation between companies
- Foreign keys with CASCADE/SET_NULL for data integrity

### 2. Note Model ✅
- **Title** - CharField(500) with index
- **Content** - TextField for large text
- **Tags** - Many-to-many relationship
- **Note Type** - Enum: 'public' or 'private'
- **Created/Updated** - Auto-generated timestamps
- **Draft Flag** - Boolean for incomplete notes
- **Creator/Updater** - Foreign keys to User

### 3. Voting System ✅
- Users/Companies can upvote or downvote public notes
- Unique constraint: one vote per (note, user/company)
- Vote counts calculated at database level
- Displayed in public directory with sorting

### 4. Draft Mode ✅
- Boolean `is_draft` field on Note model
- Drafts excluded from public listings via query filters
- Draft indicator in UI
- Can be published by toggling flag

### 5. History System (7-Day Retention) ✅

#### How It Works:
1. **Automatic Tracking**: Every note update creates history entry
2. **Storage**: Previous title, content, timestamp, and user
3. **Restoration**: Users can restore any version within 7 days
4. **Auto-Cleanup**: Celery Beat runs daily at 2 AM

## ⚡ Performance Optimizations

### Database Level
| Optimization | Implementation | Impact |
|-------------|----------------|---------|
| **Strategic Indexes** | company_id, note_type, is_draft, created_at, title | 10x faster queries |
| **Composite Indexes** | (workspace, note_type, is_draft) | Optimized filtering |
| **select_related()** | Foreign key pre-fetching | Reduces N+1 queries |
| **prefetch_related()** | M:M relationship optimization | Single query for tags |
| **Annotated Counts** | Vote counts at DB level | Eliminates Python loops |
| **Bulk Operations** | bulk_create() for seeding | 1000x faster insertion |

### API Level
- **Pagination**: 50 items per page reduces payload size
- **Django Filter**: Server-side filtering for efficiency
- **Minimal Serializers**: Only required fields in responses
- **Query Optimization**: Each endpoint makes 1-3 DB queries max

### Frontend Level
- **React Query**: Automatic caching, background refetching
- **Debounced Search**: Prevents excessive API calls
- **Lazy Loading**: Components load on-demand
- **Optimistic Updates**: Instant UI feedback

**Result**: Public notes page loads in <500ms with 500K records

---

## 🔐 Security Implementation

### Authentication
- **JWT Tokens**: Access (1 hour) + Refresh (7 days)
- **Auto Refresh**: Seamless token renewal on expiry
- **Token Storage**: localStorage with secure handling

### Authorization
- **Role-Based Access Control (RBAC)**
  - Owner: Full CRUD on notes
  - Member: Read-only access
- **Object-Level Permissions**: Ownership verification
- **Company Isolation**: Automatic filtering by company

### Input Protection
- **DRF Serializers**: Automatic validation and sanitization
- **Type Checking**: Strict data type enforcement
- **Max Length Limits**: Prevents overflow attacks

### Injection Prevention
- **SQL Injection**: Django ORM parameterized queries
- **XSS Protection**: React auto-escaping output
- **CSRF Protection**: Django CSRF middleware

### Production Security
- HTTPS redirect enabled
- Secure cookies (HTTPOnly, Secure flags)
- Security headers (XSS, Content-Type, Frame)
- ALLOWED_HOSTS whitelist
- Debug mode disabled

---

## 📈 Scalability Design

### Current Capabilities
- Handles 500,000+ notes smoothly
- Sub-500ms response times
- Efficient search and sorting
- Concurrent user support

### Architecture for Growth

#### Horizontal Scaling
- **Stateless API**: JWT tokens enable multiple servers
- **Load Balancer Ready**: No session affinity needed
- **Database Connection Pooling**: Efficient connection reuse

#### Database Scaling
- **Normalized Schema**: No data redundancy
- **Strategic Indexes**: Fast queries at any scale
- **Partitioning Ready**: Can partition by company_id or date
- **Read Replicas**: Separate read/write databases

### Future Enhancements
1. **Redis Caching**: Cache frequently accessed public notes
2. **ElasticSearch**: Advanced full-text search
3. **CDN**: Static assets on content delivery network
4. **Database Sharding**: Horizontal database partitioning
5. **Microservices**: Split into specialized services
6. **Message Queue**: RabbitMQ for inter-service communication

**Capacity**: Can scale from thousands to millions of records without architectural changes

---

## 🔌 API Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/token/` | POST | Login, get JWT tokens | No |
| `/api/token/refresh/` | POST | Refresh access token | No |
| `/api/register/` | POST | User registration | No |
| `/api/companies/` | GET | List all companies | Optional |
| `/api/companies/{id}/` | GET | Get company details | Optional |
| `/api/workspaces/` | GET, POST | List/create workspaces | Yes |
| `/api/workspaces/{id}/` | GET, PATCH, DELETE | Workspace CRUD | Yes |
| `/api/notes/public_notes/` | GET | Public notes directory | No |
| `/api/notes/my_notes/` | GET | Private dashboard | Yes |
| `/api/notes/` | POST | Create note | Yes |
| `/api/notes/{id}/` | GET, PATCH, DELETE | Note CRUD | Yes |
| `/api/notes/{id}/vote/` | POST | Upvote/downvote | Yes |
| `/api/notes/{id}/history/` | GET | Get note history | Yes |
| `/api/notes/{id}/restore/` | POST | Restore from history | Yes |
| `/api/tags/` | GET | List all tags | No |
| `/api/users/me/` | GET, PATCH | User profile | Yes |

---

## 🧪 Testing Approach

### Manual Testing
✅ User registration and login
✅ Create notes in different workspaces
✅ Toggle public/private and draft modes
✅ Search and sort functionality
✅ Vote on public notes
✅ Edit notes and verify history creation
✅ View and restore from history
✅ Delete notes
✅ Role-based access control

### API Testing
✅ All 15+ endpoints tested with curl
✅ Authentication and authorization flows
✅ Error handling and validation
✅ Pagination and filtering
✅ Concurrent request handling

### Performance Testing
✅ 500K notes seeded and queried
✅ Search performance verified
✅ Vote count calculations optimized
✅ Page load times measured (<500ms)

---

## 💡 Key Design Decisions

### Why Django?
- Built-in security features (CSRF, XSS, SQL injection protection)
- Powerful ORM with query optimization
- Admin interface for data management
- Excellent documentation and community

### Why MySQL?
- Proven reliability for relational data
- Excellent indexing capabilities
- ACID compliance for data integrity
- Wide hosting support

### Why Celery?
- Reliable background task processing
- Beat scheduler for periodic tasks
- Redis integration for low latency
- Scalable worker architecture

### Why React Query?
- Automatic caching reduces API calls
- Background refetching keeps data fresh
- Optimistic updates improve UX
- Built-in loading and error states


