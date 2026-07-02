> 리뷰 일자: 2026-07-02 · 대상 브랜치: f567c61 시점 스냅샷 · 읽기 전용 정적 분석 (코드 미수정)

# claude-skills 종합 코드리뷰

## 리포 개요

Claude용 스킬 라이브러리. 9개 도메인 디렉토리 아래 SKILL.md 기반 스킬 패키지(문서 + stdlib Python CLI 도구 + 참고자료 + 템플릿)를 배포용으로 관리한다. 실측 규모: SKILL.md 239개(도메인 내 최상위 198 + 중첩 서브스킬 32 + 도메인 번들 9), `scripts/*.py` 도구 324개, references 443개, agents 28개(TEMPLATE.md 포함), commands 29개, marketplace 플러그인 35개, 커밋된 zip 37개, `.gemini/`(302파일)·`.codex/`(198스킬) 미러, MkDocs `docs/`, pytest 스위트 13파일.

**검증 방법**: CLAUDE.md 및 도메인별 CLAUDE.md 정독, 15개 이상 스크립트 정독/부분 정독, AST 기반 전수 import 스캔(368 py), 시크릿/shell=True/eval·exec/pickle 전수 grep, **전체 324개 스크립트 `--help` 실행(323 통과)**, **pytest 전체 실행(1594개 전부 통과)**, plugin.json 35개 스키마 전수 검증, zip 2개 압축 해제 후 소스와 diff.

## 종합 평가: **B (양호하나 문서 정합성·릴리즈 위생이 발목)**

스크립트 자체의 위생은 기대 이상이다 — 실제 시크릿 0건, eval/exec/pickle 0건, LLM API 호출 0건, 324개 중 323개 `--help` 통과, 1594개 테스트 전부 통과. 반면 **리포의 정체성인 "문서 주도(documentation-driven)" 원칙이 숫자 수준에서 무너져 있다**: 헤드라인 카운트(235/314/435/27/30)가 실측(239/324/443/29/35)과 전부 불일치하고, CHANGELOG에 현재 버전(2.3.0) 항목이 없으며, plugin.json 35개 중 18개가 두 릴리즈 전 버전에 머물러 있고, 커밋된 zip 스냅샷은 소스와 확인된 드리프트 상태다.

---

## 발견 사항

### Critical

없음. (하드코딩 시크릿, 위험한 동적 코드 실행, 악성 패턴 미발견)

### High

**H-1. `torch.load()`를 `weights_only=True` 없이 호출 — 신뢰할 수 없는 모델 파일 분석 시 임의 코드 실행**
- `engineering-team/senior-computer-vision/scripts/inference_optimizer.py:152`
  ```python
  checkpoint = torch.load(str(self.model_path), map_location='cpu')
  ```
- torch.load 기본값은 pickle 역직렬화이므로, "모델 최적화 분석"이라는 도구 목적상 외부에서 받은 .pt 파일을 넣는 순간 임의 코드가 실행될 수 있다. 파일 전체에서 `weights_only` grep 결과 0건.
- **권고**: `weights_only=True` 지정, 실패 시 state_dict 전용 로드 안내. 보안 스킬을 6종이나 파는 리포이므로 자기 코드부터 준수 필요.

**H-2. 커밋된 zip 스냅샷 37개가 소스와 드리프트 (샘플 2/2 스테일 확인)**
- `engineering-team/senior-backend.zip` 내 SKILL.md의 name/description/본문이 현재 `engineering-team/senior-backend/SKILL.md`와 상이(구버전 frontmatter vs 전면 재작성된 현재본).
- `marketing-skill/app-store-optimization.zip`도 `diff -q` 결과 STALE.
- `.gitignore`에 "skill packages are intentional"이라고 명시되어 있으나 재생성 자동화가 없어, zip으로 설치하는 사용자는 검증되지 않은 구버전을 받는다.
- **권고**: zip을 리포에서 제거하고 GitHub Release 아티팩트로 이전하거나, CI에서 재생성·정합성 검증. 최소한 `tests/test_skill_integrity.py`에 zip-소스 동기 검사 추가.

