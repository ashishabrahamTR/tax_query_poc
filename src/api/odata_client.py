from typing import Dict, Any
import os
import json
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ODataClient:
    def __init__(self, base_url: str = None, auth_token: str = None):
        """
        Initialize the ODATA client.
        
        Args:
            base_url (str, optional): Base URL for the ODATA API
            auth_token (str, optional): Authentication token
        """
        self.base_url = base_url or os.getenv('ODATA_API_URL', 
            "https://gst-odata.api.qa.tr-atap-nonprod.aws.thomsonreuters.com")
        self.auth_token = auth_token or os.getenv('ODATA_API_TOKEN', '')
        
        if not self.auth_token:
            print("Warning: No API token provided. Set ODATA_API_TOKEN in .env file")
        
    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            'accept': 'application/json;odata.metadata=minimal;odata.streaming=true',
            'Authorization': f'Bearer {self.auth_token}'
        }
        
    def transform_response(self, api_response: Dict[str, Any], eorg: str, year: int, 
                         form_name: str, field_name: str) -> Dict[str, Any]:
        """
        Transform API response to our standard format.
        
        Args:
            api_response: Raw API response
            eorg: The EORG identifier used in the request
            year: The tax year
            form_name: Name of the tax form
            field_name: Name of the field
            
        Returns:
            dict: Transformed response in our standard format
        """
        try:
            print(f"\nProcessing {len(api_response.get('value', []))} records")
            
            if not api_response.get('value'):
                return {
                    'eorg': eorg,
                    'year': year,
                    'data': None,
                    'error': 'No data found'
                }
                
            # Filter and process matching records
            matching_records = [
                record for record in api_response['value']
                if record.get('formName') == form_name and 
                   record.get('fieldName') == field_name
            ]
            
            print(f"\nFound {len(matching_records)} matching records")
            
            if not matching_records:
                return {
                    'eorg': eorg,
                    'year': year,
                    'data': None,
                    'error': f'No matching records found for {form_name} / {field_name}'
                }
            
            # Return the raw value from the first matching record
            value = matching_records[0].get('value', '')
                
            return {
                'eorg': eorg,
                'year': year,
                'data': {
                    'raw_value': value,
                    'description': field_name
                }
            }
            
        except Exception as e:
            return {
                'eorg': eorg,
                'year': year,
                'data': None,
                'error': f'Error transforming response: {str(e)}'
            }
        
    def get_data(self, eorg: str, year: int, form_name: str = None, 
                 field_name: str = None) -> Dict[str, Any]:
        """
        Get tax data for a specific EORG and year.
        
        Args:
            eorg (str): The EORG identifier
            year (int): The tax year
            form_name (str, optional): Name of the tax form
            field_name (str, optional): Name of the field
            
        Returns:
            dict: The response data in our standard format
        """
        try:
            # Build query parameters
            params = {
                'year': year,
                'eorgs': eorg,
                'taxType': '1040',
                '$top': 50,
                '$skip': 0
            }
            
            # Add form and field filters if provided
            if form_name and field_name:
                filter_params = [
                    "taxType eq '1040'",
                    f"formName eq '{form_name}'",
                    f"fieldName eq '{field_name}'",
                    "locator eq '2517KC'"
                ]
                params['$filter'] = ' and '.join(filter_params)
            
            print(f"\nRequest Parameters:")
            print(json.dumps(params, indent=2))
            
            # Make the request
            response = self.make_request('/odata/v1/tax-return-data', params)
            
            if 'error' in response:
                return {
                    'eorg': eorg,
                    'year': year,
                    'data': None,
                    'error': response['error']
                }
                
            return self.transform_response(response, eorg, year, form_name, field_name)
            
        except Exception as e:
            return {
                'eorg': eorg,
                'year': year,
                'data': None,
                'error': str(e)
            }

    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the ODATA API.
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            
        Returns:
            dict: The response data
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        try:
            print(f"\nMaking request to: {url}")
            
            response = requests.get(
                url,
                headers=self.get_headers(),
                params=params,
                timeout=30  # 30 second timeout
            )
            
            print(f"\nStatus Code: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\nRequest Error: {str(e)}")
            return {'error': str(e)}

if __name__ == "__main__":
    # Example usage
    print("\nTesting ODATA API Client...")
    client = ODataClient()
    
    # Test query
    test_params = {
        'eorg': 'FED.TTLINC',
        'year': 2024,
        'form_name': 'DUAL STATUS COMBINED',
        'field_name': 'DOMESTIC TOTAL INCOME'
    }
    
    result = client.get_data(**test_params)
    print(f"\nResult for {test_params['eorg']}, {test_params['year']}:")
    print(json.dumps(result, indent=2))
