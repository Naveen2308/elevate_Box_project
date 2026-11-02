import re
from typing import Dict, Any, Tuple

class DecisionClassifier:
    """
    Classifies buyer intent into HOT, WARM, or COLD based on conversational context,
    sentiment, buying signals, and objections.
    """

    HOT_INDICATORS = [
        "ready", "start", "quote", "send proposal", "price", "how much", "cost", 
        "budget is good", "2 weeks", "1 week", "asap", "immediately", "call me back right now",
        "send details on whatsapp", "urgent", "let's do it", "chala urgent", "tvaraga", 
        "entha avtundi", "jald se jald", "whatsapp pe bhejo", "demo dikhao", "razorpay"
    ]

    WARM_INDICATORS = [
        "call me later", "call tomorrow", "meeting", "busy", "budget is tight", 
        "partner", "brother", "director", "discuss with team", "next month", 
        "after 2 weeks", "not now", "repu matladadam", "repu call chey", 
        "kal baat karte", "kal subah", "kal shaam", "soch ke batata"
    ]

    COLD_INDICATORS = [
        "not interested", "just looking", "no need", "wrong number", "who are you", 
        "don't call", "vadhu", "avsaram ledu", "nahi chahiye", "kya kaam hai"
    ]

    def classify(self, full_dialogue: str, latest_utterance: str) -> Tuple[str, float, str]:
        """
        Returns: (Intent: 'HOT'|'WARM'|'COLD', Confidence: float, Reason: str)
        """
        combined = f"{full_dialogue} {latest_utterance}".lower()
        latest = latest_utterance.lower()

        # Check Cold first
        if any(w in latest for w in self.COLD_INDICATORS):
            return "COLD", 0.90, "Caller indicated disinterest or casual inquiry with no active intent."

        # Check Hot indicators
        hot_matches = [w for w in self.HOT_INDICATORS if w in latest or w in combined]
        if len(hot_matches) >= 2 or ("whatsapp" in latest and any(w in latest for w in ["send", "bhejo", "pampu", "details", "price"])):
            return "HOT", 0.95, f"High buying intent detected with active interest in timeline/pricing/WhatsApp preview ({', '.join(hot_matches[:3])})."

        # Check Warm indicators (Callback / Decision barrier)
        warm_matches = [w for w in self.WARM_INDICATORS if w in latest or w in combined]
        if len(warm_matches) >= 1:
            return "WARM", 0.88, f"Interested lead with timing/budget barrier or callback request ({', '.join(warm_matches[:3])})."

        # Default classification based on length and engagement
        if len(combined.split()) > 40:
            return "WARM", 0.70, "Engaged in conversation exploring options."
        
        return "COLD", 0.50, "Initial inquiry stage, qualifying in progress."

    def extract_qualification_facts(self, dialogue: str) -> Dict[str, Any]:
        """
        Extracts structured qualification data: products, budget, timeline, features, barrier.
        """
        dialogue_lower = dialogue.lower()

        # Products extraction
        products = "E-commerce Goods"
        if re.search(r'(cloth|apparel|dress|fashion|saree|garment|shirt)', dialogue_lower):
            products = "Fashion & Apparel"
        elif re.search(r'(jewel|gold|silver|necklace|ring|imitation)', dialogue_lower):
            products = "Jewelry & Accessories"
        elif re.search(r'(grocery|food|organic|spices|tea|coffee|snack)', dialogue_lower):
            products = "Food & Grocery"
        elif re.search(r'(electronic|gadget|mobile|laptop|accessories)', dialogue_lower):
            products = "Electronics & Tech"
        elif re.search(r'(handicraft|craft|pottery|gift)', dialogue_lower):
            products = "Custom Crafts & Gifts"

        # Budget extraction
        budget_match = re.search(r'(\d+[\d,]*\s*(k|thousand|lakh|rupees|rs|inr)?)', dialogue_lower)
        budget = budget_match.group(0) if budget_match else "Under discussion"

        # Timeline extraction
        timeline = "Flexible"
        if re.search(r'(asap|1 week|2 weeks|immediate|urgent|this week)', dialogue_lower):
            timeline = "1-2 Weeks (Urgent)"
        elif re.search(r'(month|3 weeks|next month)', dialogue_lower):
            timeline = "Within a Month"

        # Features extraction
        features = []
        if re.search(r'(payment|razorpay|upi|cash on delivery|cod|phonepe)', dialogue_lower):
            features.append("UPI & Razorpay Payment Gateway")
        if re.search(r'(shiprocket|delivery|courier|tracking|shipping)', dialogue_lower):
            features.append("Automated Shipping & Tracking")
        if re.search(r'(mobile app|android|ios|pwa)', dialogue_lower):
            features.append("Mobile App / PWA")
        if not features:
            features = ["High-speed Next.js Storefront", "UPI Payments", "Inventory Management"]

        # Barrier extraction
        barrier = "None"
        if "brother" in dialogue_lower or "partner" in dialogue_lower:
            barrier = "Needs consultation with business partner / brother"
        elif "budget" in dialogue_lower:
            barrier = "Budget constraints / Price verification"
        elif "meeting" in dialogue_lower or "busy" in dialogue_lower:
            barrier = "Currently occupied / Requested callback"

        return {
            "products": products,
            "budget": budget,
            "timeline": timeline,
            "features": ", ".join(features),
            "barrier": barrier
        }

decision_classifier = DecisionClassifier()
