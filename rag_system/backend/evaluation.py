"""
Evaluation metrics for RAG system performance.
Includes ROUGE scores, BLEU scores, and token overlap metrics.
"""

import logging
from typing import List, Dict, Tuple
from collections import Counter
import re

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    logging.warning("rouge_score not available, ROUGE metrics will be estimated")

logger = logging.getLogger(__name__)


class RAGEvaluator:
    """Evaluate RAG system performance using multiple metrics."""
    
    def __init__(self):
        """Initialize evaluator."""
        if ROUGE_AVAILABLE:
            self.rouge_scorer = rouge_scorer.RougeScorer(
                ['rouge1', 'rougeL'],
                use_stemmer=True
            )
        else:
            self.rouge_scorer = None
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple tokenization by splitting on whitespace and punctuation."""
        text = text.lower()
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    @staticmethod
    def _calculate_bleu_ngram(reference: List[str], hypothesis: List[str], 
                             n: int) -> Tuple[float, int, int]:
        """Calculate BLEU score for n-grams."""
        if len(hypothesis) < n or len(reference) < n:
            return 0.0, 0, 0
        
        ref_ngrams = Counter(
            tuple(reference[i:i+n]) for i in range(len(reference) - n + 1)
        )
        hyp_ngrams = Counter(
            tuple(hypothesis[i:i+n]) for i in range(len(hypothesis) - n + 1)
        )
        
        overlap = sum((ref_ngrams & hyp_ngrams).values())
        total_hyp = max(len(hypothesis) - n + 1, 0)
        
        return overlap, len(hyp_ngrams), total_hyp
    
    @classmethod
    def calculate_bleu(cls, reference: str, hypothesis: str, max_n: int = 2) -> float:
        """
        Calculate simplified BLEU score.
        
        Args:
            reference: Reference text
            hypothesis: Generated hypothesis text
            max_n: Maximum n-gram size
        
        Returns:
            BLEU score (0-1)
        """
        ref_tokens = cls.tokenize(reference)
        hyp_tokens = cls.tokenize(hypothesis)
        
        if not hyp_tokens:
            return 0.0
        
        bleu_score = 0.0
        
        for n in range(1, max_n + 1):
            overlap, _, _ = cls._calculate_bleu_ngram(ref_tokens, hyp_tokens, n)
            brevity_penalty = min(1.0, len(hyp_tokens) / max(len(ref_tokens), 1))
            n_gram_score = (overlap / max(len(hyp_tokens) - n + 1, 1)) if len(hyp_tokens) >= n else 0
            bleu_score += n_gram_score * (1.0 / max_n)
        
        return bleu_score * brevity_penalty
    
    def calculate_rouge(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Calculate ROUGE scores.
        
        Args:
            reference: Reference text
            hypothesis: Generated hypothesis text
        
        Returns:
            Dictionary of ROUGE scores
        """
        if not self.rouge_scorer:
            # Fallback to simple token overlap
            return self._estimate_rouge(reference, hypothesis)
        
        try:
            scores = self.rouge_scorer.score(reference, hypothesis)
            return {
                "rouge1_precision": scores['rouge1'].precision,
                "rouge1_recall": scores['rouge1'].recall,
                "rouge1_fmeasure": scores['rouge1'].fmeasure,
                "rougeL_precision": scores['rougeL'].precision,
                "rougeL_recall": scores['rougeL'].recall,
                "rougeL_fmeasure": scores['rougeL'].fmeasure,
            }
        except Exception as e:
            logger.error(f"Error calculating ROUGE: {e}")
            return self._estimate_rouge(reference, hypothesis)
    
    @staticmethod
    def _estimate_rouge(reference: str, hypothesis: str) -> Dict[str, float]:
        """Estimate ROUGE using simple token overlap."""
        ref_tokens = RAGEvaluator.tokenize(reference)
        hyp_tokens = RAGEvaluator.tokenize(hypothesis)
        
        if not ref_tokens or not hyp_tokens:
            return {
                "rouge1_precision": 0.0,
                "rouge1_recall": 0.0,
                "rouge1_fmeasure": 0.0,
                "rougeL_precision": 0.0,
                "rougeL_recall": 0.0,
                "rougeL_fmeasure": 0.0,
            }
        
        # Calculate token overlap
        ref_counter = Counter(ref_tokens)
        hyp_counter = Counter(hyp_tokens)
        
        overlap = sum((ref_counter & hyp_counter).values())
        
        precision = overlap / len(hyp_tokens) if hyp_tokens else 0
        recall = overlap / len(ref_tokens) if ref_tokens else 0
        fmeasure = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "rouge1_precision": precision,
            "rouge1_recall": recall,
            "rouge1_fmeasure": fmeasure,
            "rougeL_precision": precision,
            "rougeL_recall": recall,
            "rougeL_fmeasure": fmeasure,
        }
    
    @staticmethod
    def calculate_token_overlap(reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Calculate token overlap metrics.
        
        Args:
            reference: Reference text
            hypothesis: Generated hypothesis text
        
        Returns:
            Dictionary of token overlap metrics
        """
        ref_tokens = set(RAGEvaluator.tokenize(reference))
        hyp_tokens = set(RAGEvaluator.tokenize(hypothesis))
        
        if not ref_tokens or not hyp_tokens:
            return {
                "jaccard_similarity": 0.0,
                "token_precision": 0.0,
                "token_recall": 0.0
            }
        
        intersection = ref_tokens & hyp_tokens
        union = ref_tokens | hyp_tokens
        
        jaccard = len(intersection) / len(union) if union else 0
        precision = len(intersection) / len(hyp_tokens) if hyp_tokens else 0
        recall = len(intersection) / len(ref_tokens) if ref_tokens else 0
        
        return {
            "jaccard_similarity": jaccard,
            "token_precision": precision,
            "token_recall": recall
        }
    
    def evaluate_answer(self, question: str, reference_answer: str, 
                       generated_answer: str) -> Dict:
        """
        Comprehensive evaluation of a generated answer.
        
        Args:
            question: The question asked
            reference_answer: Reference/ground truth answer
            generated_answer: Generated answer from RAG system
        
        Returns:
            Dictionary with multiple evaluation metrics
        """
        metrics = {
            "question": question,
            "bleu_score": self.calculate_bleu(reference_answer, generated_answer),
            "rouge_scores": self.calculate_rouge(reference_answer, generated_answer),
            "token_overlap": self.calculate_token_overlap(reference_answer, generated_answer),
            "answer_length_generated": len(generated_answer.split()),
            "answer_length_reference": len(reference_answer.split()),
        }
        
        return metrics
    
    @staticmethod
    def evaluate_retrieval(retrieved_docs: List[str], relevant_docs: List[str]) -> Dict:
        """
        Evaluate retrieval quality (precision, recall, MRR).
        
        Args:
            retrieved_docs: List of retrieved document IDs/names
            relevant_docs: List of relevant document IDs/names (ground truth)
        
        Returns:
            Dictionary with retrieval metrics
        """
        if not relevant_docs:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "mrr": 0.0}
        
        retrieved_set = set(retrieved_docs)
        relevant_set = set(relevant_docs)
        
        true_positives = len(retrieved_set & relevant_set)
        false_positives = len(retrieved_set - relevant_set)
        false_negatives = len(relevant_set - retrieved_set)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate MRR (Mean Reciprocal Rank)
        mrr = 0.0
        for i, doc in enumerate(retrieved_docs, 1):
            if doc in relevant_set:
                mrr = 1.0 / i
                break
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "mrr": mrr,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives
        }
