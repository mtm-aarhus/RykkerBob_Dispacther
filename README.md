
# 📄 README

## Rykker Dispatcher Robot

**Rykker Dispatcher** is an automation for **Teknik og Miljø, Aarhus Kommune**. It scans KMD Nova for overdue cases, determines the appropriate rykker level, and queues tasks for further processing in OpenOrchestrator.

---

## 🚀 Features

✅ **KMD Nova Integration**  
- Connects to KMD Nova REST API  
- Retrieves all active tasks with status "S"  

🧾 **Case Classification**  
- Determines which rykker (1, 2, or 3) should be sent  
- Identifies cases that do not require action  

📤 **Queue Creation**  
- Generates queue items containing:
  - Case metadata
  - Task and case UUIDs
  - Rykker number
  - Assigned caseworker information  

🔐 **Credential Management**  
- Automatically refreshes access tokens as needed  

---

## 🧭 Process Flow

1. **Token Management**
   - Retrieves or refreshes KMD OAuth tokens (`GetKmdAcessToken.py`)
2. **Task Query**
   - Calls KMD Nova `/Task/GetList` endpoint
   - Fetches tasks with deadline equal to today
3. **Classification**
   - Determines rykker level by inspecting task descriptions
4. **Queue Preparation**
   - Packages relevant data into queue elements
5. **Queue Submission**
   - Creates all queue items in bulk in OpenOrchestrator

---

## 🔐 Privacy & Security

- All API requests use HTTPS
- Credentials and tokens are stored securely in OpenOrchestrator
- No case data is persisted locally

---

## ⚙️ Dependencies

- Python 3.10+
- `requests`
- `pandas`

---

## 👷 Maintainer

Gustav Chatterton  
*Digital udvikling, Teknik og Miljø, Aarhus Kommune*
