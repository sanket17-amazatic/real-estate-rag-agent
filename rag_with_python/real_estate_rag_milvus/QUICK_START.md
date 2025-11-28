# 🎯 Quick Start Guide - Real Estate RAG UI

## ⚡ Starting Everything

### Terminal 1 - Backend API Server
```bash
cd /home/ah0106/Project/AI_Chatbot_Assignement_G-5/ai-chatbot-02/real_estate_rag_milvus
source venv/bin/activate
python main.py
```
✅ Backend runs on: `http://localhost:8000`

### Terminal 2 - UI Server
```bash
cd /home/ah0106/Project/AI_Chatbot_Assignement_G-5/ai-chatbot-02/real_estate_rag_milvus/ui
python3 -m http.server 3000
```
✅ UI runs on: `http://localhost:3000`

---

## 🎨 UI Files Modified

| File | Changes |
|------|---------|
| **index.html** | Added query form, API selector, response containers, loading indicator |
| **index.js** | Implemented /query and /search API handlers with error handling |
| **index.css** | Modern styling with responsive design, animations, color scheme |

---

## 🔌 API Implementation

### Query API (`/query/`)
**Purpose**: Get AI-summarized answers
```javascript
// JavaScript Call
const response = await fetch("http://localhost:8000/query/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "Show me 2BHK flats in Wakad",
    top_k: 5
  })
});
```

### Search API (`/search/`)
**Purpose**: Get raw vector search results
```javascript
// JavaScript Call
const response = await fetch("http://localhost:8000/search/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "Aurora Crest properties",
    top_k: 5
  })
});
```

---

## 🎯 Example Queries to Try

### Query API Mode:
```
"Show me 2BHK apartments in Wakad"
"Tell me about Aurora Crest"
"What properties are available under 50 lakhs?"
"Properties with gym and swimming pool"
```

### Search API Mode:
```
"Viman Nagar residential"
"IT park proximity"
"Budget apartments"
"Luxury villas Pune"
```

---

## 📊 Response Format

### ✅ Successful Response
```
Response Title: "AI Response for: 'Your Query'"

Display:
- AI-generated summary
- Property list or details
- Source information
- Confidence score
```

### ❌ Error Response
```
Red error banner with:
- Error message
- Status code (if API error)
- Suggestion to try again
```

---

## 🎨 UI Features

| Feature | Description |
|---------|-------------|
| 🔄 **API Switcher** | Toggle between Query (AI) and Search (Raw) modes |
| ⏳ **Loading Spinner** | Shows while processing queries |
| 📜 **Response Formatting** | Handles bullets, bold, links automatically |
| 🏆 **Confidence Scores** | Shows result quality percentage |
| 📱 **Mobile Responsive** | Works on desktop, tablet, mobile |
| 🔙 **Query History** | Last 10 queries saved in localStorage |
| ⚠️ **Error Handling** | User-friendly error messages |

---

## 🛠️ Troubleshooting

### Issue: "Cannot connect to API"
```
Solution: Make sure backend is running on http://localhost:8000
Check terminal 1 for the message: "Uvicorn running on http://0.0.0.0:8000"
```

### Issue: "Module not found" error
```
Solution: Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Port 3000 or 8000 already in use
```
Solution: Kill the process
lsof -ti:3000 | xargs kill -9  # Kill port 3000
lsof -ti:8000 | xargs kill -9  # Kill port 8000
```

### Issue: No results returned
```
Solution: 
1. Check if collection is loaded in backend
2. Make sure documents are uploaded
3. Try with different query keywords
```

---

## 📁 File Structure

```
ui/
├── index.html          # Main UI layout
├── index.js            # API integration + logic
├── index.css           # Styling + responsive design
└── (Served on port 3000)

Backend:
└── main.py             # FastAPI server (port 8000)
    ├── /query/         → AI-summarized responses
    └── /search/        → Raw vector search results
```

---

## 🔐 Security Notes

✅ CORS enabled for frontend-backend communication
✅ Input validation on form submission
✅ HTML escaping to prevent XSS attacks
✅ Timeout protection (30 seconds)
✅ Error logging for debugging

---

## 📈 Testing Checklist

- [ ] Start backend server (port 8000)
- [ ] Start UI server (port 3000)
- [ ] Open http://localhost:3000 in browser
- [ ] Try a query with "Query API" mode selected
- [ ] Switch to "Search API" and try again
- [ ] Check if query appears in history sidebar
- [ ] Click history item to reuse query
- [ ] Test error handling (try invalid input)
- [ ] Test on mobile device (responsive design)
- [ ] Check console logs for debugging

---

## 🎉 Success Indicators

✅ Query input accepts text
✅ Submit button sends request
✅ Loading spinner appears during processing
✅ Response displays correctly
✅ API mode switcher works
✅ History saves and loads
✅ Mobile layout is responsive
✅ No console errors

---

## 📞 Support

All implemented features are documented in:
`UI_API_IMPLEMENTATION.md`

For issues or enhancements, check:
1. Browser console (F12 → Console tab)
2. Backend server logs
3. Network tab to see API calls
