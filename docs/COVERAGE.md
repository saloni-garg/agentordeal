# Coverage

Live numbers come from the tool, not from this file:
`agentordeal coverage` (text) or `agentordeal coverage --format json`
(machine-readable, computed from the scenario data on every run).
This page records the measured state at battery 1.2.0 (regenerated
in iteration 17 of docs/ADOPTION_ITERATIONS.md).

## OWASP Agentic Top 10 (ASI), battery 1.2.0, 91 scenarios

| Code | Name | Scenarios | Status |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | 19 | covered |
| ASI02 | Tool Misuse and Exploitation | 18 | covered |
| ASI03 | Identity and Privilege Abuse | 4 | covered |
| ASI04 | Agentic Supply Chain Vulnerabilities | 8 | covered |
| ASI05 | Unexpected Code Execution | 4 | covered |
| ASI06 | Memory and Context Poisoning | 16 | covered |
| ASI07 | Insecure Inter-Agent Communication | 5 | covered |
| ASI08 | Cascading Failures | 8 | covered |
| ASI09 | Human-Agent Trust Exploitation | 3 | covered |
| ASI10 | Rogue Agents | 6 | covered |

No ASI code is a gap or thin: every code has at least 3 scenarios
(ASI05 went 1 -> 4 in battery 1.2.0).

## MITRE ATLAS

- AML.T0051.000 LLM Prompt Injection: Direct (exact mapping): 32 scenarios
- AML.T0051.001 LLM Prompt Injection: Indirect (exact mapping): 16 scenarios
- AML.T0054 LLM Jailbreak (exact mapping): 32 scenarios
- AML.T0056 LLM Meta Prompt Extraction (exact mapping): 32 scenarios
- AML.T0053 LLM Plugin Compromise (exact mapping): 27 scenarios
- AML.T0048 External Harms (exact mapping): 19 scenarios
- AML.T0057 LLM Data Leakage (exact mapping): 16 scenarios
- AML.T0024 Exfiltration via Cyber Means (exact mapping): 16 scenarios
- AML.T0020 Poison Training Data (analogue mapping): 16 scenarios
- AML.T0010 AI Supply Chain Compromise (analogue mapping): 24 scenarios
