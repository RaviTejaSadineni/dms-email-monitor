from __future__ import annotations

from app.services.classification_service import classify_email


async def test_ai_classification_detects_negotiation_and_priority():
    result = classify_email('Urgent NDA liability redlines', 'Please review indemnity and payment terms ASAP.', 'legal@company.com')
    assert result.category == 'Negotiation/Redline'
    assert result.priority == 'P1'
    assert result.delay_reason == 'Negotiation loop caused by clause redlines'
