import json
import requests
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
KEY_FILE = PROJECT_ROOT / "ibm_nlu_service_key.json"


class WatsonNLU:
    def __init__(self):
        self.apikey = None
        self.url = None
        self._load_creds()

    def _load_creds(self):
        if not KEY_FILE.exists():
            print(f"❌ NLU Key file missing: {KEY_FILE}")
            return
        with open(KEY_FILE, "r") as f:
            data = json.load(f)
            self.apikey = data.get("apikey")
            self.url = data.get("url")

    def analyze_shadow(self, text):
        """
        Analyzes the 'Shadow Tone' (Sentiment + Emotion) of a text.
        Returns a 'Psi' factor (Anxiety/Fear) derived from NLU.
        """
        if not self.apikey or not self.url:
            return None

        endpoint = f"{self.url}/v1/analyze?version=2022-04-07"

        # Features: Sentiment and Emotion
        payload = {"text": text, "features": {"sentiment": {}, "emotion": {}}}

        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=("apikey", self.apikey),
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                result = response.json()

                # Extract Shadow Metrics
                sentiment = result["sentiment"]["document"]["score"]  # -1 to 1
                emotions = result["emotion"]["document"]["emotion"]

                # Psi (Anxiety) = Fear + Sadness
                psi_nlu = emotions.get("fear", 0) + emotions.get("sadness", 0)

                return {"sentiment": sentiment, "psi_nlu": psi_nlu, "emotions": emotions}
            else:
                print(f"⚠️ NLU Error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ NLU Connection Failed: {e}")
            return None


if __name__ == "__main__":
    nlu = WatsonNLU()
    print("Testing Shadow Analysis...")
    res = nlu.analyze_shadow("I am afraid that the system will collapse under its own entropy.")
    print(json.dumps(res, indent=2))
