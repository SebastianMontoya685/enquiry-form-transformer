import os
import json
import base64
import requests
from google.cloud import pubsub_v1


# ─── CONFIG ───
PROJECT_ID    = "avian-cosmos-458703-g3"
TOPIC_ID      = "enquiry-form-submissions"
SLACK_WEBHOOK = "https://webhook.site/2a23e182-3120-45e7-a00e-f2f7725d08f5"


# Pub/Sub publisher client (only used by receive_and_publish)
publisher  = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(PROJECT_ID, TOPIC_ID)


def process_pubsub_push(request):
   # 1. Parse the Pub/Sub push envelope
   envelope = request.get_json(force=True, silent=True)
   if not envelope or "message" not in envelope:
       return ("Bad Pub/Sub envelope", 400)


   # 2. Decode the message
   encoded_data = envelope["message"].get("data")
   if not encoded_data:
       return ("Missing data field in Pub/Sub message", 400)


   try:
       decoded_data = base64.b64decode(encoded_data).decode("utf-8")
       parsed = json.loads(decoded_data)
   except Exception as e:
       return (f"Error decoding message: {e}", 400)


   # 3. Extract required fields
   email       = parsed.get("email")


   if not email:
       return ("Missing required fields", 400)


   # 4. Format the payload for Slack
   payload = {
       "Email": email or 'N/A'
}


   # 5. POST to Slack webhook
   try:
       resp = requests.post(SLACK_WEBHOOK, json=payload)
       resp.raise_for_status()
   except requests.exceptions.HTTPError as e:
       print("🔴 HTTP error:", e)
       return (f"Slack HTTP error: {e}", 502)
   except Exception as e:
       print("🔴 Slack POST failed:", e)
       return (f"Slack error: {e}", 502)


   return ("", 204)



