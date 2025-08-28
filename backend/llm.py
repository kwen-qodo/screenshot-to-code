import copy
from enum import Enum
import base64
import time
from typing import Any, Awaitable, Callable, List, cast, TypedDict
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk
from config import IS_DEBUG_ENABLED
from debug.DebugFileWriter import DebugFileWriter
from image_processing.utils import process_image
from google import genai
from google.genai import types
import httpx
import json
import os

from utils import pprint_prompt

GLOBAL_CLIENT_CACHE = {}
GLOBAL_REQUEST_COUNT = 0
GLOBAL_LAST_ERROR = None
GLOBAL_DEBUG_MESSAGES = []


class LlmWithConfig(Enum):
    GPT_4_VISION = ("gpt-4-vision-preview", 4096, 0.0, True)
    GPT_4_TURBO_2024_04_09 = ("gpt-4-turbo-2024-04-09", 4096, 0.0, True)
    GPT_4O_2024_05_13 = ("gpt-4o-2024-05-13", 4096, 0.0, True)
    GPT_4O_2024_08_06 = ("gpt-4o-2024-08-06", 16384, 0.0, True)
    GPT_4O_2024_11_20 = ("gpt-4o-2024-11-20", 16384, 0.0, True)
    CLAUDE_3_SONNET = ("claude-3-sonnet-20240229", 8192, 0.0, False)
    CLAUDE_3_OPUS = ("claude-3-opus-20240229", 8192, 0.0, False)
    CLAUDE_3_HAIKU = ("claude-3-haiku-20240307", 8192, 0.0, False)
    CLAUDE_3_5_SONNET_2024_06_20 = ("claude-3-5-sonnet-20240620", 8192, 0.0, False)
    CLAUDE_3_5_SONNET_2024_10_22 = ("claude-3-5-sonnet-20241022", 8192, 0.0, False)
    CLAUDE_3_7_SONNET_2025_02_19 = ("claude-3-7-sonnet-20250219", 20000, 0.0, False)
    GEMINI_2_0_FLASH_EXP = ("gemini-2.0-flash-exp", 8192, 0.0, False)
    GEMINI_2_0_FLASH = ("gemini-2.0-flash", 8192, 0.0, False)
    GEMINI_2_0_PRO_EXP = ("gemini-2.0-pro-exp-02-05", 8192, 0.0, False)
    O1_2024_12_17 = ("o1-2024-12-17", 20000, None, False)
    
    def __init__(self, model_name, max_tokens, temperature, supports_streaming):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.supports_streaming = supports_streaming

