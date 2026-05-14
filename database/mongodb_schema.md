

#### 1. **users** Collection

```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String,
  password: String (hashed)
}
```

**Indexes:**
- `username` (unique)

---

#### 2. **categories** Collection

```javascript
{
  _id: ObjectId,
  user_id: String (reference to users._id),
  name: String
}
```

**Indexes:**
- `user_id` + `name` (unique compound index)

---

#### 3. **expenses** Collection
Stores individual expense entries.

```javascript
{
  _id: ObjectId,
  user_id: String (reference to users._id),
  category_id: String (reference to categories._id),
  amount: Number (Decimal),
  description: String,
  date: String (ISO 8601 format)
}
```

**Indexes:**
- `user_id`

---

#### 4. **expense_backup** Collection
Stores backup versions of expenses for restore functionality.

```javascript
{
  _id: ObjectId,
  expense_id: String (reference to expenses._id),
  user_id: String (reference to users._id),
  category_id: String (reference to categories._id),
  amount: Number (Decimal),
  description: String,
  date: String (ISO 8601 format),
  modified_at: ISODate (timestamp)
}
```

**Indexes:**
- `expense_id`

---

## Key Differences from MySQL to MongoDB

| Aspect | MySQL | MongoDB |
|--------|-------|---------|
| **IDs** | INT AUTO_INCREMENT | ObjectId |
| **Foreign Keys** | Explicit FOREIGN KEY constraints | References via strings (manual enforcement in app) |
| **Data Model** | Normalized tables | Document-based collections |
| **Joins** | SQL JOIN | `$lookup` aggregation pipeline |
| **Transactions** | ACID guaranteed | ACID on document level, multi-doc transactions available |
| **Scaling** | Vertical | Horizontal (sharding support) |
   - minPoolSize: 10
   - maxIdleTimeMS: 300000
   - connectTimeoutMS: 10000

## Querying Examples

### Get all expenses for a user with category names
```javascript
db.expenses.aggregate([
  { $match: { user_id: "userId" } },
  {
    $lookup: {
      from: "categories",
      let: { category_id: "$category_id" },
      pipeline: [
        { $match: { $expr: { $eq: ["$_id", { $toObjectId: "$$category_id" }] } } }
      ],
      as: "category_details"
    }
  },
  {
    $project: {
      _id: 1,
      amount: 1,
      description: 1,
      date: 1,
      category_name: { $arrayElemAt: ["$category_details.name", 0] }
    }
  }
])
```

### Create backups of specific user's expenses
```javascript
db.expenses.find({ user_id: "userId" })
```

## Python Driver Setup

Install required package:
```bash
pip install pymongo
```

Connect to MongoDB:
```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["expense_tracker"]
```
