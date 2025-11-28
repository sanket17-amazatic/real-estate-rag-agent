# 🎯 Setup and Deployment Checklist

## ✅ Pre-Setup Checklist

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] pip package manager available
- [ ] OpenAI API account and API key
- [ ] Milvus Zilliz Cloud account and credentials
- [ ] Text editor or IDE (VS Code recommended)
- [ ] Terminal/PowerShell access

## 📦 Installation Checklist

### Step 1: Install Dependencies
- [ ] Navigate to project directory
- [ ] Run: `pip install -r requirements.txt`
- [ ] Run: `pip install -r requirements-pdf.txt` (optional, for PDF conversion)
- [ ] Verify no installation errors
- [ ] Check Python packages: `pip list | findstr openai`
- [ ] Check Python packages: `pip list | findstr pymilvus`

### Step 2: Configure Environment
- [ ] Copy `.env.example` to `.env`
- [ ] Add OpenAI API key to `.env`
- [ ] Add Milvus host endpoint to `.env`
- [ ] Add Milvus username to `.env`
- [ ] Add Milvus password to `.env`
- [ ] Verify `.env` file is not tracked by git

## 🔧 Configuration Verification

### Environment Variables
- [ ] `OPENAI_API_KEY` is set and valid
- [ ] `MILVUS_HOST` is correct endpoint
- [ ] `MILVUS_PORT` is 19530
- [ ] `MILVUS_USER` is set
- [ ] `MILVUS_PASSWORD` is set

### Milvus Zilliz Cloud
- [ ] Cluster is running
- [ ] IP whitelist configured (if applicable)
- [ ] Connection credentials are correct
- [ ] Test connection from local machine

### OpenAI API
- [ ] API key is active
- [ ] Billing is set up
- [ ] Usage limits are appropriate
- [ ] GPT-4 access confirmed

## 🚀 First Run Checklist

### Start the Server
- [ ] Run: `python main.py`
- [ ] Server starts without errors
- [ ] See "Connected to Milvus" in logs
- [ ] See "Application startup complete" message
- [ ] Server running on http://localhost:8000

### Health Check
- [ ] Open browser: http://localhost:8000
- [ ] Visit: http://localhost:8000/health
- [ ] Response shows "healthy" status
- [ ] Milvus connection confirmed
- [ ] Collection name displayed

### API Documentation
- [ ] Visit: http://localhost:8000/docs
- [ ] Swagger UI loads correctly
- [ ] All endpoints visible
- [ ] Can expand and view endpoint details

## 📄 PDF Preparation Checklist

### Convert Mock Data (Optional)
- [ ] Locate: `NewLaunches_MockData (1).txt`
- [ ] Run: `python convert_to_pdf.py "NewLaunches_MockData (1).txt"`
- [ ] PDF created in `data/pdfs/` folder
- [ ] PDF opens and displays correctly
- [ ] Text is readable and properly formatted

### Prepare Your PDFs
- [ ] PDFs are text-based (not scanned images)
- [ ] PDFs are not password-protected
- [ ] PDFs contain property information
- [ ] File sizes are reasonable (<50MB each)
- [ ] Files are named descriptively

## 📤 PDF Ingestion Checklist

### Upload First PDF
- [ ] Visit: http://localhost:8000/docs
- [ ] Find `/ingest/pdf` endpoint
- [ ] Click "Try it out"
- [ ] Upload PDF file
- [ ] (Optional) Add locality parameter
- [ ] (Optional) Add property_type parameter
- [ ] Click "Execute"
- [ ] Response shows success
- [ ] Check `chunks_created` > 0
- [ ] Check `vectors_inserted` > 0

### Verify Ingestion
- [ ] Visit: http://localhost:8000/stats
- [ ] `num_entities` > 0
- [ ] Collection name is correct
- [ ] PDF moved to `data/processed/` folder

### Upload Additional PDFs
- [ ] Upload 2-3 more PDFs
- [ ] Each ingestion succeeds
- [ ] Check stats after each upload
- [ ] Verify entity count increases

## 🧪 Testing Checklist

### Run Test Suite
- [ ] Run: `python test_api.py`
- [ ] Health check passes
- [ ] RAG queries return results
- [ ] Buy agent responds
- [ ] Rent agent responds
- [ ] Details agent responds
- [ ] Auto-routing works
- [ ] Property search works

### Manual API Testing

#### Test RAG Query
- [ ] POST to `/query/rag`
- [ ] Query: "What amenities are in Wakad?"
- [ ] Receives answer
- [ ] Answer is relevant
- [ ] Sources are included (if requested)

#### Test Buy Agent
- [ ] POST to `/query/agent`
- [ ] agent_type: "buy"
- [ ] Message: "Show me 2 BHK in Wakad"
- [ ] Receives response
- [ ] Response includes property suggestions

#### Test Rent Agent
- [ ] POST to `/query/agent`
- [ ] agent_type: "rent"
- [ ] Message: "Looking for rentals in Hinjewadi"
- [ ] Receives response
- [ ] Response addresses rental query

#### Test Details Agent
- [ ] POST to `/query/agent`
- [ ] agent_type: "details"
- [ ] Message: "Tell me about Evergreen Heights"
- [ ] Receives detailed information
- [ ] Information from ingested PDFs

#### Test Auto-Routing
- [ ] POST to `/query/auto`
- [ ] Query: "What is connectivity in Wakad?"
- [ ] Receives response
- [ ] Check `routing_info` in response
- [ ] Verify correct intent detected

