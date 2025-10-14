import os
from dotenv import load_dotenv
load_dotenv()

SLACK_BOT_TOKEN=os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET=os.getenv("SLACK_SIGNING_SECRET")
SUPABASE_URL=os.getenv("SUPABASE_URL")
SUPABASE_KEY=os.getenv("SUPABASE_KEY")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")