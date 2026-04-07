// MongoDB migration script to remove pg_id field and keep only id
// This removes redundant pg_id field from all documents

import { MongoClient } from "mongodb";

const MONGO_URI = process.env.MONGO_URI || "mongodb://localhost:27017";

async function migrateRemovePgId() {
  const client = new MongoClient(MONGO_URI);

  try {
    await client.connect();
    console.log("✓ Connected to MongoDB");

    const db = client.db("BOOKS");
    const collections = await db.listCollections().toArray();

    console.log(`\nFound ${collections.length} collection(s)\n`);

    let totalUpdated = 0;

    for (const col of collections) {
      const collection = db.collection(col.name);

      // Find all documents that have pg_id field
      const docs = await collection.find({ pg_id: { $exists: true } }).toArray();

      if (docs.length > 0) {
        console.log(`📝 Updating collection: "${col.name}"`);
        console.log(`   Found ${docs.length} document(s) with pg_id field`);

        // Remove pg_id field from all documents
        const result = await collection.updateMany(
          { pg_id: { $exists: true } },
          { $unset: { pg_id: "" } }
        );

        console.log(`   ✓ Removed pg_id from ${result.modifiedCount} document(s)\n`);
        totalUpdated += result.modifiedCount;
      } else {
        console.log(`⊘ Collection "${col.name}": No documents with pg_id field\n`);
      }
    }

    console.log(`\n${'='.repeat(50)}`);
    console.log(`✅ Migration Complete!`);
    console.log(`📊 Total documents updated: ${totalUpdated}`);
    console.log(`📌 Schema now uses only "id" field for PostgreSQL reference`);
    console.log(`${'='.repeat(50)}\n`);

  } catch (err) {
    console.error("❌ Migration error:", err.message);
  } finally {
    await client.close();
  }
}

migrateRemovePgId();
