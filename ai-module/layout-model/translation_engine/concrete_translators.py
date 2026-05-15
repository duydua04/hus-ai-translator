"""
Concrete Translator Implementations

Các translator cụ thể:
    - OpenAITranslator: Sử dụng OpenAI GPT API
    - DeepLTranslator: Sử dụng DeepL API
    - OllamaTranslator: Sử dụng Ollama (local LLMs)
    - AzureTranslator: Sử dụng Azure Translator
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

from .base_translator import BaseTranslator


class OpenAITranslator(BaseTranslator):
    """
    Translator sử dụng OpenAI GPT models.
    
    Yêu cầu: OPENAI_API_KEY environment variable
    """
    
    name = "openai"
    lang_map = {
        "english": "en",
        "vietnamese": "vi",
        "chinese": "zh",
        "japanese": "ja",
        "korean": "ko",
    }
    
    def __init__(
        self,
        lang_in: str = "en",
        lang_out: str = "vi",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not found in environment")
        
        super().__init__(lang_in, lang_out, model, api_key=self.api_key, **kwargs)
    
    def translate(self, text: str) -> str:
        """
        Dịch text sử dụng OpenAI GPT.
        
        Args:
            text: Text cần dịch
        
        Returns:
            Text đã dịch
        """
        try:
            import openai
            
            # Chuẩn bị client
            client = openai.OpenAI(api_key=self.api_key)
            
            # Prompt cho dịch thuật chính xác
            system_prompt = (
                f"You are a professional translator. "
                f"Translate the following text from {self.lang_in} to {self.lang_out}. "
                f"Preserve: mathematical formulas, scientific terms, "
                f"proper nouns, formatting. "
                f"Respond with ONLY the translated text, no explanations."
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,  # Giảm randomness
                max_tokens=2000,
            )
            
            translated = response.choices[0].message.content.strip()
            logger.debug(f"✅ OpenAI translation: {len(text)} → {len(translated)} chars")
            
            return translated
        
        except Exception as e:
            logger.error(f"❌ OpenAI translation failed: {e}")
            raise


class DeepLTranslator(BaseTranslator):
    """
    Translator sử dụng DeepL API.
    
    Yêu cầu: DEEPL_API_KEY environment variable
    """
    
    name = "deepl"
    supported_lang_pairs = {
        "vi": ["en", "zh", "ja"],
        "en": ["vi", "zh", "ja"],
    }
    
    def __init__(
        self,
        lang_in: str = "en",
        lang_out: str = "vi",
        model: str = "",
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.api_key = api_key or os.getenv("DEEPL_API_KEY", "")
        
        if not self.api_key:
            logger.warning("⚠️ DEEPL_API_KEY not found in environment")
        
        super().__init__(lang_in, lang_out, model, api_key=self.api_key, **kwargs)
    
    def translate(self, text: str) -> str:
        """
        Dịch text sử dụng DeepL API.
        
        Args:
            text: Text cần dịch
        
        Returns:
            Text đã dịch
        """
        try:
            import deepl
            
            # Khởi tạo translator
            translator = deepl.Translator(self.api_key)
            
            # Map language codes
            lang_in_map = {"en": "EN", "vi": "VI", "zh": "ZH"}
            lang_out_map = {"en": "EN", "vi": "VI", "zh": "ZH"}
            
            lang_in_code = lang_in_map.get(self.lang_in, self.lang_in.upper())
            lang_out_code = lang_out_map.get(self.lang_out, self.lang_out.upper())
            
            result = translator.translate_text(text, source_lang=lang_in_code, target_lang=lang_out_code)
            translated = str(result)
            
            logger.debug(f"✅ DeepL translation: {len(text)} → {len(translated)} chars")
            
            return translated
        
        except Exception as e:
            logger.error(f"❌ DeepL translation failed: {e}")
            raise


class OllamaTranslator(BaseTranslator):
    """
    Translator sử dụng Ollama (local LLMs).
    
    Yêu cầu: Ollama service chạy ở http://localhost:11434
    Có thể override base_url qua environment: OLLAMA_BASE_URL
    """
    
    name = "ollama"
    
    def __init__(
        self,
        lang_in: str = "en",
        lang_out: str = "vi",
        model: str = "llama2",  # Default model
        base_url: Optional[str] = None,
        **kwargs
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        if not model:
            model = "llama2"  # Default
        
        super().__init__(lang_in, lang_out, model, base_url=self.base_url, **kwargs)
    
    def translate(self, text: str) -> str:
        """
        Dịch text sử dụng Ollama.
        
        Args:
            text: Text cần dịch
        
        Returns:
            Text đã dịch
        """
        try:
            import requests
            
            # Prompt
            prompt = (
                f"Translate the following text from {self.lang_in} to {self.lang_out}. "
                f"Respond with ONLY the translated text:\n\n{text}"
            )
            
            # Gọi Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.text}")
            
            result = response.json()
            translated = result.get("response", "").strip()
            
            logger.debug(f"✅ Ollama translation: {len(text)} → {len(translated)} chars")
            
            return translated
        
        except Exception as e:
            logger.error(f"❌ Ollama translation failed: {e}")
            raise


class GoogleTranslator(BaseTranslator):
    """
    Translator sử dụng Google Translate (Free API).
    
    Lợi ích: Không cần API key, free, hỗ trợ 100+ ngôn ngữ
    Yêu cầu: pip install googletrans
    """
    
    name = "google"
    
    def __init__(
        self,
        lang_in: str = "en",
        lang_out: str = "vi",
        model: str = "",
        **kwargs
    ):
        super().__init__(lang_in, lang_out, model, **kwargs)
    
    def translate(self, text: str) -> str:
        """
        Dịch text sử dụng Google Translate (free).
        
        Args:
            text: Text cần dịch
        
        Returns:
            Text đã dịch
        """
        try:
            import asyncio
            from googletrans import Translator
            
            translator = Translator()
            
            # 1 & 2: Bọc asyncio.run() và sửa lại tên tham số src, dest
            result = asyncio.run(
                translator.translate(text, src=self.lang_in, dest=self.lang_out)
            )
            
            # 3: Lấy thuộc tính .text (chứ không phải dictionary ['text'])
            translated = result.text
            
            logger.debug(f"Google translation: {len(text)} -> {len(translated)} chars")
            
            return translated
            
        except Exception as e:
            logger.error(f"Google translation failed: {e}")
            raise

class AzureTranslator(BaseTranslator):
    """
    Translator sử dụng Microsoft Azure Translator service.
    
    Yêu cầu: AZURE_TRANSLATOR_KEY và AZURE_TRANSLATOR_ENDPOINT
    """
    
    name = "azure"
    
    def __init__(
        self,
        lang_in: str = "en",
        lang_out: str = "vi",
        model: str = "",
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs
    ):
        self.api_key = api_key or os.getenv("AZURE_TRANSLATOR_KEY", "")
        self.endpoint = endpoint or os.getenv("AZURE_TRANSLATOR_ENDPOINT", "")
        
        if not self.api_key or not self.endpoint:
            logger.warning(
                "⚠️ AZURE_TRANSLATOR_KEY or AZURE_TRANSLATOR_ENDPOINT not found"
            )
        
        super().__init__(lang_in, lang_out, model, api_key=self.api_key, endpoint=self.endpoint, **kwargs)
    
    def translate(self, text: str) -> str:
        """
        Dịch text sử dụng Azure Translator.
        
        Args:
            text: Text cần dịch
        
        Returns:
            Text đã dịch
        """
        try:
            from azure.ai.translation.text import TextTranslationClient
            from azure.core.credentials import AzureKeyCredential
            
            client = TextTranslationClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.api_key)
            )
            
            result = client.translate(
                content=text,
                from_parameter=self.lang_in,
                to_language=self.lang_out,
            )
            
            translated = result[0].translations[0].text
            
            logger.debug(f"✅ Azure translation: {len(text)} → {len(translated)} chars")
            
            return translated
        
        except Exception as e:
            logger.error(f"❌ Azure translation failed: {e}")
            raise


# Dictionary map service name → class
TRANSLATORS_MAP = {
    "openai": OpenAITranslator,
    "deepl": DeepLTranslator,
    "ollama": OllamaTranslator,    "google": GoogleTranslator,    "azure": AzureTranslator,
}
