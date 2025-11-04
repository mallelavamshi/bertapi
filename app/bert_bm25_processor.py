from transformers import AutoTokenizer, AutoModel
from rank_bm25 import BM25Okapi
import torch
from nltk.tokenize import sent_tokenize, word_tokenize
from typing import List, Dict
import nltk
from app.us_legal_ner import extract_us_legal_metadata

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class BERTBm25Processor:
    """BERT + BM25 for entity extraction and summarization"""
    
    def __init__(self):
        print("Loading Legal-BERT model...")
        self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
        self.model = AutoModel.from_pretrained("nlpaueb/legal-bert-base-uncased")
        print("Legal-BERT model loaded successfully")
    
    def get_sentence_embedding(self, sentence: str) -> torch.Tensor:
        """Get BERT embedding for sentence"""
        inputs = self.tokenizer(
            sentence,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[0][0]
        
        return embedding
    
    def summarize_with_bm25(self, text: str, summary_length: int = 5) -> str:
        """Summarize using BERT clustering + BM25 ranking"""
        sentences = sent_tokenize(text)
        
        if len(sentences) <= summary_length:
            return text
        
        # Tokenize for BM25
        tokenized_sentences = [word_tokenize(sent.lower()) for sent in sentences]
        
        # Create BM25 index
        bm25 = BM25Okapi(tokenized_sentences)
        
        # Query with legal terms
        query = word_tokenize("court case plaintiff defendant holding ruling statute law")
        
        # Get BM25 scores
        bm25_scores = bm25.get_scores(query)
        
        # Get BERT scores
        bert_scores = []
        for sent in sentences:
            emb = self.get_sentence_embedding(sent)
            score = torch.mean(torch.abs(emb)).item()
            bert_scores.append(score)
        
        # Combine scores
        combined_scores = []
        for bm25_score, bert_score in zip(bm25_scores, bert_scores):
            combined = 0.6 * bm25_score + 0.4 * bert_score
            combined_scores.append(combined)
        
        # Select top sentences
        ranked_indices = sorted(
            range(len(combined_scores)),
            key=lambda i: combined_scores[i],
            reverse=True
        )[:summary_length]
        
        ranked_indices.sort()
        summary_sentences = [sentences[i] for i in ranked_indices]
        
        return " ".join(summary_sentences)
    
    def extract_facts_with_bert(self, text: str, num_facts: int = 10) -> List[str]:
        """Extract important facts using BERT"""
        sentences = sent_tokenize(text)
        
        factual_sentences = []
        for sent in sentences:
            if self._is_factual(sent):
                emb = self.get_sentence_embedding(sent)
                score = torch.mean(torch.abs(emb)).item()
                factual_sentences.append((sent, score))
        
        factual_sentences.sort(key=lambda x: x[1], reverse=True)
        return [fact[0] for fact in factual_sentences[:num_facts]]
    
    def _is_factual(self, sentence: str) -> bool:
        """Check if sentence is factual"""
        factual_keywords = [
            "on", "dated", "filed", "testified", "evidence",
            "plaintiff", "defendant", "alleged", "contract",
            "signed", "executed", "court", "ruled"
        ]
        return any(kw in sentence.lower() for kw in factual_keywords)
    
    def process_legal_document(self, text: str, summary_length: int = 5, num_facts: int = 10) -> Dict:
        """Complete processing: entities, summary, facts"""
        entities = extract_us_legal_metadata(text)
        summary = self.summarize_with_bm25(text, summary_length)
        facts = self.extract_facts_with_bert(text, num_facts)
        
        return {
            "entities": entities,
            "summary": summary,
            "important_facts": facts
        }

# Global instance
bert_processor = None

def get_bert_processor():
    global bert_processor
    if bert_processor is None:
        bert_processor = BERTBm25Processor()
    return bert_processor
