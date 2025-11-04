from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.models import TextInput, ProcessResponse, HealthResponse, EntityResponse
from app.bert_bm25_processor import get_bert_processor
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BERT Legal API",
    description="Entity extraction and summarization for US legal documents using BERT + BM25",
    version="1.0.0"
)

# CORS middleware for Lovable app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your Lovable app domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize BERT model on startup"""
    logger.info("Starting BERT Legal API...")
    # Initialize processor
    get_bert_processor()
    logger.info("BERT model loaded and ready")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "model_loaded": True
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    processor = get_bert_processor()
    return {
        "status": "ok",
        "version": "1.0.0",
        "model_loaded": processor is not None
    }

@app.post("/process", response_model=ProcessResponse)
async def process_document(input_data: TextInput):
    """
    Process legal document: extract entities, summarize, and extract facts
    
    Example request:
    ```
    POST http://178.16.141.15:8005/process
    {
        "text": "Your legal document text here...",
        "summary_length": 5,
        "num_facts": 10
    }
    ```
    """
    try:
        start_time = time.time()
        
        if not input_data.text or len(input_data.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        logger.info(f"Processing document ({len(input_data.text)} characters)")
        
        # Get processor
        processor = get_bert_processor()
        
        # Process document
        result = processor.process_legal_document(
            text=input_data.text,
            summary_length=input_data.summary_length,
            num_facts=input_data.num_facts
        )
        
        processing_time = time.time() - start_time
        
        logger.info(f"Processing completed in {processing_time:.2f}s")
        
        return {
            "status": "success",
            "entities": EntityResponse(**result["entities"]),
            "summary": result["summary"],
            "important_facts": result["important_facts"],
            "processing_time": round(processing_time, 2)
        }
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/extract-entities", response_model=EntityResponse)
async def extract_entities_only(input_data: TextInput):
    """
    Extract only entities from legal document (faster)
    
    Example request:
    ```
    POST http://178.16.141.15:8005/extract-entities
    {
        "text": "Your legal document text here..."
    }
    ```
    """
    try:
        from app.us_legal_ner import extract_us_legal_metadata
        
        if not input_data.text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        logger.info("Extracting entities only")
        
        entities = extract_us_legal_metadata(input_data.text)
        
        return EntityResponse(**entities)
    
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

@app.post("/summarize")
async def summarize_only(input_data: TextInput):
    """
    Summarize legal document only (no entity extraction)
    
    Example request:
    ```
    POST http://178.16.141.15:8005/summarize
    {
        "text": "Your legal document text here...",
        "summary_length": 5
    }
    ```
    """
    try:
        if not input_data.text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        logger.info("Summarizing document only")
        
        processor = get_bert_processor()
        summary = processor.summarize_with_bm25(
            text=input_data.text,
            summary_length=input_data.summary_length
        )
        
        return {
            "status": "success",
            "summary": summary
        }
    
    except Exception as e:
        logger.error(f"Error summarizing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
