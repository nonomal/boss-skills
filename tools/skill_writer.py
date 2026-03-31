#!/usr/bin/env python3
"""
Skill file writer for boss.skill.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SKILL_MD_TEMPLATE = """\
---
name: {slug}
description: {name}，{identity}
user-invocable: true
---

# {name}

{identity}

---

## PART A：Boss Judgment

{judgment_content}

---

## PART B：Managing Up

{management_content}

---

## PART C：Persona

{persona_content}

---

## 运行规则

接收到任何项目、方案、汇报、风险或管理问题时：

1. 先由 PART C 判断语气、姿态和管理状态
2. 再由 PART A 评判项目、方案、优先级、风险和执行
3. 再由 PART B 给出向上管理动作和汇报建议
4. 最终用该老板的风格输出

PART C 的 Layer 0 规则永远优先。
"""


def slugify(name: str) -> str:
    try:
        from pypinyin import lazy_pinyin

        parts = lazy_pinyin(name)
        slug = "-".join(parts)
    except ImportError:
        result = []
        for char in name.lower():
            if char.isascii() and (char.isalnum() or char in ("-", "_")):
                result.append(char)
            elif char.isspace():
                result.append("-")
            elif unicodedata.category(char).startswith("L"):
                continue
        slug = "".join(result)

    slug = re.sub(r"[-_]+", "-", slug).strip("-")
    return slug or "boss"


def build_identity_string(meta: dict) -> str:
    profile = meta.get("profile", {})
    parts = []
    for key in ("company", "level", "role"):
        value = profile.get(key, "")
        if value:
            parts.append(value)
    identity = " ".join(parts) if parts else "老板"
    relation = profile.get("relation", "")
    if relation:
        identity += f"，{relation}"
    mbti = profile.get("mbti", "")
    if mbti:
        identity += f"，MBTI {mbti}"
    return identity


def create_skill(
    base_dir: Path,
    slug: str,
    meta: dict,
    judgment_content: str,
    management_content: str,
    persona_content: str,
) -> Path:
    skill_dir = base_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "versions").mkdir(exist_ok=True)
    (skill_dir / "knowledge" / "chats").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "docs").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "emails").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "meetings").mkdir(parents=True, exist_ok=True)

    (skill_dir / "judgment.md").write_text(judgment_content, encoding="utf-8")
    (skill_dir / "management.md").write_text(management_content, encoding="utf-8")
    (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")

    name = meta.get("name", slug)
    identity = build_identity_string(meta)
    skill_md = SKILL_MD_TEMPLATE.format(
        slug=slug,
        name=name,
        identity=identity,
        judgment_content=judgment_content,
        management_content=management_content,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    (skill_dir / "judgment_skill.md").write_text(
        f"---\nname: {slug}-judgment\ndescription: {name} 的项目评判逻辑\nuser-invocable: true\n---\n\n{judgment_content}\n",
        encoding="utf-8",
    )
    (skill_dir / "management_skill.md").write_text(
        f"---\nname: {slug}-management\ndescription: 如何向上管理 {name}\nuser-invocable: true\n---\n\n{management_content}\n",
        encoding="utf-8",
    )
    (skill_dir / "persona_skill.md").write_text(
        f"---\nname: {slug}-persona\ndescription: {name} 的老板 Persona\nuser-invocable: true\n---\n\n{persona_content}\n",
        encoding="utf-8",
    )

    now = datetime.now(timezone.utc).isoformat()
    meta["slug"] = slug
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta.setdefault("corrections_count", 0)
    (skill_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return skill_dir


def update_skill(
    skill_dir: Path,
    judgment_patch: Optional[str] = None,
    management_patch: Optional[str] = None,
    persona_patch: Optional[str] = None,
    correction: Optional[dict] = None,
) -> str:
    meta_path = skill_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    current_version = meta.get("version", "v1")
    try:
        version_num = int(current_version.lstrip("v").split("_")[0]) + 1
    except ValueError:
        version_num = 2
    new_version = f"v{version_num}"

    version_dir = skill_dir / "versions" / current_version
    version_dir.mkdir(parents=True, exist_ok=True)
    for fname in (
        "SKILL.md",
        "judgment.md",
        "management.md",
        "persona.md",
        "judgment_skill.md",
        "management_skill.md",
        "persona_skill.md",
    ):
        src = skill_dir / fname
        if src.exists():
            shutil.copy2(src, version_dir / fname)

    def append_patch(path: Path, patch: Optional[str]) -> None:
        if not patch:
            return
        current = path.read_text(encoding="utf-8")
        path.write_text(current.rstrip() + "\n\n" + patch.strip() + "\n", encoding="utf-8")

    append_patch(skill_dir / "judgment.md", judgment_patch)
    append_patch(skill_dir / "management.md", management_patch)

    if correction:
        current_persona = (skill_dir / "persona.md").read_text(encoding="utf-8")
        correction_line = f"\n- [{correction.get('scene', '通用')}] 不应该 {correction['wrong']}，应该 {correction['correct']}"
        target = "## Correction 记录"
        if target in current_persona:
            insert_pos = current_persona.index(target) + len(target)
            rest = current_persona[insert_pos:]
            placeholder = "\n\n（暂无记录）"
            if rest.startswith(placeholder):
                rest = rest[len(placeholder):]
            new_persona = current_persona[:insert_pos] + correction_line + rest
        else:
            new_persona = current_persona.rstrip() + "\n\n## Correction 记录\n" + correction_line + "\n"
        (skill_dir / "persona.md").write_text(new_persona, encoding="utf-8")
        meta["corrections_count"] = meta.get("corrections_count", 0) + 1
    else:
        append_patch(skill_dir / "persona.md", persona_patch)

    slug = skill_dir.name
    name = meta.get("name", slug)
    identity = build_identity_string(meta)
    judgment_content = (skill_dir / "judgment.md").read_text(encoding="utf-8")
    management_content = (skill_dir / "management.md").read_text(encoding="utf-8")
    persona_content = (skill_dir / "persona.md").read_text(encoding="utf-8")
    skill_md = SKILL_MD_TEMPLATE.format(
        slug=slug,
        name=name,
        identity=identity,
        judgment_content=judgment_content,
        management_content=management_content,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (skill_dir / "judgment_skill.md").write_text(
        f"---\nname: {slug}-judgment\ndescription: {name} 的项目评判逻辑\nuser-invocable: true\n---\n\n{judgment_content}\n",
        encoding="utf-8",
    )
    (skill_dir / "management_skill.md").write_text(
        f"---\nname: {slug}-management\ndescription: 如何向上管理 {name}\nuser-invocable: true\n---\n\n{management_content}\n",
        encoding="utf-8",
    )
    (skill_dir / "persona_skill.md").write_text(
        f"---\nname: {slug}-persona\ndescription: {name} 的老板 Persona\nuser-invocable: true\n---\n\n{persona_content}\n",
        encoding="utf-8",
    )

    meta["version"] = new_version
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return new_version


def list_bosses(base_dir: Path) -> list[dict]:
    bosses: list[dict] = []
    if not base_dir.exists():
        return bosses
    for skill_dir in sorted(base_dir.iterdir()):
        meta_path = skill_dir / "meta.json"
        if not skill_dir.is_dir() or not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        bosses.append(
            {
                "slug": meta.get("slug", skill_dir.name),
                "name": meta.get("name", skill_dir.name),
                "identity": build_identity_string(meta),
                "version": meta.get("version", "v1"),
                "updated_at": meta.get("updated_at", ""),
                "corrections_count": meta.get("corrections_count", 0),
            }
        )
    return bosses


def read_optional(path_str: Optional[str]) -> Optional[str]:
    if not path_str:
        return None
    return Path(path_str).read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="boss.skill file writer")
    parser.add_argument("--action", required=True, choices=["create", "update", "list"])
    parser.add_argument("--slug")
    parser.add_argument("--name")
    parser.add_argument("--meta")
    parser.add_argument("--judgment")
    parser.add_argument("--management")
    parser.add_argument("--persona")
    parser.add_argument("--judgment-patch")
    parser.add_argument("--management-patch")
    parser.add_argument("--persona-patch")
    parser.add_argument("--base-dir", default="./bosses")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).expanduser()

    if args.action == "list":
        bosses = list_bosses(base_dir)
        if not bosses:
            print("暂无已创建的老板 Skill")
        else:
            print(f"已创建 {len(bosses)} 个老板 Skill：\n")
            for item in bosses:
                updated = item["updated_at"][:10] if item["updated_at"] else "未知"
                print(f"  [{item['slug']}]  {item['name']} — {item['identity']}")
                print(f"    版本: {item['version']}  纠正次数: {item['corrections_count']}  更新: {updated}")
                print()
        return

    if args.action == "create":
        if not args.slug and not args.name:
            print("错误：create 操作需要 --slug 或 --name", file=sys.stderr)
            sys.exit(1)
        meta = json.loads(Path(args.meta).read_text(encoding="utf-8")) if args.meta else {}
        if args.name:
            meta["name"] = args.name
        slug = args.slug or slugify(meta.get("name", "boss"))
        skill_dir = create_skill(
            base_dir,
            slug,
            meta,
            read_optional(args.judgment) or "",
            read_optional(args.management) or "",
            read_optional(args.persona) or "",
        )
        print(f"Skill 已创建：{skill_dir}")
        print(f"   触发词：/{slug}")
        return

    if not args.slug:
        print("错误：update 操作需要 --slug", file=sys.stderr)
        sys.exit(1)

    skill_dir = base_dir / args.slug
    if not skill_dir.exists():
        print(f"错误：找不到 Skill 目录 {skill_dir}", file=sys.stderr)
        sys.exit(1)

    new_version = update_skill(
        skill_dir,
        read_optional(args.judgment_patch),
        read_optional(args.management_patch),
        read_optional(args.persona_patch),
    )
    print(f"Skill 已更新到 {new_version}：{skill_dir}")


if __name__ == "__main__":
    main()