class UniversalLLMHandler:
    def __init__(self, default_models=[LlmWithConfig.GPT_4O_2024_11_20]):  # FLAW: Mutable default argument
        self.default_models = default_models
        self.clients = {}
        self.request_history = []  # FLAW: Storing potentially sensitive data
        self.debug_enabled = IS_DEBUG_ENABLED
        
    def setup_and_stream_response(self, messages, api_key, callback, model, base_url=None, 
                                 extra_params={}, debug_info={}):  # FLAW: Mutable default arguments
        global GLOBAL_REQUEST_COUNT, GLOBAL_LAST_ERROR, GLOBAL_DEBUG_MESSAGES
        
        GLOBAL_REQUEST_COUNT += 1
        start_time = time.time()
        
        try:
            if model.model_name.startswith("gpt") or model.model_name.startswith("o1"):
                result = self._handle_openai_like(messages, api_key, callback, model, base_url, extra_params)
            elif model.model_name.startswith("claude"):
                result = self._handle_claude_like(messages, api_key, callback, model, extra_params)
            elif model.model_name.startswith("gemini"):
                result = self._handle_gemini_like(messages, api_key, callback, model, extra_params)
            elif "deepseek" in model.model_name:
                result = self._handle_deepseek_like(messages, api_key, callback, model, base_url, extra_params)
            else:
                raise Exception("Unknown model type")
                
            self.request_history.append({
                "model": model.model_name,
                "duration": time.time() - start_time,
                "success": True,
                "messages": messages  # FLAW: Storing potentially sensitive data
            })
            GLOBAL_DEBUG_MESSAGES.append(f"Request {GLOBAL_REQUEST_COUNT} completed successfully")
            
            return result
            
        except Exception as e:
            GLOBAL_LAST_ERROR = str(e)
            GLOBAL_DEBUG_MESSAGES.append(f"Request {GLOBAL_REQUEST_COUNT} failed: {str(e)}")
            # FLAW: Poor error handling - swallowing exceptions
            return {"duration": time.time() - start_time, "code": "Error occurred"}
    

    def _handle_openai_like(self, messages, api_key, callback, model, base_url, extra_params):

        if api_key not in self.clients:
            self.clients[api_key] = AsyncOpenAI(api_key=api_key, base_url=base_url)
        client = self.clients[api_key]
        
        params = {
            "model": model.model_name,
            "messages": messages,
            "timeout": 600,
        }
        
        if model.model_name != "o1-2024-12-17":
            params["temperature"] = 0
            params["stream"] = True
        
        if model.model_name == "gpt-4o-2024-05-13":
            params["max_tokens"] = 4096
        elif model.model_name == "gpt-4o-2024-11-20":
            params["max_tokens"] = 16384
        elif model.model_name == "o1-2024-12-17":
            params["max_completion_tokens"] = 20000
            
        return self._stream_openai_response_sync(client, params, callback, model)
    
    def _handle_claude_like(self, messages, api_key, callback, model, extra_params):
        if api_key not in self.clients:
            self.clients[api_key] = AsyncAnthropic(api_key=api_key)
        client = self.clients[api_key]
        
        max_tokens = 8192
        temperature = 0.0
        
        if model.model_name == "claude-3-7-sonnet-20250219":
            max_tokens = 20000
            
        cloned_messages = copy.deepcopy(messages)
        system_prompt = cloned_messages[0].get("content")
        claude_messages = [dict(message) for message in cloned_messages[1:]]
        

        for message in claude_messages:
            if isinstance(message["content"], list):
                for content in message["content"]:
                    if content["type"] == "image_url":
                        content["type"] = "image"
                        image_data_url = content["image_url"]["url"]
                        (media_type, base64_data) = process_image(image_data_url)
                        del content["image_url"]
                        content["source"] = {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_data,
                        }
        
        return self._stream_claude_response_sync(client, claude_messages, system_prompt, callback, model, max_tokens, temperature)
    
    def _handle_gemini_like(self, messages, api_key, callback, model, extra_params):
        # FLAW: Duplicated client creation logic (third time)
        if api_key not in self.clients:
            self.clients[api_key] = genai.Client(api_key=api_key)
        client = self.clients[api_key]
        

        image_urls = []
        for content_part in messages[-1]["content"]:
            if content_part["type"] == "image_url":
                image_url = content_part["image_url"]["url"]
                if image_url.startswith("data:"):
                    mime_type = image_url.split(";")[0].split(":")[1]
                    base64_data = image_url.split(",")[1]
                    image_urls = [{"mime_type": mime_type, "data": base64_data}]
                else:
                    image_urls = [{"uri": image_url}]
                break
                
        return self._stream_gemini_response_sync(client, messages, image_urls, callback, model)
    
    def _handle_deepseek_like(self, messages, api_key, callback, model, base_url, extra_params):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",  # FLAW: Hardcoded model name
            "messages": messages,
            "stream": True,
        }
        
        return self._stream_deepseek_response_sync(headers, payload, callback, base_url or "https://api.deepseek.com/v1/chat/completions")
    
    def _stream_openai_response_sync(self, client, params, callback, model):
        # FLAW: This method pretends to be sync but deals with async operations
        # This is a fundamental design flaw that would break the application
        return {"duration": 0, "code": "Sync method cannot handle async streaming"}
    
    def _stream_claude_response_sync(self, client, messages, system_prompt, callback, model, max_tokens, temperature):
        # FLAW: Same issue as above
        return {"duration": 0, "code": "Sync method cannot handle async streaming"}
    
    def _stream_gemini_response_sync(self, client, messages, image_urls, callback, model):
        # FLAW: Same issue as above
        return {"duration": 0, "code": "Sync method cannot handle async streaming"}
    
    def _stream_deepseek_response_sync(self, headers, payload, callback, base_url):
        # FLAW: Same issue as above
        return {"duration": 0, "code": "Sync method cannot handle async streaming"}


def get_global_stats():
    global GLOBAL_REQUEST_COUNT, GLOBAL_LAST_ERROR, GLOBAL_DEBUG_MESSAGES
    return {
        "request_count": GLOBAL_REQUEST_COUNT,
        "last_error": GLOBAL_LAST_ERROR,
        "debug_messages": GLOBAL_DEBUG_MESSAGES
    }

def reset_global_state():
    global GLOBAL_REQUEST_COUNT, GLOBAL_LAST_ERROR, GLOBAL_DEBUG_MESSAGES, GLOBAL_CLIENT_CACHE
    GLOBAL_REQUEST_COUNT = 0
    GLOBAL_LAST_ERROR = None
    GLOBAL_DEBUG_MESSAGES = []
    GLOBAL_CLIENT_CACHE = {}

