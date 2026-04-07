// MongoDB migration script to add Type field to existing documents
// Run this once to update all existing records with the Type field

import { MongoClient } from "mongodb";

const MONGO_URI = process.env.MONGO_URI || "mongodb://localhost:27017";

function getTypeFromSource(source) {
  if (source === "Kindle Unlimited" || source === "Pushtaka Digital Media") {
    return "E-Book";
  } else if (source === "Kuku FM") {
    return "AudioBook";
  } else if (source === "YouTube") {
    return "VideoBook";
  } else if (source === "Book") {
    return "Book";
  }
  return "Unknown";
}

async function migrate() {
  const client = new MongoClient(MONGO_URI);

  try {
    await client.connect();
    console.log("Connected to MongoDB");

    const db = client.db("BOOKS");
    const collections = await db.listCollections().toArray();

    for (const col of collections) {
      const collection = db.collection(col.name);

      // Find all documents without a type field
      const docs = await collection.find({ type: { $exists: false } }).toArray();

      if (docs.length > 0) {
        console.log(`Updating ${docs.length} documents in collection: ${col.name}`);

        for (const doc of docs) {
          const source = doc.source || "";
          const type = getTypeFromSource(source);

          await collection.updateOne(
            { _id: doc._id },
            { $set: { type } }
          );
        }

        console.log(`✓ Completed migration for collection: ${col.name}`);
      }
    }

    console.log("✓ Migration complete!");
  } catch (err) {
    console.error("Migration error:", err);
  } finally {
    await client.close();
  }
}

migrate();
