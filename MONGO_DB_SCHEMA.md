# MongoDB Schema Structure - ReadVault

## Database Name
```
BOOKS
```

---

## Collections Structure

### Collection Naming Convention
- **Pattern**: `{author_name_with_underscores}`
- **Example**: `Sujatha_Ilanthirayan`, `Sriram_TV`, `Balakumaran`
- Collections are created dynamically per author (from `get_mongo_collection(author)`)

---

## Document Schema

Each book document in an author's collection follows this structure:

```javascript
{
  "_id": ObjectId("..."),                    // MongoDB unique identifier
  
  // Core Book Info
  "id": 1,                                   // PostgreSQL ID reference
  "title": "String",                         // Book title
  "author": "String",                        // Author name
  
  // Source & Type Info
  "source": "String",                        // Source type
  "type": "String",                          // Calculated content type
  "status": "String",                        // Reading status
  "featuring": "String or null"              // Featured characters (optional)
}
```

---

## Field Details

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `_id` | ObjectId | MongoDB unique ID | Auto-generated |
| `id` | Number | PostgreSQL ID reference | Integer |
| `title` | String | Book title | Any text |
| `author` | String | Author name | Any text |
| `source` | String | Where you read it | `Kuku FM`, `Kindle Unlimited`, `Pushtaka Digital Media`, `YouTube`, `Book` |
| `type` | String | Content type (derived) | `AudioBook`, `E-Book`, `VideoBook`, `Book` |
| `status` | String | Reading progress | `Finished`, `Reading` |
| `featuring` | String/Null | Character names | Any text or null |

---

## Type Mapping Rules

Automatically calculated based on **source**:

```javascript
source → type mapping:
┌─────────────────────────────┬──────────────┐
│ Source                      │ Type         │
├─────────────────────────────┼──────────────┤
│ Kindle Unlimited            │ E-Book       │
│ Pushtaka Digital Media      │ E-Book       │
│ Kuku FM                     │ AudioBook    │
│ YouTube                     │ VideoBook    │
│ Book                        │ Book         │
└─────────────────────────────┴──────────────┘
```

---

## Example Document

```json
{
  "_id": ObjectId("6789abcd1234567890def123"),
  "id": 1,
  "title": "Ponniyin Selvan",
  "author": "Kalki Krishnamurthy",
  "source": "Kindle Unlimited",
  "type": "E-Book",
  "status": "Finished",
  "featuring": "Arulmozhivarman, Vanathi"
}
```

```json
{
  "_id": ObjectId("6789abcd1234567890def456"),
  "id": 5,
  "title": "Vetrimalai",
  "author": "Sujatha",
  "source": "Kuku FM",
  "type": "AudioBook",
  "status": "Reading",
  "featuring": null
}
```

---

## Data Sync Flow

```
PostgreSQL (book table)
         ↓
    Flask API
         ↓
MongoDB (author_collection)

When you add/edit/delete in the app:
1. PostgreSQL is updated
2. API calculates Type from Source
3. MongoDB is mirrored using "id" as sync reference
```

---

## Indexes (Recommended)

```javascript
// Create these indexes for better query performance
db.{author_collection}.createIndex({ "id": 1 })         // For sync lookups
db.{author_collection}.createIndex({ "source": 1 })     // For filtering
db.{author_collection}.createIndex({ "status": 1 })     // For status queries
db.{author_collection}.createIndex({ "type": 1 })       // For type queries
```

---

## Sample Collection Structure

**Collection Name**: `Sujatha`

```javascript
[
  {
    "_id": ObjectId(...),
    "id": 1,
    "title": "Vetrimalai",
    "author": "Sujatha",
    "source": "Kuku FM",
    "type": "AudioBook",
    "status": "Finished",
    "featuring": "Vivek"
  },
  {
    "_id": ObjectId(...),
    "id": 2,
    "title": "Vetrimalai Part 2",
    "author": "Sujatha",
    "source": "Kindle Unlimited",
    "type": "E-Book",
    "status": "Reading",
    "featuring": null
  }
]
```

---

## How to Query

### Using the MCP Server

**Find all books by an author:**
```javascript
// Query: {"author": "Sujatha"}
// In the MCP find_documents tool, use:
database: "BOOKS"
collection: "Sujatha"
query: '{"author": "Sujatha"}'
```

**Find by source type:**
```javascript
database: "BOOKS"
collection: "Sujatha"
query: '{"source": "AudioBook"}'
```

**Find by reading status:**
```javascript
database: "BOOKS"
collection: "Sujatha"
query: '{"status": "Reading"}'
```

---

## Migration Notes

### Step 1: Add Type field (if not done)
```bash
node migrate_add_type.js
```
This updates all existing documents with the `type` field based on their `source`.

### Step 2: Remove redundant pg_id field
```bash
node migrate_remove_pg_id.js
```
This removes the redundant `pg_id` field from all documents, keeping only `id` for PostgreSQL sync reference.
