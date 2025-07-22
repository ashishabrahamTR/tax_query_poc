"""
CLINE (Custom Language Intelligence & Natural Entity) processing module.
Provides natural language understanding and mapping capabilities.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

class ClINE:
    def __init__(self):
        """Initialize CLINE agent with context and mapping data."""
        self.context = {}
        self.mapping_data = self.load_mapping_data()
        self.current_year = datetime.now().year

    def load_mapping_data(self) -> List[Dict]:
        """Load the tax form mapping data."""
        try:
            mapping_path = Path(__file__).parent.parent.parent / "mapping" / "1040Mapping.json"
            with open(mapping_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading mapping file: {str(e)}")
            return []

    def semantic_match(self, query: str, target: str) -> float:
        """
        Calculate semantic similarity between query and target.
        In a full implementation, this would use an actual LLM for semantic matching.
        
        Args:
            query: User's query text
            target: Target text to match against
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not query or not target:
            return 0
            
        # For now, using simple word overlap
        query_words = set(query.lower().split())
        target_words = set(target.lower().split())
        
        if not query_words or not target_words:
            return 0
            
        intersection = query_words.intersection(target_words)
        return len(intersection) / max(len(query_words), len(target_words))

    def extract_year(self, text: str) -> int:
        """Extract year from query text."""
        text_lower = text.lower()
        
        # Handle relative years
        if "this year" in text_lower:
            return self.current_year
        elif "last year" in text_lower:
            return self.current_year - 1
        elif "next year" in text_lower:
            return self.current_year + 1
            
        # Look for explicit year
        year_match = re.search(r'\b(20\d{2})\b', text)
        if year_match:
            year = int(year_match.group(1))
            if 2020 <= year <= self.current_year + 1:
                return year
            raise ValueError(
                f"Invalid year: {year}. Please use a year between 2020 and {self.current_year + 1}"
            )
            
        raise ValueError("No year found in query. Please include a year (e.g., 2024)")

    def find_best_mapping(self, query: str) -> Optional[Dict]:
        """
        Find the best matching field in the mapping data for the given query.
        Uses semantic matching to find the most relevant mapping.
        
        Args:
            query: User's natural language query
            
        Returns:
            dict: Best matching mapping entry or None if no good match found
        """
        best_match = None
        best_score = 0
        
        for entry in self.mapping_data:
            if not entry.get('Eorg'):  # Skip entries without EORG
                continue
                
            # Get field values, ensuring they're strings
            question = str(entry.get('Question', ''))
            description = str(entry.get('Description', ''))
                
            # Calculate similarity scores
            question_score = self.semantic_match(query, question)
            desc_score = self.semantic_match(query, description)
            
            # Use the higher of the two scores
            score = max(question_score, desc_score)
            
            if score > best_score:
                best_score = score
                best_match = entry
        
        # More lenient threshold and boost for common synonyms
        if best_score > 0.15:
            return best_match
            
        # Special handling for common tax concepts and acronyms
        tax_concepts = {
            'refund': ['refund', 'overpaid', 'money back', 'return'],
            'income': ['income', 'earnings', 'salary', 'wages'],
            'tax': ['tax', 'taxes', 'taxation', 'owe', 'due'],
            'deductions': ['deductions', 'deducted', 'write-off', 'write off'],
            'adjusted gross income': ['agi', 'adjusted gross', 'gross income', 'adjusted income'],
            'itemized deductions': ['itemized', 'itemization', 'schedule a'],
            'filing status': ['filing', 'file as', 'filing as']
        }
        
        # Check if query matches any tax concepts
        query_lower = query.lower()
        for concept, synonyms in tax_concepts.items():
            if any(syn in query_lower for syn in synonyms):
                # Find first matching entry for this concept
                for entry in self.mapping_data:
                    desc = entry.get('Description', '').lower()
                    question = entry.get('Question', '').lower()
                    if entry.get('Eorg') and (concept in desc or any(syn in desc or syn in question for syn in synonyms)):
                        return entry
        
        return None

    def process(self, text: str, context: dict = None) -> dict:
        """
        Process text input using language model capabilities.
        Acts as an agent to understand the query and find relevant tax form mappings.
        
        Args:
            text: Input text to process
            context: Additional context for processing
            
        Returns:
            dict: Processing results including year and matched form field
        """
        if context:
            self.context.update(context)
            
        try:
            # Extract year
            year = self.extract_year(text)
            
            # Find best matching field
            best_match = self.find_best_mapping(text)
            if not best_match:
                raise ValueError(
                    "Could not find a matching tax form field for your query. "
                    "Please try rephrasing your question."
                )
            
            # Create query_type from Description or Question, ensuring we have a value
            query_type = best_match.get('Description') or best_match.get('Question', '')
            query_type = query_type.lower() if query_type else 'unknown'
            
            return {
                'year': year,
                'query_type': query_type,
                'form_name': best_match.get('Form_Name'),
                'field_name': best_match.get('Field_Name'),
                'eorg': best_match.get('Eorg'),
                'description': best_match.get('Description'),
                'confidence': 0.95  # Would be actual confidence in full implementation
            }
            
        except ValueError as e:
            return {'error': str(e)}
        except Exception as e:
            return {'error': f"Failed to process query: {str(e)}"}
