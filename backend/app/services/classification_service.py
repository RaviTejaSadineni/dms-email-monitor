from __future__ import annotations

import re
from dataclasses import dataclass


CATEGORY_KEYWORDS = [
    ('Negotiation/Redline', ['redline', 'markup', 'indemnity', 'liability']),
    ('Legal Review', ['legal review', 'legal team', 'counsel review']),
    ('Finance Review', ['pricing approval', 'finance review', 'budget']),
    ('Procurement', ['procurement', 'vendor onboarding', 'purchase order']),
    ('Compliance', ['compliance', 'security review', 'data privacy']),
    ('Sign-off', ['approved', 'sign-off', 'signature', 'executed']),
    ('Contract Request', ['contract request', 'please review', 'new agreement', 'nda request']),
    ('General Correspondence', ['follow up', 'update', 'check in']),
]

PRIORITY_KEYWORDS = {
    'P1': ['urgent', 'asap', 'critical', 'immediately'],
    'P2': ['high priority', 'today', 'tomorrow'],
    'P3': ['review', 'follow up', 'thanks'],
}

SPAM_MARKERS = ['unsubscribe', 'lottery', 'free trial', 'marketing']
CONTRACT_RE = re.compile(r'(?:NDA|MSA|SOW|PO|AGR|CONTRACT)[-_/ ]?\d{2,}', re.IGNORECASE)
MONEY_RE = re.compile(r'\$\s?([\d,]+(?:\.\d+)?)')
CLAUSE_REASONS = ['liability', 'indemnity', 'payment terms', 'security', 'data privacy']


@dataclass(slots=True)
class ClassificationResult:
    category: str
    priority: str
    confidence: float
    sentiment: str
    is_spam: bool
    summary: str
    contract_numbers: list[str]
    parties: list[str]
    delay_reason: str


def _contains_any(source: str, values: list[str]) -> bool:
    return any(token in source for token in values)


def classify_email(subject: str | None, body: str | None, sender: str | None = None) -> ClassificationResult:
    content = f"{subject or ''} {body or ''}".lower()
    is_spam = _contains_any(content, SPAM_MARKERS)
    category = 'Spam/Irrelevant' if is_spam else 'General Correspondence'
    confidence = 0.45
    for name, keywords in CATEGORY_KEYWORDS:
        if _contains_any(content, keywords):
            category = name
            confidence = 0.72
            break
    priority = 'Spam' if is_spam else 'P4'
    for level, keywords in PRIORITY_KEYWORDS.items():
        if _contains_any(content, keywords):
            priority = level
            break
    if 'delay' in content or 'blocked' in content:
        priority = 'P2' if priority == 'P4' else priority
    sentiment = 'neutral'
    if any(word in content for word in ['frustrated', 'blocked', 'delay', 'urgent']):
        sentiment = 'urgent'
    elif any(word in content for word in ['thanks', 'great', 'appreciate']):
        sentiment = 'positive'
    contract_numbers = sorted(set(match.upper().replace(' ', '-') for match in CONTRACT_RE.findall(content)))
    parties = [item for item in [sender] if item]
    delay_reason = 'Pending stakeholder response'
    if 'missing' in content or 'awaiting' in content:
        delay_reason = 'Missing documentation or pending approval'
    elif 'customer' in content and 'inactive' in content:
        delay_reason = 'Customer inactivity'
    elif any(clause in content for clause in CLAUSE_REASONS):
        delay_reason = 'Negotiation loop caused by clause redlines'
    summary = f"{category} email with {priority} priority and {sentiment} tone."
    return ClassificationResult(
        category=category,
        priority=priority,
        confidence=confidence,
        sentiment=sentiment,
        is_spam=is_spam,
        summary=summary,
        contract_numbers=contract_numbers,
        parties=parties,
        delay_reason=delay_reason,
    )


def detect_contract_type(content: str) -> str | None:
    lowered = content.lower()
    for contract_type in ['NDA', 'MSA', 'SOW', 'Amendment', 'Procurement Terms']:
        if contract_type.lower() in lowered:
            return contract_type
    return None


def extract_amount(content: str) -> tuple[float | None, str | None]:
    match = MONEY_RE.search(content)
    if not match:
        return None, None
    return float(match.group(1).replace(',', '')), 'USD'
