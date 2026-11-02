import re
import datetime
import dateparser
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("callback_scheduler")
logger.setLevel(logging.INFO)

# In-memory store for scheduled callbacks
scheduled_callbacks_store: List[Dict[str, Any]] = []

class CallbackSchedulerService:
    def __init__(self):
        pass

    def parse_natural_time(self, phrase: str) -> Optional[datetime.datetime]:
        """
        Parses phrases like 'tomorrow morning', 'tomorrow 11 am', 'call me back at 4pm', 'next monday'
        """
        now = datetime.datetime.now()
        phrase_lower = phrase.lower()

        # Handle common vague colloquial terms in Indian business context
        if "tomorrow morning" in phrase_lower:
            tomorrow = now + datetime.timedelta(days=1)
            return tomorrow.replace(hour=10, minute=30, second=0, microsecond=0)
        elif "tomorrow afternoon" in phrase_lower:
            tomorrow = now + datetime.timedelta(days=1)
            return tomorrow.replace(hour=14, minute=30, second=0, microsecond=0)
        elif "tomorrow evening" in phrase_lower:
            tomorrow = now + datetime.timedelta(days=1)
            return tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
        elif "today evening" in phrase_lower or "this evening" in phrase_lower:
            return now.replace(hour=17, minute=30, second=0, microsecond=0)

        # Use dateparser with relative base settings
        parsed = dateparser.parse(
            phrase,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': now,
                'RETURN_AS_TIMEZONE_AWARE': False
            }
        )

        if parsed:
            # If time was not explicitly specified, default to 10:00 AM
            if parsed.hour == 0 and parsed.minute == 0:
                parsed = parsed.replace(hour=10, minute=0)
            # Ensure scheduled time is in future
            if parsed <= now:
                parsed = parsed + datetime.timedelta(days=1)

        return parsed

    def schedule_callback(
        self,
        phone_number: str,
        time_expression: str,
        notes: str = "",
        barrier_reason: str = ""
    ) -> Dict[str, Any]:
        """
        Extracts timestamp from spoken phrase and saves the scheduled booking.
        """
        scheduled_dt = self.parse_natural_time(time_expression)
        if not scheduled_dt:
            # Fallback to tomorrow morning at 10:30 AM
            scheduled_dt = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=10, minute=30, second=0, microsecond=0)

        formatted_time = scheduled_dt.strftime("%A, %B %d at %I:%M %p")
        iso_time = scheduled_dt.isoformat()

        callback_record = {
            "id": f"cb_{len(scheduled_callbacks_store) + 1}",
            "phone_number": phone_number,
            "raw_input": time_expression,
            "scheduled_time": iso_time,
            "display_time": formatted_time,
            "notes": notes,
            "barrier_reason": barrier_reason,
            "status": "SCHEDULED",
            "created_at": datetime.datetime.now().isoformat()
        }

        scheduled_callbacks_store.insert(0, callback_record)
        logger.info(f"📅 Booked callback for {phone_number} at {formatted_time} (Reason: {barrier_reason})")

        return {
            "success": True,
            "callback": callback_record,
            "spoken_confirmation": f"I have scheduled a callback for you on {formatted_time}. Our senior e-commerce architect will reach out to you then!"
        }

    def get_all_callbacks(self) -> List[Dict[str, Any]]:
        return scheduled_callbacks_store

callback_service = CallbackSchedulerService()
