#!/usr/bin/env bash
# One-time installer for the PLAYBOOK §11 design toolchain (skills + MCP).
# Safe to re-run; installs are idempotent. Run from the project root.
set -euo pipefail

# --- Design skills (the skills CLI drops SKILL.md bundles into .claude/skills/) ---
# Emil Kowalski's design-engineering set: emil-design-eng, review-animations,
# improve-animations, find-animation-opportunities, animation-vocabulary, apple-design.
npx -y skills@latest add emilkowalski/skills

# Taste: anti-slop frontend design taste (typography, color, spacing, motion, states).
npx -y skills@latest add https://github.com/Leonxlnx/taste-skill --skill design-taste-frontend

# --- Impeccable (plugin: design language + polish/audit/critique commands) ---
# Plugins install from inside Claude Code, not from this script:
echo ""
echo "Next, inside Claude Code run:  /plugin marketplace add pbakaus/impeccable"
echo "then:                          /impeccable init"

# --- MCP servers ---
# .mcp.json in this repo already declares figma (remote) + playwright, so Claude Code
# prompts to enable them on first open. Manual equivalents if needed:
#   claude mcp add --transport http figma https://mcp.figma.com/mcp
#   claude mcp add playwright -- npx -y @playwright/mcp@latest
# Figma desktop Dev Mode (select-a-frame workflows) instead runs locally:
#   claude mcp add --transport http figma-dev-mode http://127.0.0.1:3845/mcp
