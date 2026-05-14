import type { SummaryResponse } from '../api/dashboard';

export const demoSummary: SummaryResponse = {
  metrics: [
    { title: 'Emails Processed', value: 20868, subtitle: 'Historical Gmail Takeout corpus' },
    { title: 'Contracts Tracked', value: 104, subtitle: 'NDAs, MSAs, SOWs, amendments' },
    { title: 'Conversation Threads', value: 518, subtitle: 'Merged legal workflows' },
    { title: 'SLA Breach Rate', value: '20.5%', subtitle: '15-day target' },
    { title: 'Average Cycle Time', value: 19.4, subtitle: 'Days end-to-end' },
    { title: 'Attachments Indexed', value: 3917, subtitle: 'PDF, DOCX, image evidence' },
  ],
  priority_distribution: [
    { label: 'P1', value: 38 },
    { label: 'P2', value: 91 },
    { label: 'P3', value: 162 },
    { label: 'P4', value: 84 },
    { label: 'Spam', value: 26 },
  ],
  category_distribution: [
    { label: 'Contract Request', value: 86 },
    { label: 'Legal Review', value: 73 },
    { label: 'Finance Review', value: 42 },
    { label: 'Procurement', value: 37 },
    { label: 'Negotiation/Redline', value: 58 },
    { label: 'Sign-off', value: 29 },
    { label: 'Spam/Irrelevant', value: 26 },
  ],
  lifecycle_pipeline: [
    { stage: 'Request', count: 104, average_hours: 5.1, breach_rate: 20.5 },
    { stage: 'Legal Review', count: 88, average_hours: 31.2, breach_rate: 20.5 },
    { stage: 'Finance Review', count: 47, average_hours: 26.3, breach_rate: 20.5 },
    { stage: 'Procurement/Compliance', count: 39, average_hours: 105.6, breach_rate: 20.5 },
    { stage: 'Redline Negotiation', count: 32, average_hours: 175.2, breach_rate: 20.5 },
    { stage: 'Leadership Sign-off', count: 19, average_hours: 21.7, breach_rate: 20.5 },
    { stage: 'Repository & Obligation Tracking', count: 14, average_hours: 16.5, breach_rate: 20.5 },
  ],
  email_volume: [
    { label: 'Mon', value: 44 },
    { label: 'Tue', value: 57 },
    { label: 'Wed', value: 61 },
    { label: 'Thu', value: 54 },
    { label: 'Fri', value: 49 },
    { label: 'Sat', value: 21 },
    { label: 'Sun', value: 16 },
  ],
  response_time_distribution: [
    { label: '<4h', value: 94 },
    { label: '4-8h', value: 66 },
    { label: '8-24h', value: 43 },
    { label: '>24h', value: 28 },
  ],
  stakeholder_activity: [
    { label: 'legal@company.com', value: 122 },
    { label: 'sales@company.com', value: 108 },
    { label: 'procurement@company.com', value: 79 },
    { label: 'finance@company.com', value: 67 },
    { label: 'customer@partner.com', value: 59 },
  ],
};

export const demoInsights = [
  {
    title: 'Negotiation loop is the top bottleneck',
    content: 'Liability, indemnity, and payment terms account for the longest redline loops and consume 33% of total cycle time.',
    confidence: 0.86,
  },
  {
    title: 'Procurement review is slowing execution',
    content: 'Procurement and compliance handoffs average 4.4 days. Earlier security questionnaires would reduce queue time.',
    confidence: 0.81,
  },
  {
    title: 'Customer follow-up could cut cycle time by ~20%',
    content: 'Threads with proactive customer nudges in the first 48 hours show materially lower inactivity delays.',
    confidence: 0.78,
  },
];

