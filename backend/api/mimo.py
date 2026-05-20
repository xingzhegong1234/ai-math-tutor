"""MiMo API client — OpenAI-compatible interface for Xiaomi MiMo models."""

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from ..config import MIMO_API_KEY, MIMO_BASE_URL, MIMO_MODEL, MIMO_REASONING_MODEL


class MiMoClient:
    """Wrapper around OpenAI client configured for MiMo API."""

    def __init__(self):
        if not MIMO_API_KEY:
            raise ValueError(
                "MIMO_API_KEY is not set. "
                "Please set it in .env file or as an environment variable."
            )
        self.client = OpenAI(api_key=MIMO_API_KEY, base_url=MIMO_BASE_URL)

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        image_url: str | None = None,
    ) -> list[dict]:
        """Build messages array, optionally including a base64 image."""
        messages = [{"role": "system", "content": system_prompt}]

        if image_url:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_url}"},
                    },
                ],
            })
        else:
            messages.append({"role": "user", "content": user_message})

        return messages

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        image_url: str | None = None,
        model: str | None = None,
        stream: bool = False,
        reasoning: bool = False,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """Send a chat completion request to MiMo API.

        Args:
            system_prompt: System-level instruction.
            user_message: The user's query.
            image_url: Optional base64-encoded image (without data URI prefix).
            model: Model override (defaults to config value).
            stream: Whether to stream the response.
            reasoning: Whether to use the pro/reasoning model.

        Returns:
            ChatCompletion object or Stream of ChatCompletionChunks.
        """
        if reasoning:
            model = model or MIMO_REASONING_MODEL
        else:
            model = model or MIMO_MODEL

        messages = self._build_messages(system_prompt, user_message, image_url)

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            temperature=0.3,
            max_tokens=4096,
        )
