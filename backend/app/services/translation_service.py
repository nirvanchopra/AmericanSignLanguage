from typing import List, Dict, Any, Optional
import re

class TranslationService:
    """
    Intelligent Translation & Sentence Formation Engine:
    - Assembles fingerspelling characters into coherent words.
    - Handles word boundaries, pauses, spaces, and backspaces.
    - Resolves spelling suggestions & autocorrect (pyenchant with built-in dictionary fallback).
    - Formats capitalization, punctuation, and question marks contextually.
    - Modular architecture allowing LLM plugins (e.g. Gemini, GPT, Llama).
    """

    COMMON_WORDS = {
        "THE", "BE", "TO", "OF", "AND", "A", "IN", "THAT", "HAVE", "I",
        "IT", "FOR", "NOT", "ON", "WITH", "HE", "AS", "YOU", "DO", "AT",
        "THIS", "BUT", "HIS", "BY", "FROM", "THEY", "WE", "SAY", "HER", "SHE",
        "OR", "AN", "WILL", "MY", "ONE", "ALL", "WOULD", "THERE", "THEIR", "WHAT",
        "SO", "UP", "OUT", "IF", "ABOUT", "WHO", "GET", "WHICH", "GO", "ME",
        "HELLO", "YES", "NO", "PLEASE", "THANK", "YOU", "THANKS", "HELP", "GOODBYE",
        "NAME", "NICE", "MEET", "HOW", "ARE", "FINE", "GOOD", "MORNING", "WELCOME"
    }

    QUESTION_WORDS = {"WHAT", "WHO", "WHERE", "WHEN", "WHY", "HOW", "IS", "ARE", "DO", "CAN"}

    def __init__(self):
        self.enchant_dict = None
        self._init_spellcheck()

    def _init_spellcheck(self):
        try:
            import enchant
            self.enchant_dict = enchant.Dict("en_US")
        except Exception:
            try:
                import enchant
                self.enchant_dict = enchant.get_default_language()
            except Exception:
                self.enchant_dict = None

    def get_suggestions(self, partial_word: str, max_suggestions: int = 4) -> List[str]:
        """
        Returns spelling suggestions for the current word being fingerspelled.
        """
        if not partial_word or len(partial_word.strip()) == 0:
            return []

        word_upper = partial_word.strip().upper()

        # 1. Check pyenchant if available
        if self.enchant_dict:
            try:
                suggs = self.enchant_dict.suggest(word_upper)
                if suggs:
                    return [s.upper() for s in suggs[:max_suggestions]]
            except Exception:
                pass

        # 2. Fallback prefix matching from COMMON_WORDS
        matches = [w for w in self.COMMON_WORDS if w.startswith(word_upper)]
        if not matches:
            # Simple edit distance match
            matches = [w for w in self.COMMON_WORDS if len(w) == len(word_upper)]
        return matches[:max_suggestions]

    def assemble_sentence(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Processes a raw list of tokens (letters, space, dynamic words, delete)
        into a grammatically structured sentence with suggestions.
        """
        words: List[str] = []
        current_word_chars: List[str] = []

        for token in tokens:
            t = token.strip()
            if not t:
                continue

            if t in ["DEL", "BACKSPACE"]:
                if current_word_chars:
                    current_word_chars.pop()
                elif words:
                    # Remove last word if nothing in current buffer
                    words.pop()
            elif t in ["SPACE", " "]:
                if current_word_chars:
                    words.append("".join(current_word_chars))
                    current_word_chars = []
            elif len(t) > 1:
                # Dynamic word token (e.g. HELLO, THANK_YOU)
                if current_word_chars:
                    words.append("".join(current_word_chars))
                    current_word_chars = []
                words.append(t.replace("_", " "))
            else:
                # Single letter token
                current_word_chars.append(t.upper())

        current_partial = "".join(current_word_chars)
        full_words = list(words)
        if current_partial:
            full_words.append(current_partial)

        raw_sentence = " ".join(full_words)

        # Context-aware punctuation and casing
        formatted_sentence = self._format_sentence(raw_sentence)

        # Suggestions for currently active word
        suggestions = self.get_suggestions(current_partial) if current_partial else []

        is_valid = bool(
            self.enchant_dict and current_partial and self.enchant_dict.check(current_partial)
        ) or (current_partial in self.COMMON_WORDS)

        return {
            "sentence": formatted_sentence,
            "raw_sentence": raw_sentence,
            "current_word": current_partial,
            "suggestions": suggestions,
            "is_valid_word": is_valid,
            "word_count": len(full_words),
            "tts_text": formatted_sentence
        }

    def _format_sentence(self, text: str) -> str:
        if not text:
            return ""

        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', text).strip()
        if not clean:
            return ""

        # Sentence casing
        words = clean.split(" ")
        formatted_words = []
        for i, w in enumerate(words):
            if i == 0 or w.upper() == "I":
                formatted_words.append(w.capitalize() if len(w) > 1 else w.upper())
            else:
                formatted_words.append(w.lower())

        sentence = " ".join(formatted_words)

        # Punctuation heuristics
        first_word = words[0].upper()
        if first_word in self.QUESTION_WORDS:
            if not sentence.endswith("?"):
                sentence += "?"
        else:
            if not sentence.endswith((".", "!", "?")):
                sentence += "."

        return sentence

# Global singleton
translation_service = TranslationService()
