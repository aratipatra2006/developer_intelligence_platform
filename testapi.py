import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Supabase client created successfully!")

try:
    response = supabase.auth.get_session()
    print("Supabase Auth connection successful!")
    print("Current session:", response)
except Exception as e:
    print("Supabase Auth connection failed!")
    print(e)