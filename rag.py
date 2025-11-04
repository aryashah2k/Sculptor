"""RAG functionality for document analysis and entity extraction."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def extract_entities(documents_text: str) -> list[str]:
    """
    Extract characters and objects from documents using Together AI API.
    Returns a list of unique entity names.
    """
    try:
        # Create prompt for entity extraction
        prompt = f"""Extract a list of all unique characters and objects from the following text.
Return only the names, one per line, without numbering or additional text.

Text:
{documents_text}

Characters and Objects:"""
        
        # Call Together AI API directly
        api_key = os.getenv('TOGETHER_API_KEY')
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
            'messages': [
                {'role': 'system', 'content': 'You are a precise entity extraction assistant. Extract only character names and object names from the text. Return each name on a new line without any numbering, bullets, or extra text.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 500,
            'temperature': 0.1
        }
        
        response = requests.post(
            'https://api.together.xyz/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse the response into a list
        entities = []
        if content:
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                # Remove common prefixes like "- ", "* ", numbers, etc.
                if line:
                    # Clean up the line
                    cleaned = line.lstrip('-*•0123456789. ')
                    if cleaned and len(cleaned) > 1:
                        entities.append(cleaned)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity.lower() not in seen:
                seen.add(entity.lower())
                unique_entities.append(entity)
        
        return unique_entities if unique_entities else ["No entities found"]
        
    except Exception as e:
        raise Exception(f"Failed to extract entities: {str(e)}")
