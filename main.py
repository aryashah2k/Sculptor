"""Sculptor - Main application entry point."""
import os
import base64
from pathlib import Path
from nicegui import ui, app
from dotenv import load_dotenv
from auth import signup_user, login_user
from database import get_user_by_id, deduct_credits
from rag import extract_entities
from api_clients import generate_image, generate_3d_model
from mock_payment import simulate_payment_success

load_dotenv()

# Session state keys
SESSION_USER_ID = 'user_id'
SESSION_USERNAME = 'username'
SESSION_CREDITS = 'credits'

# Global state for workflow
workflow_state = {
    'entities': [],
    'selected_entity': None,
    'generated_image': None,
    'generated_3d_model': None
}

def get_current_user():
    """Get current user from session."""
    user_id = app.storage.user.get(SESSION_USER_ID)
    if user_id:
        return get_user_by_id(user_id)
    return None

def update_session_credits():
    """Update credits in session from database."""
    user = get_current_user()
    if user:
        app.storage.user[SESSION_CREDITS] = user.credits
        return user.credits
    return 0

def require_auth(func):
    """Decorator to require authentication."""
    from functools import wraps
    @wraps(func)
    def wrapper():
        if not app.storage.user.get(SESSION_USER_ID):
            ui.navigate.to('/login')
            return
        return func()
    return wrapper

@ui.page('/')
def index():
    """Landing page - redirects to login or main app."""
    if app.storage.user.get(SESSION_USER_ID):
        ui.navigate.to('/app')
    else:
        ui.navigate.to('/login')

@ui.page('/login')
def login_page():
    """Login and signup page."""
    if app.storage.user.get(SESSION_USER_ID):
        ui.navigate.to('/app')
        return
    
    # Add custom styling
    ui.query('body').style('background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);')
    
    with ui.card().classes('absolute-center w-96 shadow-2xl'):
        # Logo/Title section
        with ui.column().classes('w-full items-center mb-6'):
            ui.label('🎨').classes('text-6xl mb-2')
            ui.label('Sculptor').classes('text-4xl font-bold text-center bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent')
            ui.label('Transform Text into 3D Models').classes('text-sm text-gray-500 text-center mt-2')
        
        with ui.tabs().classes('w-full') as tabs:
            login_tab = ui.tab('Login')
            signup_tab = ui.tab('Sign Up')
        
        with ui.tab_panels(tabs, value=login_tab).classes('w-full'):
            # Login panel
            with ui.tab_panel(login_tab):
                login_username = ui.input('Username').classes('w-full')
                login_password = ui.input('Password', password=True, password_toggle_button=True).classes('w-full')
                
                def do_login():
                    # Validate inputs
                    if not login_username.value or not login_password.value:
                        ui.notify('Please fill in all fields', type='negative')
                        return
                    
                    try:
                        success, message, user = login_user(login_username.value, login_password.value)
                        if success:
                            app.storage.user[SESSION_USER_ID] = user.id
                            app.storage.user[SESSION_USERNAME] = user.username
                            app.storage.user[SESSION_CREDITS] = user.credits
                            ui.notify(message, type='positive')
                            ui.navigate.to('/app')
                        else:
                            ui.notify(message, type='negative')
                    except Exception as e:
                        ui.notify(f'Login error: {str(e)}', type='negative')
                
                ui.button('Log In', on_click=do_login).classes('w-full')
            
            # Signup panel
            with ui.tab_panel(signup_tab):
                signup_username = ui.input('Username').classes('w-full')
                signup_password = ui.input('Password', password=True, password_toggle_button=True).classes('w-full')
                signup_confirm = ui.input('Confirm Password', password=True, password_toggle_button=True).classes('w-full')
                
                def do_signup():
                    # Validate inputs
                    if not signup_username.value or not signup_password.value:
                        ui.notify('Please fill in all fields', type='negative')
                        return
                    
                    if signup_password.value != signup_confirm.value:
                        ui.notify('Passwords do not match', type='negative')
                        return
                    
                    if len(signup_password.value) < 6:
                        ui.notify('Password must be at least 6 characters', type='negative')
                        return
                    
                    try:
                        success, message = signup_user(signup_username.value, signup_password.value)
                        if success:
                            # Auto-login after signup
                            _, _, user = login_user(signup_username.value, signup_password.value)
                            app.storage.user[SESSION_USER_ID] = user.id
                            app.storage.user[SESSION_USERNAME] = user.username
                            app.storage.user[SESSION_CREDITS] = user.credits
                            ui.notify(f'{message}! You have 5 free credits.', type='positive')
                            ui.navigate.to('/app')
                        else:
                            ui.notify(message, type='negative')
                    except Exception as e:
                        ui.notify(f'Signup error: {str(e)}', type='negative')
                
                ui.button('Sign Up', on_click=do_signup).classes('w-full')