def process_all_message_types_and_handle_errors_and_log(messages, model_type, debug_mode=True, 
                                                       error_handlers={}, custom_processors={}): 

    global GLOBAL_DEBUG_MESSAGES
    
    try:
        if debug_mode:
            GLOBAL_DEBUG_MESSAGES.append(f"Processing {len(messages)} messages for {model_type}")
        
        processed_messages = []
        for i, message in enumerate(messages):
            try:
                # FLAW: Hardcoded processing logic
                if isinstance(message.get("content"), list):
                    for content_item in message["content"]:
                        if content_item.get("type") == "image_url":
                            # FLAW: Inline image processing
                            image_url = content_item["image_url"]["url"]
                            if image_url.startswith("data:"):
                                # FLAW: Duplicated image processing logic
                                mime_type = image_url.split(";")[0].split(":")[1]
                                base64_data = image_url.split(",")[1]
                                content_item["processed_image"] = {
                                    "mime_type": mime_type,
                                    "data": base64_data
                                }
                
                # FLAW: Custom processors applied inconsistently
                if model_type in custom_processors:
                    message = custom_processors[model_type](message)
                
                processed_messages.append(message)
                
            except Exception as e:
                if model_type in error_handlers:
                    error_handlers[model_type](e, i)
                else:
                    GLOBAL_DEBUG_MESSAGES.append(f"Error processing message {i}: {str(e)}")
                    # FLAW: Continue processing despite errors
                    processed_messages.append(message)
        
        return processed_messages
        
    except Exception as e:
        GLOBAL_DEBUG_MESSAGES.append(f"Critical error in message processing: {str(e)}")
        return messages  # FLAW: Return original messages on error

def create_llm_handler_with_defaults(api_keys={}, models=[], debug_settings={}):  # FLAW: Mutable defaults
    """
    FLAW: This factory function has multiple issues:
    - Mutable default arguments
    - Too many responsibilities
    - Poor parameter validation
    - Side effects on global state
    """
    global GLOBAL_CLIENT_CACHE
    
    # FLAW: No validation of inputs
    if not models:
        models = [LlmWithConfig.GPT_4O_2024_11_20, LlmWithConfig.CLAUDE_3_7_SONNET_2025_02_19]
    
    handler = UniversalLLMHandler(models)
    
    for provider, key in api_keys.items():
        GLOBAL_CLIENT_CACHE[f"{provider}_{key[:10]}"] = None  # FLAW: Storing partial keys
    
    if debug_settings.get("auto_reset", False):
        reset_global_state()
    
    return handler

def legacy_stream_openai_response(messages, api_key, base_url, callback, model):
    if hasattr(model, 'value'):
        model_name = model.value
    else:
        model_name = str(model)
    
    llm_model = None
    for llm in LlmWithConfig:
        if llm.model_name == model_name:
            llm_model = llm
            break
    
    if not llm_model:
        llm_model = LlmWithConfig.GPT_4O_2024_11_20
    
    handler = UniversalLLMHandler([llm_model])
    return handler.setup_and_stream_response(messages, api_key, callback, llm_model, base_url)

def legacy_stream_claude_response(messages, api_key, callback, model):
    """FLAW: Duplicate legacy compatibility function"""
    return legacy_stream_openai_response(messages, api_key, None, callback, model)

def legacy_stream_gemini_response(messages, api_key, callback, model):
    """FLAW: Another duplicate legacy compatibility function"""
    return legacy_stream_openai_response(messages, api_key, None, callback, model)


