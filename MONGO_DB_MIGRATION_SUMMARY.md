# MongoDB Data Migration Summary

## Changes Made

### ✅ Removed Redundant Field
- **Removed**: `pg_id` field from all MongoDB documents
- **Kept**: `id` field (PostgreSQL reference)
- **Reason**: Both fields stored the same value - unnecessary duplication

---

## New Schema (Cleaner)

### Before ❌
```json
{
  "_id": ObjectId("..."),
  "id": 1,
  "title": "Book Title",
  "author": "Author Name",
  "source": "Kuku FM",
  "type": "AudioBook",
  "status": "Finished",
  "featuring": "Character Name",
  "pg_id": 1              // ← REDUNDANT (removed)
}
```

### After ✅
```json
{
  "_id": ObjectId("..."),
  "id": 1,
  "title": "Book Title",
  "author": "Author Name",
  "source": "Kuku FM",
  "type": "AudioBook",
  "status": "Finished",
  "featuring": "Character Name"
}
```

---

## Files Updated

### 1. **API Changes** (`api.py`)

#### POST /api/books
```python
# Before
col.update_one({"pg_id": row['id']}, {"$set": {**row, "pg_id": row['id']}}, upsert=True)

# After
col.update_one({"id": row['id']}, {"$set": row}, upsert=True)
```

#### PUT /api/books/<id>
```python
# Before
col.update_one({"pg_id": book_id}, {"$set": {**row, "pg_id": book_id}}, upsert=True)

# After
col.update_one({"id": book_id}, {"$set": row}, upsert=True)
```

#### DELETE /api/books/<id>
```python
# Before
col.delete_one({"pg_id": book_id})

# After
col.delete_one({"id": book_id})
```

### 2. **Migration Scripts**

#### migrate_add_type.js
- Already adds `type` field based on source
- No changes needed (still compatible)

#### migrate_remove_pg_id.js (NEW)
- Removes `pg_id` field from all existing documents
- Runs across all author collections in BOOKS database
- Safe operation (no data loss, just field removal)

### 3. **Schema Documentation** (`SCHEMA.md`)
- Updated all examples to remove `pg_id`
- Updated field table to remove `pg_id` row
- Updated sync flow description
- Updated indexes recommendation
- Added migration notes for both scripts

---

## How to Run Migration

### Step 1: Add Type Field (if needed)
```bash
cd C:\Scripts\CLAUDE\MCP\MONGO_DB
node migrate_add_type.js
```

### Step 2: Remove pg_id Field
```bash
node migrate_remove_pg_id.js
```

Expected output:
```
✓ Connected to MongoDB

Found 3 collection(s)

📝 Updating collection: "Sujatha"
   Found 5 document(s) with pg_id field
   ✓ Removed pg_id from 5 document(s)

📝 Updating collection: "Kalki_Krishnamurthy"
   Found 3 document(s) with pg_id field
   ✓ Removed pg_id from 3 document(s)

...

==================================================
✅ Migration Complete!
📊 Total documents updated: 47
📌 Schema now uses only "id" field for PostgreSQL reference
==================================================
```

---

## Benefits of This Change

| Aspect | Before | After |
|--------|--------|-------|
| **Redundancy** | ❌ `id` + `pg_id` | ✅ Only `id` |
| **Data Size** | Larger | Smaller |
| **Clarity** | Confusing | Clear intent |
| **Maintenance** | Need to sync 2 fields | Only 1 field to manage |
| **API Logic** | Complex `{**row, "pg_id": row['id']}` | Simple `row` object |

---

## Verification

After running the migrations, verify with:

```javascript
// Connect to MongoDB and run:
use BOOKS

// Check a collection
db.Sujatha.findOne()

// Should NOT have pg_id field
// Should look like:
{
  "_id": ObjectId(...),
  "id": 1,
  "title": "...",
  "author": "...",
  "source": "...",
  "type": "...",
  "status": "...",
  "featuring": "..."
}
```

---

## Rollback (if needed)

To restore from backup or previous state:
```bash
# All changes are additive/removals, no data corruption
# Keep a MongoDB backup before running migrations
```

---

## Summary

✅ Removed redundant `pg_id` field  
✅ Updated API to use only `id` for sync  
✅ Created migration script  
✅ Updated documentation  
✅ **Result**: Cleaner, more efficient MongoDB schema
