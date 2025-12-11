import uuid
import json
import logging
from typing import Dict, Any, Generator, Optional
from curl_cffi import requests
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class ClaudeWebClient:
    """
    Unofficial client acting as a browser to talk to claude.ai.
    """
    def __init__(self, session_key: str):
        self.session_key = session_key
        # Use a fixed Chrome user agent for consistency, or generate one
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.base_url = "https://claude.ai/api"
        self.org_id: Optional[str] = None
        
        # Test connection and get Org ID on init
        self._init_connection()

    def _init_connection(self):
        """Verify cookie and get Organization ID."""
        try:
            # We impersonate Chrome 110 to pass TLS fingerprinting
            response = requests.get(
                f"{self.base_url}/organizations",
                cookies={"sessionKey": self.session_key},
                headers=self._get_headers(),
                impersonate="chrome110"
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to auth with Claude Web: {response.text}")
                raise Exception("Invalid Session Key or Blocked by Cloudflare")
                
            orgs = response.json()
            if not orgs:
                raise Exception("No organization found for this account")
                
            # Pick the first organization
            self.org_id = orgs[0]["uuid"]
            logger.info(f"Successfully authenticated with Claude Web. Org ID: {self.org_id}")
            
        except Exception as e:
            logger.error(f"Init Error: {e}")
            raise e

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://claude.ai/chats",
            "Origin": "https://claude.ai",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Connection": "keep-alive"
        }

    def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """
        Send message via internal API.
        Note: The internal API doesn't support 'max_tokens' or 'temperature' seamlessly in the same way.
        """
        request_id = str(uuid.uuid4())
        
        # 1. Create a new conversion (Internal API requires this first)
        chat_id = self._create_conversation()
        
        # 2. Append message
        full_response = ""
        for chunk in self.stream_generate(prompt, model, max_tokens, temperature, chat_id=chat_id):
            full_response += chunk
            
        return {
            "request_id": request_id,
            "output": full_response,
            "model": "claude-web-pro",
            "usage": {"input_tokens": 0, "output_tokens": len(full_response.split())}, # Unavailable in web
            "warnings": ["Generated via Unofficial Web Client"]
        }

    def _create_conversation(self) -> str:
        url = f"{self.base_url}/organizations/{self.org_id}/chat_conversations"
        payload = {
            "uuid": str(uuid.uuid4()),
            "name": ""
        }
        
        response = requests.post(
            url,
            json=payload,
            cookies={"sessionKey": self.session_key},
            headers=self._get_headers(),
            impersonate="chrome110"
        )
        
        if response.status_code not in [200, 201]:
             raise Exception(f"Failed to create chat: {response.text}")
             
        return response.json()["uuid"]

    def stream_generate(self, prompt: str, model: str, max_tokens: int, temperature: float, chat_id: str = None) -> Generator[str, None, None]:
        """
        Stream response using Server-Sent Events (SSE).
        """
        if not chat_id:
            chat_id = self._create_conversation()
            
        url = f"{self.base_url}/organizations/{self.org_id}/chat_conversations/{chat_id}/completion"
        
        payload = {
            "prompt": prompt,
            "timezone": "America/New_York",
            "model": "claude-3-opus-20240229" # Web usually defaults to latest. Overriding might not work as expected.
        }
        
        # Using requests.post(stream=True) with curl_cffi
        response = requests.post(
            url,
            json=payload,
            cookies={"sessionKey": self.session_key},
            headers=self._get_headers(),
            impersonate="chrome110",
            stream=True
        )
        
        if response.status_code != 200:
             yield f"Error: {response.status_code} - {response.text}"
             return

        # Simple SSE Parser
        for line in response.iter_lines():
            if not line:
                continue
            
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("data: "):
                data_str = decoded_line[6:]
                if data_str == "[DONE]":
                    break
                
                try:
                    data = json.loads(data_str)
                    if "completion" in data:
                        yield data["completion"]
                except:
                    pass
