#!/usr/bin/env python3
import os
import json
import logging
import requests
import webbrowser
from pathlib import Path
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

def get_yandex_token():
    base_dir = Path(__file__).resolve().parents[1]
    config_dir = base_dir / "src" / "config"
    token_path = config_dir / "yandex_token.json"

    try:
        from dotenv import load_dotenv
        load_dotenv(base_dir / ".env")
    except ImportError:
        pass

    client_id = os.getenv("YANDEX_CLIENT_ID")
    client_secret = os.getenv("YANDEX_CLIENT_SECRET")

    if not client_id or not client_secret:
        log.error("Missing YANDEX_CLIENT_ID or YANDEX_CLIENT_SECRET in .env file")
        return

    redirect_uri = "https://oauth.yandex.ru/verification_code"
    
    auth_url = (
        "https://oauth.yandex.ru/authorize"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&force_confirm=true"
    )

    log.info("Opening browser for Yandex authorization...")
    webbrowser.open(auth_url)

    raw_input = input("\nEnter the code from Yandex (or full redirect URL): ").strip()
    
    code = raw_input
    if "code=" in raw_input:
        query = parse_qs(urlparse(raw_input).query)
        code = query.get("code", [raw_input])[0]

    log.info("Requesting access token...")
    
    try:
        response = requests.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=15
        )
        response.raise_for_status()
        
        token_data = response.json()
        
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=4)
            
        log.info("Success! Token saved to: %s", token_path)
        log.info("Expires in: %d days", token_data.get('expires_in', 0) // 86400)

    except requests.exceptions.RequestException as e:
        log.error("Token exchange failed: %s", e)
        if hasattr(e.response, 'text'):
            log.error("Server response: %s", e.response.text)

if __name__ == "__main__":
    get_yandex_token()
    