**H-3. 헤드라인 수치 전방위 불일치 + CHANGELOG에 현재 버전 항목 부재**
- CLAUDE.md 주장 vs 실측:

  | 항목 | 주장 | 실측 |
  |---|---|---|
  | 스킬 | 235 | 239 (최상위 198 + 중첩 32 + 번들 9 — 어떤 조합으로도 235가 안 나옴) |
  | Python 도구 | 314 | 324 |
  | references | 435 | 443 |
  | commands | 27 | 29 (`commands/*.md`) |
  | marketplace 플러그인 | 30 | 35 (`.claude-plugin/marketplace.json` plugins 배열) |
  | agents | 28 | 28 — 단, `agents/personas/TEMPLATE.md` 포함 카운트 |
- `CHANGELOG.md` 최상단 항목이 `## [2.2.0] - 2026-03-31`인데 CLAUDE.md·marketplace.json은 v2.3.0을 주장 — 2.3.0 릴리즈 노트 부재.
- **권고**: 카운트를 손으로 쓰지 말고 스크립트로 산출해 문서에 주입, CI에서 검증. CHANGELOG 2.3.0 블록 소급 작성.

### Medium

**M-1. plugin.json 버전 파편화 — 자체 "non-negotiable" 규칙 위반**
- CLAUDE.md ClawHub 규칙 #6: "ClawHub package versions must match the repo release version". 실측: 35개 중 **2.1.2가 18개**, 2.2.0이 11개, 2.3.0이 6개.
- 참고: `.codex-plugin/plugin.json`은 허용 필드 외 `interface`, `keywords` 포함 및 `skills: "./.codex/skills/"` (Codex 생태계용이라면 규칙 적용 예외임을 문서화 필요).
- **권고**: 릴리즈 시 전체 plugin.json 버전 범프 스크립트 + 정합성 테스트.

**M-2. `autoresearch-agent`의 파괴적 git 조작 — 미커밋 작업 소실 위험**
- `engineering/autoresearch-agent/scripts/run_experiment.py:197-198, 207, 215, 233`
  ```python
  run_git(["checkout", "--", "."], cwd=str(project_root))
  run_git(["reset", "--hard", "HEAD~1"], cwd=str(project_root))
  ```
- 타임아웃/크래시/미개선 시 사용자 리포에 `reset --hard HEAD~1`을 무조건 실행. 실험 커밋 외의 미커밋 변경이 있으면 **소리 없이 소실**되고, HEAD가 실험 커밋이 아닐 경우 엉뚱한 커밋을 날린다. 같은 파일 `:96`의 `shell=True`는 주석으로 의도를 명시했고 git 호출은 리스트 인자를 써서 인젝션은 없음(양호) — 문제는 파괴성 쪽.
- **권고**: 실행 전 `git status --porcelain` 클린 체크, reset 대상 커밋 해시 검증(직전 기록과 대조), 전용 브랜치 강제.

**M-3. product-team/CLAUDE.md의 RICE CSV 예시가 코드와 불일치 → 조용히 틀린 점수 산출**
- `product-team/CLAUDE.md` CSV 예시는 `impact` 3, `confidence` 0.8, `effort` 5 (숫자). 그러나 `product-team/product-manager-toolkit/scripts/rice_prioritizer.py:17-37,49-51`은 문자열 맵(`massive/high/...`, `high/medium/low`, `xl/l/m/s/xs`)만 인식하고 미매칭 시 **기본값으로 조용히 폴백**(`impact_map.get(impact.lower(), 1.0)`). 문서대로 CSV를 만들면 모든 피처가 impact=1.0, confidence=0.5, effort=5로 계산되어 우선순위 결과가 왜곡된다.
- 추가로 `rice_prioritizer.py:210-215`의 `open()`/`int(row.get('reach', 0))`은 예외 처리가 없어 파일 부재·비숫자 입력 시 raw traceback.
- **권고**: 문서 예시를 코드 스키마로 교정(스크립트 내 `create_sample_csv`가 이미 올바른 예시를 생성함), 미인식 값은 경고 출력.

