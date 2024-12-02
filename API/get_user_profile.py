import os
import base64
import hashlib
from requests_oauthlib import OAuth2Session
from urllib.parse import urlencode

client_id = '5343fed6b33e36d5e13504647f3e3ca5'
client_secret = '80797f0fe8f4dddb844c7908d53b6250111add2a8c8392af2db6f3c2cdfdf74b'
authorization_base_url = 'https://myanimelist.net/v1/oauth2/authorize'
token_url = 'https://myanimelist.net/v1/oauth2/token'
redirect_uri = 'https://2d0e-223-204-22-128.ngrok-free.app/callback'

# Step 1: สร้าง code_verifier และ code_challenge
def generate_code_verifier():
    # สร้าง string ของ code_verifier ที่มีความยาวระหว่าง 43-128 ตัวอักษร
    return base64.urlsafe_b64encode(os.urandom(64)).decode('utf-8').rstrip("=")

def generate_code_challenge(code_verifier):
    # สร้าง code_challenge จาก code_verifier โดยการใช้ SHA-256 แล้วแปลงเป็น base64
    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip("=")

# สร้าง code_verifier และ code_challenge
code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)

# Step 2: สร้าง OAuth2Session ที่รองรับ PKCE
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)

# Step 3: ส่งผู้ใช้ไปยังหน้า Authorization พร้อม code_challenge
authorization_url, state = oauth.authorization_url(
    authorization_base_url,
    code_challenge=code_challenge,
    code_challenge_method='S256'
)

print('Please go to this URL and authorize the app:', authorization_url)

# Step 4: รับ authorization code จาก URL หลังจากที่ผู้ใช้อนุญาต
redirect_response = input('Paste the full redirect URL here:')

# Step 5: แลก Authorization Code เป็น Access Token
try:
    oauth.fetch_token(token_url, authorization_response=redirect_response, client_secret=client_secret, code_verifier=code_verifier)
    print('Token received successfully.')
except Exception as e:
    print(f"Error fetching token: {e}")

# Step 6: ดึงข้อมูลจาก API ด้วย Access Token
try:
    response = oauth.get('https://api.myanimelist.net/v1/users/@me')
    if response.status_code == 200:
        print('User data:', response.json())
    else:
        print(f"Error: Unable to fetch user data. Status code: {response.status_code}")
except Exception as e:
    print(f"Error making API request: {e}")
