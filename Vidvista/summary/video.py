import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyApREJ_L5ngbgcrX8cCvu74bkbOUsaXJTI")


# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

def summariza_text(result):
  # input
  response = chat_session.send_message("summarize in one paragraph without asterisk :"+result)
  return response.text