**M-4. "표준 라이브러리 전용" 주장 위반 — 미문서화 서드파티 의존**
- AST 전수 스캔 결과 스킬 스크립트의 서드파티 모듈 의존 7건:
  - `engineering-team/epic-design/scripts/inspect-assets.py:22-25` — **PIL 하드 필수**(없으면 exit 1, 유일한 `--help` 실패 스크립트). `epic-design/SKILL.md`에 Pillow 미문서화 → "Document all dependencies in SKILL.md" 규칙 위반.
  - `engineering-team/senior-computer-vision/scripts/vision_model_trainer.py:119, 442` — 메서드 내부 `import yaml`이 **try/except 없이** 사용, PyYAML 부재 시 ImportError 크래시. SKILL.md에 pyyaml 미문서화.
  - torch/onnx/numpy(inference_optimizer), yaml(pipeline_orchestrator:18-22, api_scaffolder:91-96, openapi_to_mcp:72, skill_validator:22-27)은 try/except 가드 또는 스텁 폴백이 있어 양호.
- **권고**: 최소한 SKILL.md에 의존성 명기, vision_model_trainer의 yaml import 가드 추가.

**M-5. 원격 fetch 경로의 무방비 `urlopen`**
- `marketing-skill/seo-audit/scripts/seo_checker.py:313`, `marketing-skill/page-cro/scripts/conversion_audit.py:365`
  ```python
  with urllib.request.urlopen(args.url, timeout=10) as resp:
  ```
- try/except 없음 → DNS 실패·4xx/5xx에 raw traceback. scheme 검증 없음 → `--url file:///etc/passwd` 같은 로컬 파일 읽기 허용(로컬 CLI라 심각도는 낮으나 다른 스크립트들의 에러 처리 표준과 불일치).
- **권고**: `URLError/HTTPError` 처리 + `http(s)` scheme 화이트리스트.

**M-6. 도메인 CLAUDE.md 스테일 — 루트·도메인·실측 3중 불일치**
- `finance/CLAUDE.md`: "2/2 finance skills" ↔ 루트 CLAUDE.md "finance (4)" ↔ 실측 3개.
- `business-growth/CLAUDE.md`: "3 skills" ↔ 루트 "5" ↔ 실측 4개(contract-and-proposal-writer 누락).
- `ra-qm-team/CLAUDE.md`: "13" ↔ 루트 "14". `engineering-team/CLAUDE.md`: "36" ↔ 루트 "37". `marketing-skill/CLAUDE.md`: "43" ↔ 루트 "44" ↔ 실측 44.
- **권고**: H-3과 동일한 자동 카운트 파이프라인으로 해결.

**M-7. "No build system or test frameworks — intentional" 문서와 실제 리포의 모순**
- 루트 CLAUDE.md는 테스트 프레임워크 부재를 의도적 설계라 명시하고 Anti-Patterns에 "Adding complex build systems or test frameworks"를 올려놨지만, 실제로는 `tests/`(13파일, 1594 테스트), `pyproject.toml`(pytest 설정), `requirements-dev.txt`(pytest)가 존재하고 **전부 통과**한다. 방향은 옳으나(스킬 소비자에겐 무의존, 리포 유지보수엔 테스트) 문서가 현실을 반영하지 못해 기여자에게 잘못된 신호를 준다.
- **권고**: "배포되는 스킬은 무의존, 리포 자체는 pytest로 통합 검증"으로 문서 재서술.

**M-8. C-level 도구 일부가 자체 품질 표준 미달 — 실데이터 입력 불가**
- `c-level-advisor/cfo-advisor/scripts/burn_rate_calculator.py` — argparse 옵션이 `--csv`, `--scenario`뿐, 입력은 `make_sample_configs()` 하드코딩 샘플만 가능. JSON 입력/출력 없음. finance·business-growth CLAUDE.md가 명시한 "JSON and human-readable output via `--format`" 표준과 상충하며, 실무 활용성이 데모 수준에 그친다.
- **권고**: `input.json` 위치 인자 + `--format json` 추가(동일 도메인 dcf_valuation.py가 좋은 템플릿).

