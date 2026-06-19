# claude-skills 리팩토링 계획

작성일: 2026-06-11

## 1. 현황 요약 (실측)

| 항목 | CLAUDE.md 주장 | 실측 | 비고 |
|---|---|---|---|
| 스킬 (SKILL.md) | 235 | 도메인 폴더 합계 239 | engineering 60, engineering-team 51, marketing 45, c-level 34, product 17, ra-qm 14, pm 9, business-growth 5, finance 4 |
| `.gemini/` 미러 SKILL.md | — | **301** | 소스(239)와 불일치 |
| Python 도구 | 314 | 368 (*.py 추적 기준) | 샘플/픽스처 포함 차이 가능 |
| agents | 28 | agents/ 하위 md 30 (CLAUDE.md 등 포함) | 근사 일치 |
| commands | 27 | 29 | 드리프트 |

- Python 전 스크립트 `py_compile` 일괄 검사: **실패 0건** (CLAUDE.md v2.1.2의 "237/237 verified" 이후 품질 유지됨)
- 비밀 하드코딩: 미검출 (검출된 AKIA 문자열은 보안 스캐너의 공식 예제 키 `AKIAIOSFODNN7EXAMPLE` — 오탐)

## 2. 발견된 문제점

### High

- **`.gemini/` 미러와 소스의 개수 불일치 (301 vs 239)** — Gemini CLI 지원용 미러가 소스 스킬과 어긋나 있다. 미러가 스테일이면 Gemini 사용자에게 구버전/삭제된 스킬이 배포된다. 동기화 스크립트(또는 생성 시점) 검증이 필요하고, 수작업 이중 유지보수는 지속 불가능한 구조다.
- **stdlib-only 원칙 위반** — `engineering-team/senior-data-engineer/scripts/pipeline_orchestrator.py`가 `import pandas` 사용. CLAUDE.md의 "standard library only" 원칙과 ClawHub 배포 제약(무의존 실행) 위반. (`engineering/tech-debt-tracker/assets/sample_codebase/`의 pandas/requests는 의도된 샘플 픽스처로 예외)

### Medium

- **CLAUDE.md 수치 드리프트** — 스킬 235→239, 커맨드 27→29, Python 도구 314→368 등 문서의 수치가 실측과 어긋남. 수치를 손으로 관리하는 한 계속 어긋난다.
- **frontmatter 누락 SKILL.md 3건** — `.gemini/skills/sample-skill/`, `.gemini/skills/README/`, `engineering/skill-tester/assets/sample-skill/`. 앞의 2건은 미러 산출물 오류 가능성(README가 스킬로 미러됨), 마지막은 의도된 테스트 픽스처로 보임 — 분류 후 처리 필요.
- **engineering vs engineering-team 이원화** — 두 폴더(60+51개)에 유사 주제(보안, 데이터, DevOps)가 분산. "POWERFUL-tier" 구분 기준이 CLAUDE.md에만 있고 각 폴더 README 수준에서 중복 주제 교통정리가 안 되어 있다.

### Low

- `.gemini/skills/README/SKILL.md` — README 문서가 스킬 슬롯을 차지 (미러 생성기의 분류 버그 의심)
- 도메인별 카운트가 CLAUDE.md 본문 여러 곳(개요/구조/버전 하이라이트)에 반복 기재되어 수정 시 누락되기 쉬움

## 3. 단계적 개선 계획

### Phase 1 — 정합성 복구 (즉시)

| 작업 | 내용 | 규모 | 리스크 | 검증 |
|---|---|---|---|---|
| .gemini 미러 재생성 | 미러 생성 절차를 확인해 소스 239개 기준으로 재생성, README 등 비스킬 항목 제외 | M | Gemini 사용자 경로 변경 — 생성 스크립트가 없다면 먼저 작성 | 미러 SKILL.md 수 == 소스 수 |
| pandas 의존 제거 | pipeline_orchestrator.py를 csv/json stdlib 구현으로 교체 (불가하면 SKILL.md에 의존성 명시 + ClawHub 배포 제외) | M | 기능 동등성 | `--help` + 샘플 입력 실행 |
| 수치 자동화 | 스킬/도구/에이전트/커맨드 카운트 스크립트(`scripts/`에 추가)로 CLAUDE.md 수치 일괄 갱신 | S | 없음 | 스크립트 출력 == 문서 수치 |

### Phase 2 — 구조 일관성

| 작업 | 내용 | 규모 | 리스크 | 검증 |
|---|---|---|---|---|
| frontmatter 일괄 검사 CI화 | SKILL.md frontmatter(name+description) 검사 스크립트를 PR 게이트로 (이미 있는 plugin-audit 파이프라인에 편입) | S | 없음 | 검사 스크립트 0건 실패 |
| engineering 이원화 교통정리 | 두 폴더의 주제 매트릭스 작성 → 중복 주제는 상호 링크 + 차별점 명시 (폴더 통합은 ClawHub 슬러그 영향이 커서 비권장) | M | ClawHub 슬러그/경로 참조 | 깨진 링크 검사 |
| 미러 동기화 자동화 | .gemini 재생성을 릴리스 절차(또는 pre-commit)에 포함 | S | 없음 | CI에서 미러-소스 diff 0 |

### Phase 3 — 장기

- 스킬 메타데이터(카운트, 도메인, 버전)를 `.claude-plugin/marketplace.json` 단일 소스로 일원화하고 CLAUDE.md/README/docs는 생성물로 전환
- 435개 레퍼런스 문서의 깨진 링크 정기 검사(MkDocs 빌드에 strict 모드 적용)
- ClawHub 배포본과 리포 버전(v2.3.0) 일치 감사 자동화

## 4. 검증 체크리스트

- [ ] `find . -name SKILL.md -not -path './.git/*' -not -path './.gemini/*' | wc -l` == `.gemini` 미러 수
- [ ] 전 SKILL.md frontmatter 검사 통과 (의도된 픽스처 allowlist 제외)
- [ ] `git ls-files '*.py' | xargs -n50 python3 -m py_compile` 실패 0건
- [ ] `grep -rl "^import pandas" --include='*.py' . ` → 샘플 픽스처 외 0건
- [ ] CLAUDE.md 수치 == 카운트 스크립트 출력
