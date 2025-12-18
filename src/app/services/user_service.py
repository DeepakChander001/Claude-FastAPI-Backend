
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from src.app.dependencies import get_settings
from src.app.db import SupabaseClientWrapper

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        settings = get_settings()
        self.db = SupabaseClientWrapper(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def get_or_create_user(self, email: str, full_name: Optional[str] = None, avatar_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Handles the Sign Up vs Login decision using Supabase.
        
        Returns:
            Dict containing 'user' object and 'is_new' boolean.
        """
        if not self.db.client:
            logger.warning("Supabase client not active. Returning mock user.")
            return {
                "user": {"id": "mock-u-123", "email": email, "full_name": full_name or "Mock User"},
                "is_new": True
            }

        try:
            # 1. Check if user exists (Login Check)
            # We use the 'execute()' method as per supabase-py
            response = self.db.client.table("users").select("*").eq("email", email).execute()
            
            if response.data:
                # === LOGIN FLOW ===
                user = response.data[0]
                logger.info(f"User logged in: {email} (ID: {user['id']})")
                
                # Update last_login_at
                try:
                    self.db.client.table("users").update({
                        "last_login_at": datetime.utcnow().isoformat()
                    }).eq("id", user['id']).execute()
                except Exception as e:
                    logger.error(f"Failed to update last_login: {e}")
                
                return {"user": user, "is_new": False}
        
            else:
                # === SIGN UP FLOW ===
                logger.info(f"Creating new user: {email}")
                new_user_data = {
                    "email": email,
                    "full_name": full_name,
                    "avatar_url": avatar_url,
                    "provider": "google",
                    "created_at": datetime.utcnow().isoformat(),
                    "last_login_at": datetime.utcnow().isoformat()
                }
                
                insert_res = self.db.client.table("users").insert(new_user_data).execute()
                if insert_res.data:
                    return {"user": insert_res.data[0], "is_new": True}
                else:
                    raise Exception("Insert returned no data")

        except Exception as e:
            logger.error(f"Database error in get_or_create_user: {e}")
            # Fallback to allow flow to continue if DB fails
            return {
                "user": {"id": "error-fallback", "email": email},
                "is_new": False
            }