### Low

**L-1. 파일 IO 예외 처리 편차** — 324개 스크립트 중 `FileNotFoundError` 처리 88개, `JSONDecodeError` 처리 92개. 신형 스크립트(sprint_health_scorer.py, campaign_roi_calculator.py — stderr + exit code로 모범적)와 구형(rice_prioritizer 등 raw traceback)의 세대 차가 뚜렷.

**L-2. GDPR 스캐너의 고소음 정규식** — `ra-qm-team/gdpr-dsgvo-expert/scripts/gdpr_compliance_checker.py:57` `"german_id": r"\b[A-Z0-9]{9}\b"`는 9자리 대문자·숫자 토큰(해시 조각, 상수명)을 전부 잡는다. `:33` IP 패턴도 버전 문자열 오탐. 컴플라이언스 보고서 신뢰도 저하 요인.

**L-3. 죽은 import** — `marketing-skill/site-architecture/scripts/sitemap_analyzer.py:20` `import select`가 파일 내에서 미사용.

**L-4. DeprecationWarning** — `engineering-team/ms365-tenant-manager/scripts/powershell_generator.py:113` invalid escape sequence `'\S'` (pytest 실행 시 유일한 경고). raw string 처리 필요.

**L-5. agents 네이밍 일관성 균열** — `agents/CLAUDE.md`가 표방하는 cs-* 규칙과 달리 `agents/personas/` 8개 파일은 `name: DevOps Engineer` 같은 다단어 name을 쓰고 cs- 접두어가 없으며, `agents/personas/TEMPLATE.md`가 "28 agents" 카운트에 포함된다.

**L-6. 동명이인 스크립트의 분기 구현** — `business-growth/sales-engineer/scripts/competitive_matrix_builder.py`(525줄)와 `product-team/competitive-teardown/scripts/competitive_matrix_builder.py`(299줄)는 같은 이름·유사 목적의 서로 다른 구현. 동명 도구의 기능 분기는 사용자 혼란 요인.

**L-7. 콘텐츠 4중 복제 구조** — 소스 도메인 dir + `.gemini/skills`(302 git-tracked 파일) + `.codex/skills`(198) + zip 37개 + 생성된 `docs/`(330). 스팟체크에서 .gemini/.codex는 동기 상태였으나(sync-*-skills.py 존재), zip은 이미 스테일(H-2) — 동기 검증이 자동화되지 않은 사본은 시간문제로 썩는다.

---

## 확인했으나 문제없음 (긍정 사항)

- **시크릿 없음**: py/json/md 전수 스캔에서 걸린 `API_KEY = "sk-..."` 류는 전부 보안 교육 문서·안티패턴 예시(`standards/security/security-standards.md:54` 등). zip 내부에도 .env/pem/credential 파일 없음. `__pycache__`/.pyc는 git 미추적, `.gitignore`가 `.env*`를 배제.
- **eval/exec/pickle 미사용**: 실사용 0건 — 검출된 것은 전부 보안 스캐너의 탐지 패턴과 테스트 픽스처.
- **"No LLM calls" 규칙 준수**: anthropic/openai API 호출 grep 0건. `import requests` 1건은 tech-debt-tracker의 의도된 나쁜 코드 샘플(`assets/sample_codebase/`). 네트워크는 seo/sitemap/load-tester의 사용자 명시 URL fetch뿐.
- **테스트 실재 + 전부 통과**: `python3 -m pytest` → **1594 passed** (14초). `tests/test_skill_integrity.py`가 SKILL.md frontmatter·파일 참조·고아 scripts 디렉토리까지 검증 — 문서-코드 정합성 테스트의 씨앗이 이미 있다.
- **CLI 견고성 실증**: 324개 전 스크립트 `--help` 실행에서 323개 통과(유일한 실패도 PIL 부재 안내 후 정상 exit 1).
- **shell=True는 국소적·문서화됨**: autoresearch-agent 계열에만 존재하고 의도를 주석으로 명시. git 호출은 리스트 인자로 인젝션 안전.
- **plugin.json 스키마 준수**: ClawHub 대상 34개 전부 허용 8필드 정확히 일치, `skills: "./"` 준수 (예외는 Codex용 1개뿐).
- **미러 동기 스팟체크 통과**: `.gemini/skills`·`.codex/skills`의 senior-backend/code-reviewer/tech-debt-tracker SKILL.md가 소스와 바이트 동일.
- **모범 스크립트 다수**: `dcf_valuation.py`(inf 살균 JSON 직렬화, 예외 처리, WACC 수식 정확), `sprint_health_scorer.py`·`campaign_roi_calculator.py`(stderr/exit code 규율), `skill_validator.py`(pyyaml 부재 시 자체 YAML 스텁 폴백).
- **자기 감사 문화**: 루트 `AUDIT_REPORT.md`가 자체 스킬을 POWERFUL/SOLID/GENERIC/WEAK로 냉정하게 등급화.