export const demoEmails = [
  {
    id: 1,
    message_id: '<nda-001@example.com>',
    subject: 'Urgent NDA review for Acme renewal',
    sender: 'legal@company.com',
    recipients_to: ['sales@company.com'],
    recipients_cc: ['procurement@company.com'],
    recipients_bcc: [],
    body_plain: 'Please review NDA-2026 liability redlines and payment terms. Customer is waiting.',
    body_html: null,
    sent_at: '2026-05-12T10:00:00Z',
    received_at: '2026-05-12T10:00:00Z',
    labels: ['Important'],
    priority: 'P1',
    category: 'Negotiation/Redline',
    sentiment: 'urgent',
    ai_summary: 'Urgent legal redline cycle for NDA-2026.',
    is_spam: false,
    size_bytes: 23456,
    has_attachments: true,
    is_forwarded: false,
    is_auto_reply: false,
    language: 'en',
    attachments: [],
  },
  {
    id: 2,
    message_id: '<msa-002@example.com>',
    subject: 'MSA approval ready for finance review',
    sender: 'finance@company.com',
    recipients_to: ['legal@company.com'],
    recipients_cc: [],
    recipients_bcc: [],
    body_plain: 'Finance approval is complete for MSA-2026. Ready for sign-off.',
    body_html: null,
    sent_at: '2026-05-11T13:30:00Z',
    received_at: '2026-05-11T13:30:00Z',
    labels: ['Contracts'],
    priority: 'P2',
    category: 'Finance Review',
    sentiment: 'neutral',
    ai_summary: 'Finance approval completed.',
    is_spam: false,
    size_bytes: 14892,
    has_attachments: false,
    is_forwarded: false,
    is_auto_reply: false,
    language: 'en',
    attachments: [],
  },
];

export const demoContracts = [
  {
    id: 1,
    contract_number: 'NDA-2026',
    contract_type: 'NDA',
    parties: ['Company', 'Acme'],
    status: 'in_progress',
    current_stage: 'Redline Negotiation',
    start_date: '2026-05-01',
    end_date: null,
    renewal_date: null,
    value_amount: 250000,
    value_currency: 'USD',
    risk_score: 78,
    cycle_time_days: 18.2,
    sla_breached: true,
    sla_target_days: 15,
    ai_summary: 'High-value NDA delayed by liability and indemnity redlines.',
    stages: [],
  },
  {
    id: 2,
    contract_number: 'MSA-2026',
    contract_type: 'MSA',
    parties: ['Company', 'Globex'],
    status: 'in_progress',
    current_stage: 'Leadership Sign-off',
    start_date: '2026-05-03',
    end_date: null,
    renewal_date: null,
    value_amount: 540000,
    value_currency: 'USD',
    risk_score: 61,
    cycle_time_days: 11.4,
    sla_breached: false,
    sla_target_days: 15,
    ai_summary: 'Approaching signature after pricing and finance approvals.',
    stages: [],
  },
];

export const demoAttachments = [
  {
    id: 1,
    filename: 'Acme-NDA-Redlines.docx',
    content_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    size_bytes: 81234,
    storage_path: '/uploads/attachments/1/Acme-NDA-Redlines.docx',
    ai_extracted_text: 'Section 7 indemnity updated. Liability cap raised to fees paid.',
    ai_analysis: 'Moderate risk: liability cap and indemnity language need legal approval.',
  },
  {
    id: 2,
    filename: 'Security-Questionnaire.pdf',
    content_type: 'application/pdf',
    size_bytes: 129334,
    storage_path: '/uploads/attachments/2/Security-Questionnaire.pdf',
    ai_extracted_text: 'Questionnaire pending customer completion.',
    ai_analysis: 'Delay risk: procurement cannot proceed until questionnaire is returned.',
  },
];

