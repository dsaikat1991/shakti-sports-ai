# 04 — Database Design

Version: 1.0

Status: Planning

Project: Shakti Sports AI

Database: Firebase Cloud Firestore

---

# 1. Purpose

This document defines the database architecture for Shakti Sports AI.

The database is designed to:

- Scale to millions of users
- Support AI-generated performance reports
- Enable athlete discovery
- Support multiple user roles
- Integrate seamlessly with Firebase Authentication
- Remain flexible for future expansion

---

# 2. Database Philosophy

The database follows these principles:

- Firebase Authentication is the single identity provider.
- Every authenticated user has exactly one account.
- Role-specific information is separated into dedicated profile collections.
- Media files are stored in Firebase Storage.
- Metadata is stored in Firestore.
- Documents should remain lightweight and focused.

---

# 3. High-Level Database Structure

```
Firebase Auth
        │
        ▼
users/{uid}
        │
        ├──────────────┐
        │              │
        ▼              ▼
athleteProfiles    coachProfiles
        │              │
        └──────┐       │
               ▼       ▼
         scoutProfiles academyProfiles
```

---

# 4. Primary Collections

```
users

athleteProfiles

coachProfiles

scoutProfiles

academyProfiles

videos

reports

notifications

savedAthletes

contactRequests

adminLogs

systemSettings
```

---

# 5. Users Collection

Collection

```
users
```

Document ID

```
Firebase UID
```

Purpose

Stores common information for every authenticated account.

Example

```json
{
  "uid": "abc123",
  "role": "athlete",
  "displayName": "Rahul Sharma",
  "email": "rahul@email.com",
  "photoURL": "...",
  "phoneNumber": "+91XXXXXXXXXX",
  "status": "active",
  "emailVerified": true,
  "createdAt": "...",
  "updatedAt": "...",
  "lastLogin": "..."
}
```

---

# 6. Athlete Profiles

Collection

```
athleteProfiles
```

Document ID

```
Firebase UID
```

Purpose

Stores athlete-specific information.

Fields

- fullName
- dateOfBirth
- gender
- height
- weight
- state
- district
- city
- preferredEvent
- secondaryEvent
- bio
- profileImage
- visibility
- verificationStatus
- latestVideoId
- latestReportId
- overallAIScore
- createdAt
- updatedAt

---

# 7. Coach Profiles

Collection

```
coachProfiles
```

Document ID

```
Firebase UID
```

Fields

- fullName
- organization
- designation
- specialization
- experience
- state
- district
- verified
- bio
- createdAt

---

# 8. Scout Profiles

Collection

```
scoutProfiles
```

Document ID

```
Firebase UID
```

Fields

- fullName
- organization
- designation
- assignedRegion
- verified
- bio
- createdAt

---

# 9. Academy Profiles

Collection

```
academyProfiles
```

Document ID

```
Academy ID
```

Fields

- academyName
- address
- city
- state
- website
- contactEmail
- contactNumber
- sports
- verified
- createdAt

---

# 10. Videos Collection

Collection

```
videos
```

Document ID

```
Auto ID
```

Purpose

Stores uploaded performance video metadata.

Fields

- athleteId
- reportId
- storagePath
- thumbnailPath
- duration
- fileSize
- resolution
- fps
- uploadStatus
- processingStatus
- uploadedAt
- processedAt

---

# 11. Reports Collection

Collection

```
reports
```

Document ID

```
Auto ID
```

Purpose

Stores AI-generated performance reports.

Fields

- athleteId
- videoId
- overallScore
- speed
- acceleration
- balance
- posture
- strideLength
- strideConsistency
- reactionTime
- confidenceScore
- strengths
- improvements
- recommendations
- aiModelVersion
- generatedAt

---

# 12. Notifications

Collection

```
notifications
```

Fields

- userId
- title
- message
- type
- read
- createdAt

---

# 13. Saved Athletes

Collection

```
savedAthletes
```

Purpose

Bookmarks for coaches and scouts.

Fields

- userId
- athleteId
- createdAt

---

# 14. Contact Requests

Collection

```
contactRequests
```

Purpose

Stores communication requests.

Fields

- senderId
- receiverId
- message
- status
- createdAt

Status

- pending
- accepted
- rejected

---

# 15. Admin Logs

Collection

```
adminLogs
```

Purpose

Audit trail.

Fields

- adminId
- action
- collection
- documentId
- timestamp

---

# 16. System Settings

Collection

```
systemSettings
```

Stores platform-wide configuration.

Examples

- AI model version
- Upload limits
- Feature flags
- Maintenance mode

---

# 17. Firebase Storage Structure

```
storage/

profile-images/
    {uid}.jpg

videos/
    {uid}/
        {videoId}.mp4

thumbnails/
    {uid}/
        {videoId}.jpg

reports/
    {uid}/
        {reportId}.pdf

system/
```

---

# 18. Collection Relationships

```
users
   │
   ├── athleteProfiles
   │       │
   │       ├── videos
   │       │       │
   │       │       └── reports
   │
   ├── coachProfiles
   │
   ├── scoutProfiles
   │
   └── academyProfiles
```

---

# 19. Firestore Security Philosophy

Every request requires authentication unless explicitly public.

Rules

Athletes

- Read own profile
- Edit own profile

Coach

- Read public athlete profiles
- Cannot edit athlete profiles

Scout

- Read public athlete profiles
- Save athletes

Academy

- Read public athlete profiles

Admin

- Full access

---

# 20. Composite Indexes

Recommended indexes

```
preferredEvent + state

preferredEvent + district

overallAIScore

verificationStatus

overallAIScore + preferredEvent

createdAt

uploadStatus
```

---

# 21. Data Retention

Reports

Permanent

Videos

Configurable archive policy

Deleted Accounts

Soft delete

then

Permanent deletion

---

# 22. Future Collections

```
leaderboards

trainingPlans

competitions

subscriptions

payments

organizations

federations

analytics

auditTrail
```

---

# 23. Backup Strategy

- Firestore exports
- Storage backups
- Disaster recovery
- Versioned AI reports

---

# 24. Scalability

The database must support:

- Multiple sports
- Multiple AI engines
- Mobile applications
- International regions
- Federation dashboards
- Enterprise customers

without requiring major schema redesign.

---

# 25. Database Design Principles

Every authenticated person exists exactly once in:

```
users/{uid}
```

Role-specific information is stored separately.

This architecture:

- avoids duplicate identities
- simplifies authentication
- supports multiple roles in the future
- improves maintainability
- aligns with Firebase best practices

---

# 26. Future Multi-Role Support

A single user may eventually hold multiple roles.

Example

```json
{
  "roles": [
    "athlete",
    "coach"
  ]
}
```

The unified user model allows this without changing the authentication system.

---

# 27. Final Principle

The database exists to support one mission:

> Enable every athlete to be discovered through trusted, AI-assisted performance data while remaining secure, scalable, and easy to evolve.