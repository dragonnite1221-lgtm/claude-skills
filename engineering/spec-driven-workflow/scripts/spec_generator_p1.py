# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from spec_generator_base import *  # noqa: F403,E402


SPEC_TEMPLATE = """\
# Spec: {name}

**Author:** [your name]
**Date:** {date}
**Status:** Draft
**Reviewers:** [list reviewers]
**Related specs:** [links to related specs, or "None"]

---

## Context

{context_prompt}

---

## Functional Requirements

_Use RFC 2119 keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY._
_Each requirement is a single, testable statement. Number sequentially._

- FR-1: The system MUST [describe required behavior].
- FR-2: The system MUST [describe another required behavior].
- FR-3: The system SHOULD [describe recommended behavior].
- FR-4: The system MAY [describe optional behavior].
- FR-5: The system MUST NOT [describe prohibited behavior].

---

## Non-Functional Requirements

### Performance
- NFR-P1: [Operation] MUST complete in < [threshold] (p95) under [conditions].
- NFR-P2: [Operation] SHOULD handle [throughput] requests per second.

### Security
- NFR-S1: All data in transit MUST be encrypted via TLS 1.2+.
- NFR-S2: The system MUST rate-limit [operation] to [limit] per [period] per [scope].

### Accessibility
- NFR-A1: [UI component] MUST meet WCAG 2.1 AA standards.
- NFR-A2: Error messages MUST be announced to screen readers.

### Scalability
- NFR-SC1: The system SHOULD handle [number] concurrent [entities].

### Reliability
- NFR-R1: The [service] MUST maintain [percentage]% uptime.

---

## Acceptance Criteria

_Write in Given/When/Then (Gherkin) format._
_Each criterion MUST reference at least one FR-* or NFR-*._

### AC-1: [Descriptive name] (FR-1)
Given [precondition]
When [action]
Then [expected result]
And [additional assertion]

### AC-2: [Descriptive name] (FR-2)
Given [precondition]
When [action]
Then [expected result]

### AC-3: [Descriptive name] (NFR-S2)
Given [precondition]
When [action]
Then [expected result]
And [additional assertion]

---

## Edge Cases

_For every external dependency (API, database, file system, user input), specify at least one failure scenario._

- EC-1: [Input/condition] -> [expected behavior].
- EC-2: [Input/condition] -> [expected behavior].
- EC-3: [External service] is unavailable -> [expected behavior].
- EC-4: [Concurrent/race condition] -> [expected behavior].
- EC-5: [Boundary value] -> [expected behavior].

---

## API Contracts

_Define request/response shapes using TypeScript-style notation._
_Cover all endpoints referenced in functional requirements._

### [METHOD] [endpoint]

Request:
```typescript
interface [Name]Request {{
  field: string;       // Description, constraints
  optional?: number;   // Default: [value]
}}
```

Success Response ([status code]):
```typescript
interface [Name]Response {{
  id: string;
  field: string;
  createdAt: string;   // ISO 8601
}}
```

Error Response ([status code]):
```typescript
interface [Name]Error {{
  error: "[ERROR_CODE]";
  message: string;
}}
```

---

## Data Models

_Define all entities referenced in requirements._

### [Entity Name]
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | Primary key, auto-generated |
| [field] | [type] | [constraints] |
| createdAt | timestamp | UTC, immutable |
| updatedAt | timestamp | UTC, auto-updated |

---

## Out of Scope

_Explicit exclusions prevent scope creep. If someone asks for these during implementation, point them here._

- OS-1: [Feature/capability] — [reason for exclusion or link to future spec].
- OS-2: [Feature/capability] — [reason for exclusion].
- OS-3: [Feature/capability] — deferred to [version/sprint].

---

## Open Questions

_Track unresolved questions here. Each must be resolved before status moves to "Approved"._

- [ ] Q1: [Question] — Owner: [name], Due: [date]
- [ ] Q2: [Question] — Owner: [name], Due: [date]
"""
