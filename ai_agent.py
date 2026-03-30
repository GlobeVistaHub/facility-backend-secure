from google import genai
from google.genai import types

# 1. Initialize the client with your API key
# MAKE SURE TO KEEP THE QUOTES AROUND YOUR KEY
import os
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

def analyze_maintenance_request(user_message):
    """
    Takes an Arabic message from a user and uses Gemini to extract the category and description.
    """
    
    # 2. The System Instructions (The Brain)
    prompt = f"""
    You are a smart facility management assistant in Egypt. 
    Read the following customer message in Arabic.
    
    Customer Message: "{user_message}"
    
    Analyze the message and output ONLY a JSON object with two keys:
    1. "category": Must be exactly one of these: "كهرباء" (Electrical), "تكييف" (AC), or "سباكة" (Plumbing). If it doesn't fit, use "أخرى" (Other).
    2. "description": A short, clear summary of the problem in Arabic.
    
    Do not add any markdown formatting, just the raw JSON.
    """
    
    print("Sending request to Gemini...")
    
    # 3. Call the Gemini API
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- TESTING THE ENGINE ---
if __name__ == "__main__":
    # Simulate a WhatsApp message
    test_message = "التكييف عندي بينقط ميه كتير في الصالة بقاله يومين"
    
    print(f"Testing Message: {test_message}")
    
    # Run the AI
    result = analyze_maintenance_request(test_message)
    
    print("\n--- AI Analysis Result ---")
    print(result)