## 🔍 Functionality Verification

### RAG System
- [ ] Embeddings are generated correctly
- [ ] Milvus search returns results
- [ ] Top-k results are relevant
- [ ] LLM generates coherent answers
- [ ] Sources are cited

### Agent System
- [ ] Agents use correct system prompts
- [ ] Tools are called when appropriate
- [ ] Tool results are integrated
- [ ] Conversation history maintained
- [ ] Responses are natural and helpful

### Orchestrator
- [ ] Intent detection works
- [ ] Knowledge queries → RAG
- [ ] Buy queries → BuyAgent
- [ ] Rent queries → RentAgent
- [ ] Details queries → DetailsAgent

### LLM Processor
- [ ] Singleton pattern working
- [ ] Multiple calls reuse instance
- [ ] Completions generated successfully
- [ ] Embeddings generated successfully
- [ ] Token usage is reasonable

## 📊 Performance Checklist

### Response Times
- [ ] Health check < 1s
- [ ] RAG query < 5s
- [ ] Agent query < 10s
- [ ] PDF ingestion completes within reasonable time
- [ ] No timeout errors

### Resource Usage
- [ ] Memory usage is stable
- [ ] No memory leaks
- [ ] CPU usage is reasonable
- [ ] Network latency is acceptable

## 🔒 Security Checklist (Production)

### API Security
- [ ] Add authentication (JWT/API keys)
- [ ] Implement rate limiting
- [ ] Validate all inputs
- [ ] Sanitize file uploads
- [ ] Enable CORS appropriately

### Data Security
- [ ] Environment variables not in git
- [ ] API keys are secret
- [ ] Database credentials secure
- [ ] No sensitive data in logs
- [ ] File upload restrictions

## 🌐 Deployment Checklist (Optional)

### Docker (Optional)
- [ ] Create Dockerfile
- [ ] Build Docker image
- [ ] Test container locally
- [ ] Push to container registry

### Cloud Deployment (Optional)
- [ ] Choose platform (AWS/Azure/GCP)
- [ ] Configure environment variables
- [ ] Set up load balancer
- [ ] Configure auto-scaling
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Set up alerts

## 📝 Documentation Checklist

### Code Documentation
- [ ] README.md is complete
- [ ] QUICKSTART.md is clear
- [ ] ARCHITECTURE.md is accurate
- [ ] Code comments are helpful
- [ ] API docs are comprehensive

### User Documentation
- [ ] Usage examples provided
- [ ] Common issues documented
- [ ] FAQ created (if needed)
- [ ] Contact information added

## 🐛 Troubleshooting Checklist

### If Server Won't Start
- [ ] Check Python version
- [ ] Verify dependencies installed
- [ ] Check `.env` file exists
- [ ] Verify port 8000 is available
- [ ] Check error logs

### If Milvus Connection Fails
- [ ] Verify credentials in `.env`
- [ ] Check Zilliz Cloud cluster is running
- [ ] Verify IP whitelist
- [ ] Test network connectivity
- [ ] Check firewall settings

### If OpenAI API Fails
- [ ] Verify API key is correct
- [ ] Check API quota/billing
- [ ] Verify model access
- [ ] Check rate limits
- [ ] Review error messages

### If PDF Ingestion Fails
- [ ] Verify PDF is text-based
- [ ] Check PDF is not encrypted
- [ ] Verify file size
- [ ] Check disk space
- [ ] Review ingestion logs

### If RAG Returns No Results
- [ ] Verify PDFs ingested
- [ ] Check collection has entities
- [ ] Verify embeddings generated
- [ ] Check query similarity threshold
- [ ] Review Milvus logs

## ✨ Feature Extension Checklist (Future)

### Additional Features
- [ ] Add user authentication
- [ ] Implement conversation memory
- [ ] Add property comparison feature
- [ ] Create property recommendation engine
- [ ] Add email notifications
- [ ] Implement booking system
- [ ] Add analytics dashboard

### Integration
- [ ] Connect to real property database
- [ ] Integrate payment gateway
- [ ] Add CRM integration
- [ ] Implement notification service
- [ ] Add social media sharing

## 📈 Monitoring Checklist (Production)

### Logging
- [ ] Structured logging implemented
- [ ] Log rotation configured
- [ ] Error tracking (Sentry/etc.)
- [ ] Performance metrics logged

### Monitoring
- [ ] Uptime monitoring
- [ ] API response time tracking
- [ ] Error rate monitoring
- [ ] Resource usage tracking
- [ ] Cost monitoring (API calls)

### Alerts
- [ ] Downtime alerts
- [ ] High error rate alerts
- [ ] Performance degradation alerts
- [ ] Cost threshold alerts

---

## 🎯 Quick Verification Commands

```powershell
# Check server is running
curl http://localhost:8000/health

# Check collection stats
curl http://localhost:8000/stats

# Test RAG query
curl -X POST http://localhost:8000/query/rag -H "Content-Type: application/json" -d "{\"query\": \"test\", \"top_k\": 3}"

# Test auto-routing
curl -X POST "http://localhost:8000/query/auto?query=test"
```

---

## ✅ Final Verification

- [ ] All core features working
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Environment configured
- [ ] PDFs ingested
- [ ] Agents responding correctly
- [ ] RAG system functioning
- [ ] Ready for demo/production

**Status**: Ready to Deploy ✨

---

**Note**: Keep this checklist handy during setup and deployment. Check off items as you complete them!