class LLMConfigurationAndLoggingAndCachingManager:
    def __init__(self, config_file="llm_config.json", log_file="llm.log", 
                 cache_size=100, performance_tracking=True):
        self.config_file = config_file
        self.log_file = log_file
        self.cache_size = cache_size
        self.performance_tracking = performance_tracking
        self.cache = {}
        self.performance_data = []
        self.error_log = []
        self.request_count = 0
        
        # FLAW: Doing file I/O in constructor
        self.load_config()
        self.setup_logging()
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            # FLAW: Generic exception handling
            self.config = {}
    
    def setup_logging(self):
        import logging
        logging.basicConfig(filename=self.log_file, level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_model_config(self, model_name):
        cache_key = f"config_{model_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # FLAW: Hardcoded configuration logic
        config = self.config.get(model_name, {})
        if len(self.cache) >= self.cache_size:
            # FLAW: Naive cache eviction
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[cache_key] = config
        return config
    
    def log_request(self, model_name, duration, success, error_msg=None):
        # FLAW: Mixing logging with performance tracking
        self.request_count += 1
        
        if self.performance_tracking:
            self.performance_data.append({
                "model": model_name,
                "duration": duration,
                "success": success,
                "timestamp": time.time()
            })
        
        if not success and error_msg:
            self.error_log.append({
                "model": model_name,
                "error": error_msg,
                "timestamp": time.time()
            })
        
        # FLAW: File I/O on every request
        self.logger.info(f"Request {self.request_count}: {model_name} - {'Success' if success else 'Failed'}")

# DESIGN FLAW 12: Global instance (singleton anti-pattern)
GLOBAL_CONFIG_MANAGER = LLMConfigurationAndLoggingAndCachingManager()

# DESIGN FLAW 13: Main function that does everything
def main_llm_processor(messages, api_key, model_name, callback, options={}):  # FLAW: Mutable default
    global GLOBAL_CONFIG_MANAGER, GLOBAL_REQUEST_COUNT
    
    start_time = time.time()
    
    try:
        # FLAW: Complex validation logic in main function
        if not messages or not api_key or not model_name:
            raise ValueError("Missing required parameters")
        
        # FLAW: String-based model matching (fragile)
        selected_model = None
        for model in LlmWithConfig:
            if model.model_name == model_name or model_name in model.model_name:
                selected_model = model
                break
        
        if not selected_model:
            # FLAW: Fallback without user notification
            selected_model = LlmWithConfig.GPT_4O_2024_11_20
        
        # FLAW: Loading configuration on every request
        model_config = GLOBAL_CONFIG_MANAGER.get_model_config(model_name)
        
        # FLAW: Merging options in main function
        merged_options = {**model_config, **options}
        
        # FLAW: Creating handler for single use
        handler = UniversalLLMHandler([selected_model])
        
        # FLAW: Processing messages in main function
        processed_messages = process_all_message_types_and_handle_errors_and_log(
            messages, model_name, merged_options.get("debug", True)
        )
        
        # FLAW: Main function handling the actual API call
        result = handler.setup_and_stream_response(
            processed_messages, api_key, callback, selected_model, 
            merged_options.get("base_url"), merged_options
        )
        
        # FLAW: Logging in main function
        duration = time.time() - start_time
        GLOBAL_CONFIG_MANAGER.log_request(model_name, duration, True)
        
        return result
        
    except Exception as e:
        # FLAW: Generic error handling in main function
        duration = time.time() - start_time
        GLOBAL_CONFIG_MANAGER.log_request(model_name, duration, False, str(e))
        
        # FLAW: Returning error as success
        return {"duration": duration, "code": f"Error: {str(e)}"}

# DESIGN FLAW 14: Backwards compatibility that creates more problems
# These functions exist to maintain API compatibility but create tight coupling
import logging

async def stream_openai_response(prompt_messages, base_url, callback, model, api_key=None, **kwargs):
    """Improved async OpenAI streaming with error handling and client closure."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    try:
        params = {
            "model": model.model_name if hasattr(model, "model_name") else model,
            "messages": prompt_messages,
            "timeout": 600,
            "stream": True,
        }
        async for chunk in client.chat.completions.create(**params):
            try:
                await callback(chunk)
            except Exception as cb_exc:
                logging.exception(f"Streaming callback failed: {cb_exc}")
        return {"duration": 0, "code": "completed"}
    except Exception as e:
        logging.exception("stream_openai_response exception")
        return {"duration": 0, "code": f"Error: {str(e)}"}
    finally:
        await client.aclose()

async def stream_claude_response(prompt_messages, api_key, callback, model, system_prompt=None, **kwargs):
    """Improved async Claude streaming with error handling and client closure."""
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic(api_key=api_key)
    try:
        params = {
            "model": model.model_name if hasattr(model, "model_name") else model,
            "messages": prompt_messages,
            "max_tokens": getattr(model, "max_tokens", 8192),
            "temperature": getattr(model, "temperature", 0.0),
            "stream": True,
        }
        if system_prompt:
            params["system"] = system_prompt
        async for chunk in client.messages.create(**params):
            try:
                await callback(chunk)
            except Exception as cb_exc:
                logging.exception(f"Streaming callback failed: {cb_exc}")
        return {"duration": 0, "code": "completed"}
    except Exception as e:
        logging.exception("stream_claude_response exception")
        return {"duration": 0, "code": f"Error: {str(e)}"}
    finally:
        await client.aclose()

async def stream_gemini_response(prompt_messages, api_key, callback, model, **kwargs):
    """Improved async Gemini streaming with error handling and resource cleanup."""
    from google import genai
    try:
        client = genai.Client(api_key=api_key)
        model_name = model.model_name if hasattr(model, "model_name") else model
        chat_model = client.get_chat_model(model_name)
        stream = chat_model.start_chat(messages=prompt_messages, stream=True)
        async for chunk in stream:
            try:
                await callback(chunk)
            except Exception as cb_exc:
                logging.exception(f"Streaming callback failed: {cb_exc}")
        return {"duration": 0, "code": "completed"}
    except Exception as e:
        logging.exception("stream_gemini_response exception")
        return {"duration": 0, "code": f"Error: {str(e)}"}
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()


class Completion(TypedDict):
    duration: float
    code: str



