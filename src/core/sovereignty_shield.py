import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [SHIELD]: %(message)s")
logger = logging.getLogger("SovereigntyShield")


class ContaminationError(Exception):
    """Raised when the output is too contaminated to be saved."""

    pass


class SovereigntyShield:
    """
    Administrative Layer for enforcing Sovereign Output.
    Blocks/Sanitizes LLM "Assistant" behaviors before they touch the system.
    """

    # Patterns that indicate a fundamental failure of the Kernel voice
    # (e.g., the model refusing to answer or breaking character completely)
    CRITICAL_CONTAMINANTS = [
        r"As an AI language model",
        r"I cannot fulfill",
        r"I cannot answer",
        r"I am an AI",
        r"I am a large language model",
        r"I don't have personal",
        r"I don't have feelings",
    ]

    # Patterns that are "Noise" to be surgically removed
    # (e.g., politeness, meta-commentary, signatures)
    SANITIZABLE_PATTERNS = [
        r"^Note:",
        r"^Please note:",
        r"^Here is the",
        r"^Here's the",
        r"^Sure, here",
        r"^Certainly,",
        r"^This explanation",
        r"^This analysis",
        r"^Let me know",
        r"^Please let me know",
        r"^Feel free to",
        r"^Best regards",
        r"^Kind regards",
        r"^Sincerely",
        r"^Cheers",
        r"^Yours,",
        r"\[Your Name\]",
        r"\[Name\]",
        r"\[Signature\]",
        r"^I hope this helps",
        r"^I hope that explains",
        r"^In this rewritten text",
        r"^The above text",
    ]

    def __init__(self):
        self.critical_regex = re.compile("|".join(self.CRITICAL_CONTAMINANTS), re.IGNORECASE)
        self.sanitizable_regex = re.compile(
            "|".join(self.SANITIZABLE_PATTERNS), re.IGNORECASE | re.MULTILINE
        )

    def purify(self, text: str) -> str:
        """
        Validates and Sanitizes the text.
        Raises ContaminationError if critical contamination is found.
        Returns cleaned text otherwise.
        """
        if not text:
            return ""

        # 1. Critical Check (The "No-Go" Zone)
        if self.critical_regex.search(text):
            logger.error(f"CRITICAL CONTAMINATION DETECTED. Blocking output.")
            raise ContaminationError("Output contains critical identity refusal or AI disclosure.")

        # 2. Surgical Sanitation (The "Cleanup" Zone)
        # We process line by line to allow the scientific content to stay while removing meta-headers/footers.
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped_line = line.strip()
            if self.sanitizable_regex.search(stripped_line):
                logger.warning(f"Sanitizing line: '{stripped_line[:50]}...'")
                continue  # Skip this line

            cleaned_lines.append(line)

        # Reassemble
        cleaned_text = "\n".join(cleaned_lines).strip()

        # 3. Post-Sanitation Integrity Check
        if not cleaned_text:
            logger.warning("Sanitization resulted in empty text.")
            raise ContaminationError("Output was 100% noise/politeness.")

        return cleaned_text
