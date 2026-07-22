# yt2note

유튜브 링크·LLM 대화 공유링크·로컬 파일에서 내용을 추출해 요약하고, **Obsidian 볼트에 한국어 지식노트로 저장**하는 [Claude Code](https://claude.com/claude-code) 스킬입니다.

핵심 원칙은 *요약 모델의 출력을 그대로 믿지 않는 것* — 저장 전 결정적 코드 검증(접지 검사·중복 확인·70줄 제한)을 통과해야만 노트로 남깁니다.

## 구성

| 파일 | 역할 |
| --- | --- |
| `SKILL.md` | 스킬 본문 — 추출 → 중복확인 → 요약 → 접지검증 → 관련노트 연결 → 저장 절차 |
| `scripts/fetch_captions.py` | 유튜브 URL에서 제목·채널·자막을 추출해 JSON으로 출력 (토큰 0) |

## 설치

Claude Code 스킬 디렉터리에 배치합니다:

```bash
git clone https://github.com/jeonjin2/yt2note.git ~/.claude/skills/yt2note
```

## 의존성

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — 유튜브 자막 추출 (`brew install yt-dlp` 또는 `pip install yt-dlp`)
- Python 3

## 개인화 (필수)

이 스킬은 원 저자의 환경 기준으로 작성돼 있습니다. 사용 전 아래를 **본인 환경에 맞게 수정**하세요.

- **볼트 경로**: `SKILL.md` 상단의 `<VAULT>` 를 본인 Obsidian 볼트 경로로 바꿉니다.
- **섹터(폴더) 목록**: `SKILL.md` 3단계의 섹터 목록(경제·금융, 과학 등)은 예시이므로 본인 볼트의 폴더 구조에 맞게 조정합니다.
- **노트 형식**: 5단계의 frontmatter·섹션 형식이 본인 노트 스타일과 다르면 수정합니다.

## 사용법

Claude Code에서:

```
/yt2note <유튜브·대화 링크 또는 파일 경로 1개 이상>
```

여러 소스를 한 번에 넘기면 병렬로 처리하고, 마지막에 소스별 검증 결과 대조표를 출력합니다.
