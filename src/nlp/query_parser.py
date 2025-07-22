import spacy
import re
from typing import Dict
from datetime import datetime

class QueryParser:
    def __init__(self):
        """Initialize the QueryParser with spaCy model and query patterns."""
        self.nlp = spacy.load("en_core_web_sm")
        self.query_patterns = {
            'total income': r'total income|income total|sum of.*income|all.*income',
            'taxable income': r'taxable income',
            'total tax': r'total tax|tax total|tax (owed|due)|amount due|tax amount|how much tax|owe',
            'refund': r'refund|refund amount|tax refund|overpaid|over\s*paid'
        }
        self.current_year = datetime.now().year

    def extract_year(self, text: str) -> int:
        """
        Extract the year from the query text.
        
        Args:
            text (str): The query text
            
        Returns:
            int: The extracted year
        
        Raises:
            ValueError: If no valid year is found or year is out of valid range
        """
        # Look for variations of year references
        year_patterns = [
            r'\b(20\d{2})\b',  # Standard year format
            r'tax year\s+(20\d{2})',  # "tax year 2024"
            r'year\s+(20\d{2})',  # "year 2024"
            r'in\s+(20\d{2})'  # "in 2024"
        ]
        
        for pattern in year_patterns:
            year_match = re.search(pattern, text)
            if year_match:
                year = int(year_match.group(1))
                if year < 2020 or year > self.current_year + 1:
                    raise ValueError(
                        f"Invalid year: {year}. Please use a year between 2020 and {self.current_year + 1}"
                    )
                return year
                
        raise ValueError(
            "No year found in query. Please include a year (e.g., 2024) in your question."
        )

    def identify_query_type(self, doc) -> str:
        """
        Identify the type of tax query based on the processed text.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            str: The identified query type
            
        Raises:
            ValueError: If query type cannot be determined
        """
        text_lower = doc.text.lower()
        
        # Try each pattern and get all matches
        matches = []
        for query_type, pattern in self.query_patterns.items():
            if re.search(pattern, text_lower):
                matches.append(query_type)
        
        if not matches:
            supported_types = "\n".join([
                "- Total income (e.g., 'What is my total income?', 'sum of all income')",
                "- Taxable income (e.g., 'What is my taxable income?')",
                "- Total tax (e.g., 'total tax', 'tax owed', 'how much tax do I owe')",
                "- Refund (e.g., 'refund amount', 'how much did I overpay')"
            ])
            raise ValueError(
                f"Could not determine query type. Supported query types:\n{supported_types}"
            )
        
        # If multiple matches, prefer more specific matches
        if len(matches) > 1:
            priority = ['taxable income', 'total tax', 'total income', 'refund']
            for p in priority:
                if p in matches:
                    return p
        
        return matches[0]

    def parse_query(self, text: str) -> Dict[str, any]:
        """
        Parse the natural language query to extract year and query type.
        
        Args:
            text (str): The natural language query text
            
        Returns:
            dict: Contains 'year' and 'query_type'
            
        Raises:
            ValueError: If parsing fails
        """
        # Clean up the text
        text = re.sub(r'\s+', ' ', text.strip())
        
        if not text:
            raise ValueError("Empty query. Please enter a question.")
            
        # Remove common filler phrases
        text = re.sub(r'\b(the|for|taxtype|and|please|tell me|show me|what is|what\'s)\b', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        
        doc = self.nlp(text)
        
        try:
            year = self.extract_year(text)
            query_type = self.identify_query_type(doc)
            
            return {
                'year': year,
                'query_type': query_type
            }
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Failed to parse query: {str(e)}")

if __name__ == "__main__":
    # Example usage
    parser = QueryParser()
    test_queries = [
        "What is my total tax for 2024?",
        "Show me my taxable income for 2023",
        "What's my refund amount for 2024?",
        "What is the sum of all my income for 2024?",
        "How much tax do I owe for 2024?",
        "What is the amount due on my return for 2024?",
        "Tell me how much I overpaid in 2023"
    ]
    
    print("\nTesting Tax Query Parser:")
    for query in test_queries:
        try:
            result = parser.parse_query(query)
            print(f"\nQuery: {query}")
            print(f"Parsed: {result}")
        except ValueError as e:
            print(f"\nError parsing query '{query}': {str(e)}")
