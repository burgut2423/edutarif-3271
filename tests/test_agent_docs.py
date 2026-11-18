"""Portable AI handoff instructions must remain discoverable and self-consistent."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'skills' / 'edutarif-development' / 'references'


def test_agent_handoff_files_exist():
    for name in ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md', '.cursor/rules/edutarif.mdc',
                 '.claude/skills/edutarif-development/SKILL.md', '.github/copilot-instructions.md',
                 '.github/pull_request_template.md', 'docs/AI_HANDOFF.md',
                 'skills/edutarif-development/SKILL.md'):
        assert (ROOT / name).is_file(), name
    for name in ('ARCHITECTURE.md', 'RULES_3271.md', 'RULES_823.md',
                 'WORKFLOWS.md', 'SECURITY.md', 'TEST_PLAN.md',
                 'BACKLOG.md', 'INTEGRATIONS.md'):
        assert (REF / name).is_file(), name


def test_skill_frontmatter_and_handoff_contract():
    content = (ROOT / 'skills/edutarif-development/SKILL.md').read_text(encoding='utf-8')
    assert content.startswith('---\nname: edutarif-development\n')
    assert '\ndescription:' in content.split('---', 2)[1]
    for phrase in ('AGENTS.md', 'docs/AI_HANDOFF.md', '3271', '823',
                   'school_id', 'pytest -q'):
        assert phrase in content
    for phrase in ('P0-01', 'P0-02', 'P0-03'):
        assert phrase in (REF / 'BACKLOG.md').read_text(encoding='utf-8')