export const demoFeatures = [
  {
    area: 'Dashboard Views',
    items: [
      'Executive Summary Dashboard with KPIs', 'Contract Lifecycle Pipeline View (7-stage Kanban)', 'Email Volume Timeline', 'Priority Distribution Chart', 'Category Distribution Bar Chart', 'Stakeholder Activity Heatmap', 'Response Time Distribution Chart', 'SLA Compliance Dashboard', 'Bottleneck Analysis View', 'Thread Detail View', 'Attachment Analysis Dashboard', 'Spam vs Legitimate Ratio', 'AI Insights Panel', 'Real-time Import Progress Dashboard', 'Dark Mode / Light Mode Toggle'
    ],
  },
  {
    area: 'Email Analytics',
    items: [
      'Total email count with trend', 'Emails per sender ranking', 'Emails per recipient ranking', 'Average response time per stakeholder', 'Peak email activity hours', 'Email volume by day of week', 'Email chain length distribution', 'Average emails per contract thread', 'Unread or pending action emails', 'Email sentiment distribution over time', 'Top active threads', 'Word cloud source data', 'Subject pattern analysis', 'CC/BCC usage analytics', 'Internal vs external ratio', 'Email size distribution', 'Forwarded email tracking', 'Auto-reply detection', 'Out-of-office pattern detection', 'Email language detection'
    ],
  },
  {
    area: 'Contract Analytics',
    items: [
      'Total contracts tracked', 'Contracts by type', 'Contracts by status/stage', 'Average contract cycle time', 'Cycle time trend', 'SLA breach count and percentage', 'Most negotiated clauses', 'Contract value distribution', 'Counterparty analytics', 'Renewal tracking', 'Amendment frequency', 'Redline round count', 'Time-to-signature metrics', 'AI contract risk score', 'Clause-level risk analysis', 'Side-by-side comparison', 'Template adherence score', 'Obligation tracking', 'Key date alerts', 'Contract aging report'
    ],
  },
  {
    area: 'Priority & Classification',
    items: [
      'Priority-wise distribution', 'Priority trend over time', 'Priority accuracy feedback loop', 'Manual priority override', 'Priority escalation alerts', 'Classification accuracy metrics', 'Re-classification capability', 'Custom classification rules', 'Bulk re-classify action', 'Confidence score display', 'Misclassification reporting', 'Priority SLA mapping', 'Urgent email notifications', 'Priority queue view', 'Classification audit log'
    ],
  },
  {
    area: 'Stakeholder Analytics',
    items: [
      'Stakeholder response time leaderboard', 'Stakeholder involvement per contract', 'Internal team performance metrics', 'External party responsiveness', 'Relationship graph', 'Communication frequency matrix', 'Escalation path visualization', 'Stakeholder workload distribution', 'Team bottleneck analysis', 'Activity timeline', 'RBAC views', 'Sentiment-based stakeholder indicators', 'Cross-team collaboration metrics', 'Handoff delay analysis', 'Contact directory'
    ],
  },
  {
    area: 'Filtering & Search',
    items: [
      'Date range filters', 'Full-text search across emails and attachments', 'Filter by sender or recipient', 'Filter by priority', 'Filter by classification', 'Filter by contract type', 'Filter by contract stage', 'Filter by SLA status', 'Filter by sentiment', 'Filter by attachment type', 'Multi-filter combination', 'Saved filter presets', 'Boolean search', 'Search within threads', 'Export filtered results'
    ],
  },
  {
    area: 'AI & Insights',
    items: [
      'AI executive summary per contract', 'AI delay reason analysis', 'AI suggested next actions', 'AI risk assessment', 'AI anomaly detection', 'Similar contract finder', 'Clause extraction from attachments', 'Contract summarization', 'Stakeholder performance report', 'Trend prediction', 'Email drafting suggestions', 'Compliance check', 'Obligation extraction', 'Duplicate contract detection', 'Natural language query interface'
    ],
  },
  {
    area: 'System & Management',
    items: [
      'User management', 'RBAC', 'Audit log', 'CSV/PDF/Excel export', 'Email notifications', 'Webhook support', 'API rate limiting', 'Health check endpoint', 'System metrics dashboard', 'Backup & restore'
    ],
  },
  {
    area: 'Attachment Features',
    items: [
      'Attachment preview', 'Attachment content search', 'Attachment type distribution', 'Attachment size analytics', 'AI-extracted content display'
    ],
  },
];
