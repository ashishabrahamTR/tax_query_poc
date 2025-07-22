from nlp.query_parser import QueryParser
from mapping.tax_form_mapper import TaxFormMapper
from api.odata_client import ODataClient

def process_query(text: str) -> dict:
    """
    Process a natural language tax query and return the result.
    
    Args:
        text (str): The natural language query text
        
    Returns:
        dict: The processed result containing the requested tax information
    """
    parser = QueryParser()
    mapper = TaxFormMapper()
    api_client = ODataClient()
    
    try:
        # 1. Parse query to get year and type
        query_info = parser.parse_query(text)
        print(f"\nParsed Query: {query_info}")
        
        # 2. Map to tax form fields
        form_info = mapper.get_query_info(query_info['query_type'])
        print(f"\nForm Mapping: {form_info}")
        
        # 3. Get data from API
        result = api_client.get_data(
            eorg=form_info['eorg'],
            year=query_info['year'],
            form_name=form_info['form_name'],
            field_name=form_info['field_name']
        )
        
        # 4. Format and return response
        return {
            'query_type': query_info['query_type'],
            'year': query_info['year'],
            'form_info': form_info,
            'result': result
        }
    except ValueError as e:
        return {'error': str(e)}
    except Exception as e:
        return {'error': f"Failed to process query: {str(e)}"}

def print_help():
    """Print help information about supported queries."""
    print("\nSupported query types:")
    print("1. Total income: 'What is my total income for 2024?'")
    print("2. Taxable income: 'What is my taxable income for 2023?'")
    print("3. Total tax: 'What is my total tax for 2024?'")
    print("4. Refund: 'What is my refund amount for 2023?'")
    print("\nNote: Query must include a year (2020-2024)")
    print("Type 'exit' to quit\n")

if __name__ == "__main__":
    print("=== Tax Query System ===")
    print_help()
    
    while True:
        query = input("> ").strip()
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        elif query.lower() == 'help':
            print_help()
            continue
        elif not query:
            print("Please enter a query. Type 'help' for examples.")
            continue
            
        result = process_query(query)
        
        print("\nQuery:", query)
        if 'error' in result:
            print("Error:", result['error'])
            print("Type 'help' for example queries.")
        else:
            if result['result'].get('data'):
                data = result['result']['data']
                print(f"\nResult for {result['query_type']} ({result['year']}):")
                print(f"Value: {data['raw_value']}")
                print(f"Description: {data['description']}")
            else:
                print("No data found for this query.")
