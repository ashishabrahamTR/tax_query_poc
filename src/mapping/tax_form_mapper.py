import json
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

class TaxFormMapper:
    def __init__(self, mapping_file: str = "1040Mapping.json"):
        """
        Initialize TaxFormMapper with tax form mapping data.
        
        Args:
            mapping_file (str): Path to mapping JSON file
        """
        self.mapping_data = []
        self.load_mapping(mapping_file)

    def load_mapping(self, file_path: str) -> None:
        """
        Load tax form mapping data from JSON file.
        
        Args:
            file_path (str): Path to mapping file
        """
        try:
            # Get the directory of the current file
            current_dir = Path(__file__).parent
            mapping_path = current_dir / file_path
            
            with open(mapping_path, 'r') as f:
                self.mapping_data = json.load(f)
                print(f"Loaded {len(self.mapping_data)} mappings")
        except Exception as e:
            print(f"Error loading mapping file: {str(e)}")
            self.mapping_data = []

    def find_mapping(self, query_type: str) -> Optional[Dict[str, Any]]:
        """
        Find mapping entry for a query type based on Description.
        
        Args:
            query_type (str): The type of query (e.g., 'total income')
            
        Returns:
            dict: Mapping entry if found, None otherwise
        """
        # Create a lookup dictionary from descriptions to entries
        query_words = set(query_type.lower().split())
        
        for entry in self.mapping_data:
            # Check Description field
            if entry.get('Description'):
                desc_words = set(entry['Description'].lower().split())
                # If all query words are in description
                if query_words.issubset(desc_words):
                    return entry
                
            # Check Question field
            if entry.get('Question'):
                q_words = set(entry['Question'].lower().split())
                if query_words.issubset(q_words):
                    return entry
                
        return None

    def get_query_info(self, query_type: str) -> Dict[str, str]:
        """
        Get form, field, and EORG information for a query type.
        
        Args:
            query_type (str): The type of query
            
        Returns:
            dict: Query information including form_name, field_name, and eorg
            
        Raises:
            ValueError: If no mapping found for query type
        """
        mapping = self.find_mapping(query_type)
        if not mapping:
            raise ValueError(f"No mapping found for query type: {query_type}")
            
        return {
            'form_name': mapping.get('Form_Name'),
            'field_name': mapping.get('Field_Name'),
            'eorg': mapping.get('Eorg'),
            'description': mapping.get('Description')
        }

if __name__ == "__main__":
    # Example usage
    mapper = TaxFormMapper()
    
    # Test queries
    test_queries = [
        'total income',
        'taxable income',
        'total tax',
        'refund'
    ]
    
    print("\nTesting Tax Form Mapper:")
    for query in test_queries:
        try:
            info = mapper.get_query_info(query)
            print(f"\nQuery: {query}")
            print(f"Mapping: {json.dumps(info, indent=2)}")
        except ValueError as e:
            print(f"\nError for '{query}': {str(e)}")