@ui.page('/app')
@require_auth
def main_app():
    """Main application page."""
    username = app.storage.user.get(SESSION_USERNAME, 'User')
    credits = app.storage.user.get(SESSION_CREDITS, 0)
    
    # Add custom styling for main app
    ui.query('body').style('background: linear-gradient(to bottom, #f8fafc 0%, #e2e8f0 100%);')
    
    # Header with gradient
    with ui.header().classes('items-center justify-between shadow-lg').style('background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'):
        with ui.row().classes('items-center gap-2'):
            ui.label('🎨').classes('text-3xl')
            ui.label('Sculptor').classes('text-2xl font-bold text-white')
        with ui.row().classes('items-center gap-4'):
            with ui.card().classes('bg-white/20 backdrop-blur'):
                credit_label = ui.label(f'💎 {credits} Credits').classes('text-lg text-white font-bold px-2')
            ui.label(f'👤 {username}').classes('text-lg text-white font-semibold')
            
            def do_logout():
                app.storage.user.clear()
                ui.navigate.to('/login')
            
            ui.button('Logout', on_click=do_logout, icon='logout').props('flat color=white')
    
    # Main content with container
    with ui.column().classes('w-full max-w-7xl mx-auto p-8 gap-8'):
        # Hero section
        with ui.card().classes('w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-xl'):
            with ui.column().classes('p-6 items-center w-full'):
                ui.label('Transform Text into 3D Models').classes('text-4xl font-bold text-center w-full')
                ui.label('Upload documents, extract entities, generate images, and create production-ready 3D models').classes('text-lg text-center mt-2 opacity-90 w-full')
                with ui.row().classes('gap-4 mt-4 justify-center w-full'):
                    ui.label('✨ AI-Powered').classes('bg-white/20 px-4 py-2 rounded-full')
                    ui.label('🚀 Fast Generation').classes('bg-white/20 px-4 py-2 rounded-full')
                    ui.label('💎 High Quality').classes('bg-white/20 px-4 py-2 rounded-full')
        
        # Step 1: Document Upload and Analysis
        with ui.card().classes('w-full shadow-lg hover:shadow-xl transition-shadow'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.label('📄').classes('text-3xl')
                ui.label('Step 1: Upload and Analyze Documents').classes('text-2xl font-bold text-gray-800')
            
            uploaded_files = []
            entities_list = ui.column()
            selected_entity = {'value': None}
            
            async def handle_upload(e):
                try:
                    # In NiceGUI 3.2.0, use e.file to access the uploaded file
                    # Read the file content - it might be async
                    if hasattr(e.file, 'read'):
                        content = e.file.read()
                        # If it's a coroutine, await it
                        if hasattr(content, '__await__'):
                            content = await content
                    else:
                        content = e.file
                    
                    if isinstance(content, bytes):
                        content = content.decode('utf-8')
                    
                    uploaded_files.append(content)
                    ui.notify(f'Uploaded document successfully', type='positive')
                except Exception as ex:
                    ui.notify(f'Upload error: {str(ex)}', type='negative')
            
            upload_component = ui.upload(
                label='Upload Documents (.txt, .md)',
                on_upload=handle_upload,
                multiple=True,
                auto_upload=True
            ).props('accept=".txt,.md"').classes('w-full')
            
            async def analyze_documents():
                if not uploaded_files:
                    ui.notify('Please upload at least one document', type='warning')
                    return
                
                # Show loading
                with ui.dialog() as dialog, ui.card():
                    ui.label('Analyzing documents...')
                    ui.spinner(size='lg')
                dialog.open()
                
                try:
                    # Combine all documents - ensure all are strings
                    text_items = [item for item in uploaded_files if isinstance(item, str)]
                    
                    if not text_items:
                        dialog.close()
                        ui.notify('No valid text content found', type='negative')
                        return
                    
                    combined_text = '\n\n'.join(text_items)
                    
                    # Extract entities using asyncio to avoid blocking
                    import asyncio
                    loop = asyncio.get_event_loop()
                    entities = await loop.run_in_executor(None, extract_entities, combined_text)
                    workflow_state['entities'] = entities
                    
                    # Update UI
                    entities_list.clear()
                    with entities_list:
                        ui.label('Select a character or object:').classes('font-bold mb-2')
                        radio_group = ui.radio(
                            entities,
                            value=entities[0] if entities else None,
                            on_change=lambda e: selected_entity.update({'value': e.value})
                        ).props('inline')
                        selected_entity['value'] = entities[0] if entities else None
                    
                    dialog.close()
                    ui.notify(f'Found {len(entities)} entities', type='positive')
                    
                except Exception as e:
                    dialog.close()
                    ui.notify(f'Error: {str(e)}', type='negative')
            
            ui.button('Analyze Documents', on_click=analyze_documents, icon='search').classes('mt-4')
        
        # Step 2: Image Generation
        with ui.card().classes('w-full shadow-lg hover:shadow-xl transition-shadow'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.label('🖼️').classes('text-3xl')
                ui.label('Step 2: Generate 2D Image').classes('text-2xl font-bold text-gray-800')
            
            modifications_input = ui.textarea(
                'Additional details or style modifications:',
                placeholder='e.g., "in a fantasy art style, with vibrant colors"'
            ).classes('w-full')
            
            image_container = ui.column().classes('w-full items-center')
            
            async def generate_2d_image():
                if not selected_entity.get('value'):
                    ui.notify('Please select an entity first', type='warning')
                    return
                
                # Check credits
                current_credits = update_session_credits()
                if current_credits < 1:
                    ui.notify('Insufficient credits. Please purchase more credits.', type='negative')
                    return
                
                # Show loading
                with ui.dialog() as dialog, ui.card():
                    ui.label('Generating image...')
                    ui.spinner(size='lg')
                dialog.open()
                
                try:
                    # Create prompt
                    entity = selected_entity['value']
                    modifications = modifications_input.value or ''
                    prompt = f"{entity}"
                    if modifications:
                        prompt += f", {modifications}"
                    
                    # Generate image using asyncio to avoid blocking
                    import asyncio
                    loop = asyncio.get_event_loop()
                    image_bytes = await loop.run_in_executor(None, generate_image, prompt)
                    workflow_state['generated_image'] = image_bytes
                    
                    # Deduct credit
                    user_id = app.storage.user.get(SESSION_USER_ID)
                    if deduct_credits(user_id, 1):
                        new_credits = update_session_credits()
                        credit_label.text = f'Credits: {new_credits}'
                    
                    # Display image
                    image_container.clear()
                    with image_container:
                        ui.label('Generated Image:').classes('font-bold mb-2')
                        image_b64 = base64.b64encode(image_bytes).decode()
                        ui.image(f'data:image/png;base64,{image_b64}').classes('max-w-md border rounded')
                        
                        # Download button for image
                        def download_image():
                            ui.download(image_bytes, 'generated_image.png')
                        
                        ui.button('Download Image', on_click=download_image, icon='download').props('color=primary').classes('mt-2')
                    
                    dialog.close()
                    ui.notify('Image generated successfully!', type='positive')
                    
                except Exception as e:
                    dialog.close()
                    ui.notify(f'Error: {str(e)}', type='negative')
            
            ui.button('Generate Image (1 Credit)', on_click=generate_2d_image, icon='image').classes('mt-4')
        
        # Step 3: 3D Model Generation
        with ui.card().classes('w-full shadow-lg hover:shadow-xl transition-shadow'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.label('🎲').classes('text-3xl')
                ui.label('Step 3: Generate 3D Model').classes('text-2xl font-bold text-gray-800')
            
            # Model selection dropdown
            ui.label('Select 3D Model Quality:').classes('font-bold mb-2')
            model_select = ui.select(
                options={
                    'point-aware': 'Stable Point Aware 3D (1 Credit) - Cost-effective, good quality',
                    'fast': 'Stable Fast 3D (3 Credits) - Premium quality, faster generation'
                },
                value='point-aware',
                label='3D Model Type'
            ).classes('w-full mb-4')
            
            model_container = ui.column().classes('w-full items-center')
            
            async def generate_3d():
                if not workflow_state.get('generated_image'):
                    ui.notify('Please generate an image first', type='warning')
                    return
                
                # Get selected model and credit cost
                selected_model = model_select.value
                credit_cost = 3 if selected_model == 'fast' else 1
                
                # Check credits
                current_credits = update_session_credits()
                if current_credits < credit_cost:
                    ui.notify(f'Insufficient credits. Need {credit_cost} credits for this model.', type='negative')
                    return
                
                # Show loading
                with ui.dialog() as dialog, ui.card():
                    ui.label('Generating 3D model... This may take a minute.')
                    ui.spinner(size='lg')
                dialog.open()
                
                try:
                    # Generate 3D model using asyncio to avoid blocking
                    import asyncio
                    loop = asyncio.get_event_loop()
                    model_bytes = await loop.run_in_executor(None, generate_3d_model, workflow_state['generated_image'], selected_model)
                    workflow_state['generated_3d_model'] = model_bytes
                    
                    # Save model to file
                    model_path = Path('generated_model.glb')
                    model_path.write_bytes(model_bytes)
                    
                    # Deduct credits based on model type
                    user_id = app.storage.user.get(SESSION_USER_ID)
                    if deduct_credits(user_id, credit_cost):
                        new_credits = update_session_credits()
                        credit_label.text = f'💎 {new_credits} Credits'
                    
                    # Display download option
                    model_container.clear()
                    with model_container:
                        ui.label('✅ 3D Model Generated Successfully!').classes('text-xl font-bold mb-4 text-green-600')
                        ui.label(f'Model size: {len(model_bytes) / 1024:.1f} KB').classes('text-gray-600 mb-4')
                        
                        # Download button
                        def download_model():
                            ui.download(model_bytes, 'model.glb')
                        
                        ui.button('Download .glb File', on_click=download_model, icon='download').props('color=primary size=lg')
                        
                        ui.label('You can view this .glb file in:').classes('mt-4 font-bold')
                        with ui.column().classes('ml-6 text-gray-600'):
                            ui.label('• Blender (free 3D software)')
                            ui.label('• Windows 3D Viewer')
                            ui.label('• Online viewers like gltf-viewer.donmccurdy.com')
                    
                    dialog.close()
                    ui.notify('3D model generated successfully!', type='positive')
                    
                except Exception as e:
                    dialog.close()
                    ui.notify(f'Error: {str(e)}', type='negative')
            
            # Dynamic button that updates based on selection
            generate_button = ui.button('Generate 3D Model (1 Credit)', on_click=generate_3d, icon='view_in_ar').classes('mt-4')
            
            def update_button_text():
                credit_cost = 3 if model_select.value == 'fast' else 1
                generate_button.text = f'Generate 3D Model ({credit_cost} Credit{"s" if credit_cost > 1 else ""})'
            
            model_select.on_value_change(lambda: update_button_text())
        
        # Step 4: Custom Image to 3D
        with ui.card().classes('w-full shadow-lg hover:shadow-xl transition-shadow'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.label('📸').classes('text-3xl')
                ui.label('Step 4: Upload Custom Image for 3D Conversion').classes('text-2xl font-bold text-gray-800')
            ui.label('Upload your own image to convert it directly to a 3D model').classes('text-gray-600 mb-4')
            
            custom_image_data = {'bytes': None}
            custom_image_preview = ui.column()
            custom_3d_container = ui.column().classes('w-full items-center')
            
            async def handle_custom_image_upload(e):
                try:
                    # Read file content - handle if it's a coroutine
                    content = e.file.read()
                    if hasattr(content, '__await__'):
                        content = await content
                    
                    if isinstance(content, bytes):
                        custom_image_data['bytes'] = content
                    else:
                        raise Exception(f"Unexpected content type: {type(content)}")
                    
                    # Show preview
                    custom_image_preview.clear()
                    with custom_image_preview:
                        ui.label('Uploaded Image Preview:').classes('font-bold mb-2')
                        image_b64 = base64.b64encode(content).decode()
                        ui.image(f'data:image/png;base64,{image_b64}').classes('max-w-md border rounded')
                    
                    ui.notify('Image uploaded successfully', type='positive')
                except Exception as ex:
                    ui.notify(f'Upload error: {str(ex)}', type='negative')
            
            ui.upload(
                label='Upload Image (.png, .jpg)',
                on_upload=handle_custom_image_upload,
                auto_upload=True
            ).props('accept="image/*"').classes('w-full')
            
            # Model selection dropdown for custom image
            ui.label('Select 3D Model Quality:').classes('font-bold mb-2 mt-4')
            custom_model_select = ui.select(
                options={
                    'point-aware': 'Stable Point Aware 3D (1 Credit) - Cost-effective, good quality',
                    'fast': 'Stable Fast 3D (3 Credits) - Premium quality, faster generation'
                },
                value='point-aware',
                label='3D Model Type'
            ).classes('w-full mb-4')
            
            async def generate_custom_3d():
                if not custom_image_data['bytes']:
                    ui.notify('Please upload an image first', type='warning')
                    return
                
                # Get selected model and credit cost
                selected_custom_model = custom_model_select.value
                custom_credit_cost = 3 if selected_custom_model == 'fast' else 1
                
                # Check credits
                current_credits = update_session_credits()
                if current_credits < custom_credit_cost:
                    ui.notify(f'Insufficient credits. Need {custom_credit_cost} credits for this model.', type='negative')
                    return
                
                # Show loading
                with ui.dialog() as dialog, ui.card():
                    ui.label('Converting image to 3D model... This may take a minute.')
                    ui.spinner(size='lg')
                dialog.open()
                
                try:
                    # Generate 3D model using asyncio to avoid blocking
                    import asyncio
                    loop = asyncio.get_event_loop()
                    model_bytes = await loop.run_in_executor(None, generate_3d_model, custom_image_data['bytes'], selected_custom_model)
                    
                    # Save model to file
                    model_path = Path('custom_model.glb')
                    model_path.write_bytes(model_bytes)
                    
                    # Deduct credits based on model type
                    user_id = app.storage.user.get(SESSION_USER_ID)
                    if deduct_credits(user_id, custom_credit_cost):
                        new_credits = update_session_credits()
                        credit_label.text = f'💎 {new_credits} Credits'
                    
                    # Display download option
                    custom_3d_container.clear()
                    with custom_3d_container:
                        ui.label('✅ 3D Model Generated Successfully!').classes('text-xl font-bold mb-4 text-green-600')
                        ui.label(f'Model size: {len(model_bytes) / 1024:.1f} KB').classes('text-gray-600 mb-4')
                        
                        # Download button
                        def download_custom_model():
                            ui.download(model_bytes, 'custom_model.glb')
                        
                        ui.button('Download .glb File', on_click=download_custom_model, icon='download').props('color=primary size=lg')
                        
                        ui.label('You can view this .glb file in:').classes('mt-4 font-bold')
                        with ui.column().classes('ml-6 text-gray-600'):
                            ui.label('• Blender (free 3D software)')
                            ui.label('• Windows 3D Viewer')
                            ui.label('• Online viewers like gltf-viewer.donmccurdy.com')
                    
                    dialog.close()
                    ui.notify('3D model generated successfully!', type='positive')
                    
                except Exception as e:
                    dialog.close()
                    ui.notify(f'Error: {str(e)}', type='negative')
            
            # Dynamic button that updates based on selection
            custom_generate_button = ui.button('Convert to 3D Model (1 Credit)', on_click=generate_custom_3d, icon='view_in_ar').classes('mt-4')
            
            def update_custom_button_text():
                custom_credit_cost = 3 if custom_model_select.value == 'fast' else 1
                custom_generate_button.text = f'Convert to 3D Model ({custom_credit_cost} Credit{"s" if custom_credit_cost > 1 else ""})'
            
            custom_model_select.on_value_change(lambda: update_custom_button_text())
        
        # Credit Purchase Section (Mock Payment for Testing)
        with ui.card().classes('w-full shadow-lg bg-gradient-to-r from-blue-50 to-purple-50'):
            with ui.row().classes('items-center gap-3 mb-2'):
                ui.label('💳').classes('text-3xl')
                ui.label('Need More Credits?').classes('text-2xl font-bold text-gray-800')
            ui.label('Enter payment password to get 10 credits (Mock Payment - Testing Only)').classes('text-gray-600 mb-4')
            
            async def buy_credits():
                # Create password dialog
                with ui.dialog() as password_dialog, ui.card().classes('w-96'):
                    ui.label('Payment Verification').classes('text-xl font-bold mb-4')
                    ui.label('Enter the payment password to add credits:').classes('mb-2')
                    
                    password_input = ui.input(
                        'Password',
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full')
                    
                    async def verify_and_add_credits():
                        try:
                            user_id = app.storage.user.get(SESSION_USER_ID)
                            password = password_input.value
                            
                            if not password:
                                ui.notify('Please enter a password', type='warning')
                                return
                            
                            # Simulate payment with password verification
                            success, message = simulate_payment_success(user_id, password, 10)
                            
                            if success:
                                new_credits = update_session_credits()
                                credit_label.text = f'Credits: {new_credits}'
                                ui.notify(f'✅ {message}', type='positive')
                                password_dialog.close()
                            else:
                                ui.notify(f'❌ {message}', type='negative')
                        
                        except Exception as e:
                            ui.notify(f'Error: {str(e)}', type='negative')
                    
                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancel', on_click=password_dialog.close).props('flat')
                        ui.button('Add Credits', on_click=verify_and_add_credits).props('color=primary')
                
                password_dialog.open()
            
            ui.button('Buy Credits', on_click=buy_credits, icon='shopping_cart').props('color=primary')

# Webhook endpoint removed - using mock payment system for testing

# Run the application
if __name__ in {'__main__', '__mp_main__'}:
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv('PORT', 8080))
    
    ui.run(
        title='Sculptor',
        port=port,
        host='0.0.0.0',  # Required for Railway
        storage_secret=os.getenv('SECRET_KEY', 'sculptor-secret-key'),
        reload=False  # Disable reload in production
    )
