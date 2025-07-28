import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from backend.llm import (
    stream_openai_response,
    stream_claude_response,
    stream_claude_response_native,
    stream_gemini_response,
    Llm,
)

# Helper async callback
def make_callback():
    results = []
    async def callback(chunk):
        results.append(chunk)
    return callback, results

@pytest.mark.asyncio
@patch("backend.llm.AsyncOpenAI")
async def test_stream_openai_response_happy_path(mock_openai):
    # Mock OpenAI streaming
    mock_client = mock_openai.return_value
    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        type("Chunk", (), {"choices": [type("Choice", (), {"delta": type("Delta", (), {"content": "Hello"})()})()]})()
    ]
    mock_client.chat.completions.create.return_value = mock_stream
    callback, results = make_callback()
    messages = [{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "Hi"}]
    out = await stream_openai_response(messages, "fake-key", None, callback, Llm.GPT_4O_2024_05_13)
    assert "duration" in out and "code" in out
    assert results and "Hello" in results[0]

@pytest.mark.asyncio
@patch("backend.llm.AsyncOpenAI")
async def test_stream_openai_response_edge_case_invalid_key(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = Exception("Invalid key")
    callback, _ = make_callback()
    messages = [{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "Hi"}]
    with pytest.raises(Exception):
        await stream_openai_response(messages, "bad-key", None, callback, Llm.GPT_4O_2024_05_13)

@pytest.mark.asyncio
@patch("backend.llm.AsyncAnthropic")
async def test_stream_claude_response_happy_path(mock_anthropic):
    mock_client = mock_anthropic.return_value
    mock_stream = AsyncMock()
    mock_stream.text_stream.__aiter__.return_value = ["Claude response"]
    mock_stream.get_final_message.return_value = type("Resp", (), {"content": [type("C", (), {"text": "Claude final"})()]})()
    mock_client.messages.stream.return_value.__aenter__.return_value = mock_stream
    callback, results = make_callback()
    messages = [{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "Hi"}]
    out = await stream_claude_response(messages, "fake-key", callback, Llm.CLAUDE_3_OPUS)
    assert "duration" in out and "code" in out
    assert results and "Claude response" in results[0]

@pytest.mark.asyncio
@patch("backend.llm.AsyncAnthropic")
async def test_stream_claude_response_edge_case_invalid_key(mock_anthropic):
    mock_client = mock_anthropic.return_value
    mock_client.messages.stream.side_effect = Exception("Invalid key")
    callback, _ = make_callback()
    messages = [{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "Hi"}]
    with pytest.raises(Exception):
        await stream_claude_response(messages, "bad-key", callback, Llm.CLAUDE_3_OPUS)

@pytest.mark.asyncio
@patch("backend.llm.AsyncAnthropic")
@patch("backend.llm.DebugFileWriter")
async def test_stream_claude_response_native_happy_path(mock_debug, mock_anthropic):
    mock_client = mock_anthropic.return_value
    mock_stream = AsyncMock()
    mock_stream.text_stream.__aiter__.return_value = ["Claude native"]
    mock_stream.get_final_message.return_value = type("Resp", (), {"content": [type("C", (), {"text": "Claude native final"})()], "usage": type("U", (), {"input_tokens": 1, "output_tokens": 1})()})()
    mock_client.messages.stream.return_value.__aenter__.return_value = mock_stream
    callback, results = make_callback()
    out = await stream_claude_response_native("prompt", [], "fake-key", callback)
    assert "duration" in out and "code" in out
    assert results and "Claude native" in results[0]

@pytest.mark.asyncio
@patch("backend.llm.AsyncAnthropic")
@patch("backend.llm.DebugFileWriter")
async def test_stream_claude_response_native_edge_case_no_response(mock_debug, mock_anthropic):
    mock_client = mock_anthropic.return_value
    mock_stream = AsyncMock()
    mock_stream.text_stream.__aiter__.return_value = []
    mock_stream.get_final_message.return_value = None
    mock_client.messages.stream.return_value.__aenter__.return_value = mock_stream
    callback, _ = make_callback()
    with pytest.raises(Exception):
        await stream_claude_response_native("prompt", [], "fake-key", callback)

@pytest.mark.asyncio
@patch("backend.llm.genai.Client")
async def test_stream_gemini_response_happy_path(mock_genai):
    mock_client = mock_genai.return_value
    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [type("Resp", (), {"text": "Gemini response"})()]
    mock_client.aio.models.generate_content_stream.return_value = mock_stream
    callback, results = make_callback()
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}}]},
    ]
    out = await stream_gemini_response(messages, "fake-key", callback, Llm.GEMINI_2_0_FLASH_EXP)
    assert "duration" in out and "code" in out
    assert results and "Gemini response" in results[0]

@pytest.mark.asyncio
@patch("backend.llm.genai.Client")
async def test_stream_gemini_response_edge_case_invalid_key(mock_genai):
    mock_client = mock_genai.return_value
    mock_client.aio.models.generate_content_stream.side_effect = Exception("Invalid key")
    callback, _ = make_callback()
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}}]},
    ]
    with pytest.raises(Exception):
        await stream_gemini_response(messages, "bad-key", callback, Llm.GEMINI_2_0_FLASH_EXP)
