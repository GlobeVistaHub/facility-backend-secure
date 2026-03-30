from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from ai_agent import analyze_maintenance_request
import json
import random
import requests
import os


import os

# --- SUPABASE CLOUD CONNECTION (SECURED) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://psalaayzizmoflskttgg.supabase.co") 
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '')
    sender_phone = request.values.get('From', '')
    
    print(f"\n--- NEW MESSAGE FROM {sender_phone} ---")
    print(f"Message: {incoming_msg}")

    # 1. Send it to Gemini for analysis
    print("Sending to Gemini...")
    ai_result = analyze_maintenance_request(incoming_msg)

    # 2. Bulletproof JSON Parsing
    data = {}
    try:
        if isinstance(ai_result, str):
            cleaned_json = ai_result.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned_json)
        elif isinstance(ai_result, dict):
            data = ai_result
            
        # Failsafe if data is still a string
        if isinstance(data, str):
            data = {}
    except Exception as e:
        print(f"WARNING: Gemini Parsing Error. Falling back to default. Error: {e}")
        data = {}

    # 3. Extract safe variables
    category = data.get("category", "أخرى") if isinstance(data, dict) else "أخرى"
    description = data.get("description", incoming_msg) if isinstance(data, dict) else incoming_msg
    
    # 4. Generate Ticket Number
    ticket_num = f"TKT-{random.randint(2000, 9999)}"
    
    # 5. PUSH DIRECTLY TO SUPABASE CLOUD
    headers = {
        "apikey": SUPABASE_SECRET_KEY,
        "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    db_data = {
        "ticket_number": ticket_num,
        "phone_number": sender_phone,
        "category": category,
        "description": description,
        "status": "جديد"
        # Note: We removed 'timestamp' because Supabase adds the exact time automatically!
    }
    
    print(f"Saving Ticket {ticket_num} to Supabase...")
    try:
        db_response = requests.post(f"{SUPABASE_URL}/rest/v1/tickets", headers=headers, json=db_data)
        
        if db_response.status_code in[200, 201]:
            print("✅ Saved to Cloud successfully!")
        else:
             print(f"❌ SUPABASE ERROR: {db_response.text}")
    except Exception as e:
        print(f"❌ NETWORK ERROR: {e}")

    # 6. Formulate Reply
    reply_text = f"تم استلام بلاغك بنجاح.\nرقم الطلب: {ticket_num}\nالتصنيف: {category}\nفريقنا هيتواصل معاك قريب."
    
    # 7. Send the reply back to WhatsApp via Twilio
    resp = MessagingResponse()
    resp.message(reply_text)
    
    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    print("Cloud Listener Active. Waiting for WhatsApp messages... 🟢")
    app.run(port=5000)