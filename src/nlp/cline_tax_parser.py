from typing import Dict, Any
from .cline import ClINE

class ClineTaxParser:
    def __init__(self):
        """
        Initialize ClineTaxParser with CLINE agent for natural language 
        understanding and mapping.
        """
        self.cline = ClINE()

    def parse_query(self, text: str) -> Dict[str, Any]:
        """
        Use CLINE agent to parse the natural language query and map to tax form fields.
        
        Args:
            text (str): The natural language query text
            
        Returns:
            dict: Contains parsed information including:
                - year
                - query_type
                - form_name
                - field_name
                - eorg
                - description
            
        Raises:
            ValueError: If parsing fails
        """
        if not text:
            raise ValueError("Empty query. Please enter a question.")
            
        try:
            # Let CLINE process the query and find mapping
            result = self.cline.process(text)
            
            if 'error' in result:
                raise ValueError(result['error'])
                
            return result
                
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Failed to process query: {str(e)}")

if __name__ == "__main__":
    # Example usage
    parser = ClineTaxParser()
    
    test_queries = [
        "What is my total tax for 2024?",
        "Show me my taxable income for 2023",
        "What's my refund amount for 2024?",
        "What is the sum of all my income for 2024?",
        "How much tax do I owe for 2024?",
        "What is the amount due on my return for 2024?",
        "Tell me how much I overpaid in 2023",
        "What's my AGI for 2024?",
        "What credits did I receive for 2023?",
        "Show my itemized deductions for tax year 2024"
    ]
    
    print("\nTesting Tax Query Parser with CLINE:")
    for query in test_queries:
        try:
            result = parser.parse_query(query)
            print(f"\nQuery: {query}")
            print("Parsed:", result)
        except ValueError as e:
            print(f"\nError parsing query '{query}': {str(e)}")
