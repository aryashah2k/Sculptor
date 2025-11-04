"""API clients for OpenAI and Stability AI."""
import os
import base64
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_image(prompt: str) -> bytes:
    """
    Generate a 2D image using OpenAI's DALL-E model.
    Returns the image as bytes.
    """
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
            response_format="b64_json"
        )
        
        # Decode base64 image
        image_data = base64.b64decode(response.data[0].b64_json)
        return image_data
        
    except Exception as e:
        raise Exception(f"Failed to generate image: {str(e)}")

def generate_3d_model(image_bytes: bytes, model_type: str = 'point-aware') -> bytes:
    """
    Generate a 3D model from an image using Stability AI's 3D APIs.
    
    Args:
        image_bytes: Image data as bytes
        model_type: Either 'point-aware' (1 credit) or 'fast' (3 credits)
    
    Returns the .glb file as bytes.
    """
    try:
        api_key = os.getenv('STABILITY_API_KEY')
        
        # Prepare the multipart/form-data request
        files = {
            'image': ('image.png', image_bytes, 'image/png')
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        if model_type == 'fast':
            # Stable Fast 3D - Premium quality, faster generation
            endpoint = 'https://api.stability.ai/v2beta/3d/stable-fast-3d'
            data = {}
            timeout = 120
        else:
            # Stable Point Aware 3D - Cost-effective, good quality
            endpoint = 'https://api.stability.ai/v2beta/3d/stable-point-aware-3d'
            data = {
                'texture_resolution': '2048',      # Maximum texture resolution
                'foreground_ratio': '1.0',         # Full foreground focus
                'remesh': 'quad',                  # Quad remeshing for better topology
                'vertex_count': '10000',           # Higher vertex count for detail
                'output_format': 'glb'             # GLB format output
            }
            timeout = 120
        
        # Make the API request
        response = requests.post(
            endpoint,
            headers=headers,
            files=files,
            data=data,
            timeout=timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status code {response.status_code}: {response.text}")
        
        return response.content
        
    except Exception as e:
        raise Exception(f"Failed to generate 3D model: {str(e)}")
