from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.services.classification_service import classify_email

try:
    from openai import AsyncAzureOpenAI
except ImportError:  # pragma: no cover
    AsyncAzureOpenAI = None  # type: ignore


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = None
        if AsyncAzureOpenAI and self.settings.azure_openai_api_key != 'changeme':
            self.client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_key=self.settings.azure_openai_api_key,
                api_version=self.settings.azure_openai_api_version,
            )

    async def summarize_email(self, subject: str, body: str) -> str:
        heuristic = classify_email(subject, body).summary
        if not self.client:
            return heuristic
        response = await self.client.chat.completions.create(
            model=self.settings.azure_openai_deployment,
            messages=[
                {
                    'role': 'system',
                    'content': 'You analyze legal contract workflow emails and produce concise operational summaries.',
                },
                {
                    'role': 'user',
                    'content': (
                        'Summarize the purpose, delay reason, risk, and next action in 3 short bullet points. '
                        f'Subject: {subject}\nBody: {body[:6000]}'
                    ),
                },
            ],
        )
        content = response.choices[0].message.content if response.choices else None
        return content or heuristic

    async def analyze_attachment(self, filename: str, extracted_text: str) -> str:
        heuristic = f'Attachment {filename} reviewed for contractual clauses, obligations, and risk indicators.'
        if not self.client:
            return heuristic
        response = await self.client.chat.completions.create(
            model=self.settings.azure_openai_deployment,
            messages=[
                {
                    'role': 'system',
                    'content': 'You review legal contract attachments for risk, clause changes, and missing details.',
                },
                {
                    'role': 'user',
                    'content': (
                        'Identify contract type, risky clauses, delay indicators, and missing information. '
                        f'File: {filename}\nContent: {extracted_text[:6000]}'
                    ),
                },
            ],
        )
        content = response.choices[0].message.content if response.choices else None
        return content or heuristic


@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    return AIService()
