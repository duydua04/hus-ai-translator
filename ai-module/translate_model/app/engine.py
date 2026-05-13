import os
import ctranslate2
from transformers import AutoTokenizer
import nltk
from nltk.tokenize import sent_tokenize
from schema import TranslateRequest

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')


class TranslationEngine:
    def __init__(self):
        print("Initializing Tokenizer and loading CTranslate2 Models...")

        base_path = os.path.dirname(os.path.dirname(__file__))
        model_en_vi_path = os.path.join(base_path, "models/ct2-en-vi")
        model_vi_en_path = os.path.join(base_path, "models/ct2-vi-en")

        # Down Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

        # Down Models
        self.device = "cpu"
        self.model_en_vi = ctranslate2.Translator(model_en_vi_path, device=self.device)
        self.model_vi_en = ctranslate2.Translator(model_vi_en_path, device=self.device)

        print("Downloading model complete!")

    def process_and_translate(self, request: TranslateRequest) -> str:
        if not request.text.strip():
            return request.text

        if request.direction == "en-vi":
            self.tokenizer.src_lang = "en_XX"
            tgt_lang = "vi_VN"
            model = self.model_en_vi
        else:
            self.tokenizer.src_lang = "vi_VN"
            tgt_lang = "en_XX"
            model = self.model_vi_en

        paragraphs = request.text.split('\n')
        final_paragraphs = []

        for para in paragraphs:
            if not para.strip():
                final_paragraphs.append("")
                continue

            sentences = sent_tokenize(para)
            source_tokens = [
                self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(s))
                for s in sentences
            ]
            target_prefix = [[tgt_lang]] * len(sentences)

            results = model.translate_batch(
                source_tokens,
                target_prefix=target_prefix,
                beam_size=4
            )

            translated_sentences = []
            for res in results:
                tokens = res.hypotheses[0]
                if tokens and tokens[0] == tgt_lang:
                    tokens = tokens[1:]
                text = self.tokenizer.convert_tokens_to_string(tokens)
                translated_sentences.append(text)

            final_paragraphs.append(" ".join(translated_sentences))

        return "\n".join(final_paragraphs)


translation_engine = TranslationEngine()