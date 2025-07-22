# Tax Query POC

A proof-of-concept system for processing natural language tax queries and retrieving relevant tax information using EORG mappings.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

4. Configure API Integration:
   - Copy `.env.example` to `.env`
   - Update `.env` with your ODATA API token:
     ```
     ODATA_API_URL=https://gst-odata.api.qa.tr-atap-nonprod.aws.thomsonreuters.com
     ODATA_API_TOKEN=your_bearer_token_here
     ```

## Project Structure

```
tax_query_poc/
├── src/
│   ├── nlp/              # Natural Language Processing
│   ├── mapping/          # Tax Form Mapping
│   ├── api/              # ODATA API Integration
│   └── main.py          # Main application entry
├── .env                 # API Configuration (create from .env.example)
├── requirements.txt
└── README.md
```

## Usage

Run the main application:
```bash
python src/main.py
```

Example queries:
- "What is my total tax for 2024?"
- "Show me my taxable income for 2023"
- "What's my refund amount for 2024?"
- "What is the sum of all my income for 2024?"

## Components

1. Query Parser (NLP)
   - Processes natural language queries
   - Extracts year and query type
   - Supports various query patterns

2. Tax Form Mapper
   - Maps queries to EORG values
   - Handles 1040 form field mappings
   - Converts between field names and EORG identifiers

3. ODATA Client
   - Integrates with tax data API
   - Handles authentication via Bearer token
   - Transforms API responses to standard format

## API Integration

The system integrates with the ODATA API using the following components:

1. Authentication:
   - Bearer token authentication
   - Token configured via ODATA_API_TOKEN environment variable

2. API Endpoints:
   - Base URL: https://gst-odata.api.qa.tr-atap-nonprod.aws.thomsonreuters.com
   - Endpoint: /odata/v1/tax-return-data

3. Query Parameters:
   - year: Tax year
   - eorgs: EORG identifier
   - $filter: Combines taxType, formName, and fieldName

4. Response Format:
   - Transforms API response to standardized format:
     ```python
     {
         'eorg': 'FED.TTLINC',
         'year': 2024,
         'data': {
             'amount': 75000.00,
             'description': 'Total Income'
         }
     }
     ```

## Notes

- Currently supports Form 1040 queries
- Handles basic single-year queries
- Requires valid ODATA API token for live data
- Supports environment-based configuration
- Includes error handling and user feedback