---

## 관점별 평가표

| 관점 | 점수 | 근거 |
|---|---|---|
| 1. 보안성 | **8/10** | 시크릿·eval·pickle·LLM호출 0건으로 기본기 우수하나, torch.load ACE(H-1)와 urlopen scheme 무검증(M-5)이 감점 |
| 2. 안정성 | **7/10** | 1594 테스트 전부 통과 + 323/324 --help 통과는 실증적 강점; 파일 IO 예외 처리 27% 커버리지와 reset --hard(M-2)가 감점 |
| 3. 효율성 | **7/10** | stdlib 순수 계산 도구라 가볍고 빠름; 콘텐츠 4중 복제(L-7)로 리포 비대·clone 비용 증가 |
| 4. 보수 용이성 | **5/10** | 손으로 관리하는 카운트가 루트/도메인/실측 3중 불일치(H-3, M-6), CHANGELOG 누락, plugin.json 버전 파편화(M-1) — 가장 취약한 축 |
| 5. 확장성 | **7/10** | SKILL.md+scripts+references+assets 패턴이 239개 스킬에 걸쳐 일관 적용, 플러그인 레지스트리·미러 sync 스크립트 존재; 단 신규 스킬 추가 시 5곳(문서 카운트·zip·미러·marketplace·CHANGELOG) 수동 갱신이 병목 |
| 6. 체계성 | **6/10** | "무빌드·무테스트" 트레이드오프는 스킬 소비자 관점에선 타당한 설계이나, 실제로는 pytest가 존재·작동하는데 문서가 부정(M-7) — 설계 의도와 기록의 불일치 |

**종합: 6.7/10 (B)**

## 개선 우선순위 Top 5

1. **카운트·버전의 단일 진실 공급원 구축** (H-3, M-1, M-6): 스킬/도구/커맨드/플러그인 수를 스크립트로 산출해 CLAUDE.md·marketplace.json에 주입하고 `tests/test_skill_integrity.py`에 정합성 assert 추가. CHANGELOG 2.3.0 블록 작성, plugin.json 35개 버전 일괄 동기화.
2. **zip 스냅샷 처리 결정** (H-2): CI 재생성 자동화 또는 리포에서 제거 후 Release 아티팩트화. 현재는 확인된 스테일 배포 경로.
3. **보안 핫픽스 2건** (H-1, M-5): `torch.load(..., weights_only=True)`, seo_checker/conversion_audit의 urlopen 예외 처리 + http(s) scheme 검증.
4. **autoresearch의 git 파괴 방지 가드** (M-2): 더티 워킹트리 감지 시 중단, reset 대상 커밋 검증.
5. **문서-코드 어긋남 교정** (M-3, M-4, M-7): RICE CSV 예시 수정(조용히 틀린 결과를 내는 유일한 발견), epic-design·senior-computer-vision SKILL.md에 의존성 명기, "no test frameworks" 문구를 실제 구조로 재서술.
