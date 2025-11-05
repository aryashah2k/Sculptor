# Sculptor

A web-based application for transforming textual concepts into high-quality 2D images and production-ready 3D models.

|To progress again, man must remake himself
|------------------------------------------------------|
|![sculptor](https://github.com/aryashah2k/Sculptor/blob/main/samples/sculptor.jpg)|

## Features

1. **User Authentication** - Secure signup/login with bcrypt password hashing
2. **Credit System** - Simple mock payment system for testing
3. **Document Analysis** - LLM powered entity extraction
4. **2D Image Generation** - High quality images via OpenAI DALL-E 3
5. **3D Model Generation** - Image-to-3D conversion using Stability AI

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

The `.env` file already contains the necessary API keys:

- **OPENAI_API_KEY** - For DALL-E 3 image generation
- **STABILITY_API_KEY** - For 3D model generation
- **TOGETHER_API_KEY** - For document analysis

All keys are pre-configured and ready to use!

### 3. Run the Application

```bash
python main.py
```

The application will be available at `http://localhost:8080`

## Usage Workflow

### Step 1: Sign Up / Log In
- New users receive 5 free credits upon registration
- Existing users can log in with their credentials

### Step 2: Upload Documents
- Upload `.txt` or `.md` files containing character descriptions or object details
- Click "Analyze Documents" to extract entities using AI

### Step 3: Generate 2D Image (1 Credit)
- Select an extracted entity from the list
- Add optional style modifications
- Click "Generate Image" to create a high-quality 2D image

### Step 4: Generate 3D Model (1 Credit)
- After generating an image, click "Generate 3D Model"
- View the interactive 3D preview
- Download the `.glb` file for use in other applications

### Step 5: Get More Credits
- When credits run low, click "Buy Credits"
- Enter the payment password: `sculptor` (from SECRET_KEY in .env)
- 10 credits will be added instantly after verification
- You can change the password by editing SECRET_KEY in .env file

## Project Structure

```
sculpt/
├── main.py              # Main application entry point and UI
├── auth.py              # Authentication functions
├── database.py          # SQLAlchemy models and CRUD operations
├── api_clients.py       # OpenAI and Stability AI integrations
├── rag.py               # txtai-based entity extraction
├── mock_payment.py      # Mock payment system for testing
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
└── README.md           # This file
```

## Security Notes

- All passwords are hashed using bcrypt
- API keys are stored in `.env` (never commit this file)
- Session management uses secure cookies
- Credit deductions only occur after successful API calls

## Credits Cost

- 2D Image Generation: 1 credit
- 3D Model Generation:
  - Stable Point Aware 3D: 1 credit (cost-effective, good quality)
  - Stable Fast 3D: 3 credits (premium quality, faster generation)
- Get 10 credits by entering password

## Technologies Used

- **NiceGUI** - Web framework and UI
- **SQLAlchemy** - Database ORM
- **OpenAI** - DALL-E 3 image generation
- **Stability AI** - Stable Fast 3D model generation
- **passlib** - Password hashing
