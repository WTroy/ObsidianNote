#!/usr/bin/env python3
"""
AI 自动整理 Inbox 笔记
用法:
  python organize.py           # 交互式整理
  python organize.py --dry-run # 只看建议，不执行
  python organize.py --auto    # 全自动整理
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from vault_llm import load_config, normalize_api_url, C, colored
from vault_llm import find_similar_notes, assess_content_quality, assess_timeliness
from vault_llm import get_embeddings, cosine_similarity
from vault_llm import build_frontmatter_block, call_llm, parse_frontmatter_block
from vault_llm import parse_frontmatter_list, merge_frontmatter_list, strip_related_section
from vault_llm import should_exclude_from_index

VAULT_ROOT = Path(__file__).parent
INBOX_DIR = VAULT_ROOT / "00-Inbox"


_config = load_config()
PROVIDER = _config["llm"].get("provider", "openai")
API_URL = normalize_api_url(_config["llm"]["api_url"], PROVIDER)
API_KEY = _config["llm"]["api_key"]
MODEL = _config["llm"]["model"]

DIRECTORIES = {
    "10-Projects": "进行中的项目，有明确目标和截止日期的事情",
    "20-Areas": "持续关注的领域，没有截止日期但需要长期维护的责任区",
    "30-Resources": "感兴趣的主题、参考资料、学习材料、知识卡片",
    "40-Archives": "已完成或不再活跃的内容",
}

# ── 工具函数 ──────────────────────────────────────────────

def get_existing_notes():
    """获取 vault 中所有已有笔记（排除模板和系统目录）"""
    notes = []
    for md_file in VAULT_ROOT.rglob("*.md"):
        rel = md_file.relative_to(VAULT_ROOT)
        if should_exclude_from_index(rel):
            continue
        if md_file.parent == VAULT_ROOT:
            continue
        content = read_note(md_file)
        if should_exclude_from_index(rel, content):
            continue
        parts = rel.parts
        name = md_file.stem
        notes.append({
            "name": name,
            "path": str(rel),
            "folder": parts[0] if len(parts) > 1 else "",
        })
    return notes


def get_inbox_notes():
    """获取 Inbox 中的笔记"""
    notes = []
    for md_file in INBOX_DIR.glob("*.md"):
        notes.append({
            "name": md_file.stem,
            "path": str(md_file),
        })
    return notes


def read_note(filepath):
    """读取笔记内容"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def parse_frontmatter(content):
    """解析 frontmatter，返回 (frontmatter_dict, body)"""
    return parse_frontmatter_block(content)


def build_frontmatter(fm_dict):
    """生成 frontmatter 文本"""
    return build_frontmatter_block(fm_dict)


def unique_target_path(target_path, source_path):
    """避免移动时覆盖已有同名笔记。"""
    if target_path == source_path or not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def parse_llm_response(text):
    """从 LLM 响应中提取 JSON"""
    # 尝试找 JSON 块
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # 尝试找 { ... }
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def analyze_note(note_content, note_name, existing_notes, inbox_notes, analysis_context=None):
    """让 LLM 分析笔记，返回整理建议

    Args:
        note_content: 笔记内容
        note_name: 笔记名称
        existing_notes: vault 中已有的笔记列表
        inbox_notes: Inbox 中其他待整理的笔记
        analysis_context: 预分析结果（相似笔记、质量评估、时效性）

    Returns:
        dict: 包含 directory, tags, related_notes, summary, action 等字段
    """
    notes_list = "\n".join(
        f"  - {n['name']} ({n.get('folder', n.get('directory', ''))})" for n in existing_notes[:100]
    )

    dir_desc = "\n".join(f"  - {k}: {v}" for k, v in DIRECTORIES.items())

    # 构建分析上下文
    context_parts = []

    if analysis_context:
        # 相似笔记
        if analysis_context.get("similar_notes"):
            similar = ", ".join([f"[[{n}]]" for n, score in analysis_context["similar_notes"]])
            context_parts.append(f"### 相似笔记（可能重复）\n{similar}\n")
            context_parts.append("注意：如果与相似笔记高度相关，考虑合并内容而不是单独存放。\n")

        # 内容质量
        if analysis_context.get("quality"):
            q = analysis_context["quality"]
            context_parts.append(f"### 内容质量评估\n得分: {q['score']}/10")
            if q["strengths"]:
                context_parts.append(f"优点: {', '.join(q['strengths'])}")
            if q["issues"]:
                context_parts.append(f"问题: {', '.join(q['issues'])}")
            if q["score"] < 5:
                context_parts.append("建议：内容质量较低，可能需要补充或改进后再整理。\n")
            context_parts.append("")

        # 时效性
        if analysis_context.get("timeliness"):
            t = analysis_context["timeliness"]
            if t["is_time_sensitive"]:
                context_parts.append(f"### 时效性\n{t['reason']}，建议考虑归档到 40-Archives。\n")

    # Inbox 上下文
    if inbox_notes and len(inbox_notes) > 1:
        inbox_list = "\n".join([f"- {n['name']}" for n in inbox_notes[:20]])
        context_parts.append(f"### Inbox 中其他笔记（可能需要一起整理）\n{inbox_list}\n")

    context_section = "\n".join(context_parts) if context_parts else "（无额外分析上下文）"

    prompt = f"""你是一个笔记整理助手。请分析以下笔记内容，给出整理建议。

## 可选的目标目录
{dir_desc}

## vault 中已有的笔记（用于匹配相关笔记）
{notes_list}

## 待整理的笔记
文件名: {note_name}
内容:
{note_content[:3000]}

## 额外分析上下文
{context_section}

## 要求
请返回一个 JSON 对象，格式如下（不要返回其他内容）：
```json
{{
  "directory": "目标目录名（如 30-Resources）",
  "tags": ["标签1", "标签2"],
  "related_notes": ["相关笔记名1", "相关笔记名2"],
  "summary": "一句话摘要",
  "action": "move|merge|skip|improve",
  "duplicate_of": "如果有高度相似的笔记，填入笔记名；否则为空",
  "merge_suggestion": "如果 action=merge，说明如何合并内容"
}}
```

注意：
- action 字段说明：
  - `move`: 正常移动到目标目录
  - `merge`: 与相似笔记合并，建议同时设置 duplicate_of
  - `skip`: 暂时跳过，不整理
  - `improve`: 内容需要改进，先不移动，添加改进标签
- directory 必须是以下之一：10-Projects, 20-Areas, 30-Resources, 40-Archives
- 如果内容时效性强（包含近期日期/日程），优先考虑 40-Archives
- 如果内容质量低（评分<5），使用 action=improve
- tags 用中文，2-4 个
- related_notes 从已有笔记列表中选择最相关的 0-3 个
- summary 不超过 30 字"""

    response = call_llm(prompt)
    return parse_llm_response(response)


# ── 执行整理 ──────────────────────────────────────────────

def organize_note(filepath, suggestion, dry_run=False):
    """根据建议整理笔记"""
    content = read_note(filepath)
    fm, body = parse_frontmatter(content)
    note_name = filepath.stem

    directory = suggestion.get("directory", "30-Resources")
    tags = suggestion.get("tags", [])
    related = suggestion.get("related_notes", [])
    summary = suggestion.get("summary", "")
    action = suggestion.get("action", "move")
    duplicate_of = suggestion.get("duplicate_of", "")
    merge_suggestion = suggestion.get("merge_suggestion", "")

    # 更新 frontmatter
    if "type" not in fm:
        fm["type"] = "note"

    # 根据 action 调整处理方式
    if action == "merge":
        # 合并模式：不做移动，标记待合并
        fm["status"] = "pending_merge"
        fm["merge_target"] = duplicate_of
        if merge_suggestion:
            fm["merge_note"] = merge_suggestion
        directory = "00-Inbox"  # 留在 Inbox 直到手动合并

    elif action == "skip":
        # 跳过模式：不做任何修改
        return {
            "source": str(filepath.relative_to(VAULT_ROOT)),
            "action": "skip",
            "reason": "LLM 建议跳过",
        }

    elif action == "improve":
        # 改进模式：添加待改进标签
        fm["status"] = "needs_improvement"
        tags = [t for t in tags if "待改进" not in t]
        tags.append("待改进")
        fm["tags"] = merge_frontmatter_list(fm, "tags", tags)
        if "improvement_needed" not in fm:
            fm["improvement_needed"] = True
        directory = "00-Inbox"

    # 正常移动模式
    if action == "move":
        # 添加标签
        if tags:
            fm["tags"] = merge_frontmatter_list(fm, "tags", tags)
        if summary:
            fm["summary"] = summary
        if "created" not in fm:
            fm["created"] = filepath.stem if re.match(r"\d{4}-\d{2}-\d{2}", filepath.stem) else ""

    # 构建新内容
    body = strip_related_section(body)
    new_content = build_frontmatter(fm) + "\n\n" + body

    # 添加相关笔记链接
    if related:
        related = list(dict.fromkeys(related))
        links = [f"[[{name}]]" for name in related]
        new_content += "\n\n---\n## 相关笔记\n" + "\n".join(f"- {link}" for link in links)

    # 移动文件
    target_dir = VAULT_ROOT / directory
    target_path = unique_target_path(target_dir / filepath.name, filepath)

    if dry_run:
        return {
            "source": str(filepath.relative_to(VAULT_ROOT)),
            "target": str(target_path.relative_to(VAULT_ROOT)),
            "tags": tags,
            "related": related,
            "summary": summary,
            "action": action,
            "duplicate_of": duplicate_of,
        }

    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    # 写入新内容到目标位置
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # 删除原文件（如果目标不同）
    if target_path != filepath:
        filepath.unlink()

    return {
        "source": str(filepath.relative_to(VAULT_ROOT)),
        "target": str(target_path.relative_to(VAULT_ROOT)),
        "tags": tags,
        "related": related,
        "summary": summary,
        "action": action,
        "duplicate_of": duplicate_of,
    }


# ── 工具函数 ──────────────────────────────────────────────

def get_vault_notes(directories=None):
    """获取指定目录下的所有笔记"""
    if directories is None:
        directories = ["10-Projects", "20-Areas", "30-Resources"]

    notes = []
    for directory in directories:
        dir_path = VAULT_ROOT / directory
        if not dir_path.exists():
            continue
        for md_file in dir_path.rglob("*.md"):
            rel = md_file.relative_to(VAULT_ROOT)
            if should_exclude_from_index(rel):
                continue
            try:
                content = read_note(md_file)
            except Exception:
                content = ""
            if should_exclude_from_index(rel, content):
                continue
            name = md_file.stem
            notes.append({
                "name": name,
                "path": str(rel),
                "directory": directory,
                "filepath": str(md_file),
            })
    return notes


def analyze_global(dry_run=False, auto_mode=False):
    """全局重新分析主函数

    Args:
        dry_run: 是否预览模式
        auto_mode: 是否自动模式（不询问确认）
    """
    print(colored("\n📊 全局重新分析\n", C.BOLD + C.CYAN))

    # 获取所有笔记
    notes = get_vault_notes()
    print(f"找到 {colored(str(len(notes)), C.YELLOW)} 篇笔记\n")

    # 统计
    total = 0
    low_quality = []
    duplicates = []
    updated = 0

    # 按目录分组显示
    notes_by_dir = {}
    for note in notes:
        dir_name = note["directory"]
        if dir_name not in notes_by_dir:
            notes_by_dir[dir_name] = []
        notes_by_dir[dir_name].append(note)

    for directory, dir_notes in notes_by_dir.items():
        print(colored(f"\n📂 {directory} ({len(dir_notes)} 篇)", C.BOLD))

        # 批量获取嵌入向量（用于相似度检测）
        note_records = []
        for note in dir_notes:
            try:
                content = read_note(note["filepath"])
                note_records.append((note, content))
            except Exception as e:
                print(f"  ⚠️  无法读取 {note['name']}: {e}")
                continue

        if not note_records:
            continue

        # 相似度检测
        print(colored("  🔍 批量分析中...", C.DIM), end="", flush=True)
        try:
            note_contents = [content for _, content in note_records]
            all_embeddings = get_embeddings(note_contents)
        except Exception as e:
            print(colored(f" ❌ 获取嵌入向量失败: {e}", C.RED))
            all_embeddings = None
        print(colored(" ✓", C.GREEN))

        # 逐篇分析
        for i, (note, content) in enumerate(note_records):
            total += 1
            note_name = note["name"]

            # 质量评估
            quality = assess_content_quality(content)
            quality_score = quality["score"]

            # 时效性评估
            timeliness = assess_timeliness(content)

            # 相似度检测（批量）
            if all_embeddings and i < len(all_embeddings):
                similar_to = []
                for j, ((other_note, _), other_emb) in enumerate(zip(note_records, all_embeddings)):
                    if i != j and j < len(all_embeddings):
                        score = cosine_similarity(all_embeddings[i], other_emb)
                        if score >= 0.85:  # 相似度阈值
                            similar_to.append((other_note["name"], round(score, 3)))
            else:
                similar_to = []

            # 记录问题
            if quality_score < 5:
                low_quality.append(note_name)
            if similar_to:
                duplicates.append((note_name, similar_to))

            # 显示结果
            quality_icon = "✓" if quality_score >= 5 else "⚠️"
            quality_color = C.GREEN if quality_score >= 5 else C.RED
            print(f"  📄 {note_name} [质量: {colored(str(quality_score), quality_color)}/10] {quality_icon}")

            if timeliness["is_time_sensitive"]:
                print(f"    ⏰ {timeliness['reason']}")

            if similar_to:
                similar_str = ", ".join([f"[[{n}]] ({s})" for n, s in similar_to])
                print(f"    📎 相似: {colored(similar_str, C.YELLOW)}")

            # 如果不是预览模式，调用 LLM 给出建议
            if not dry_run:
                print(colored("    🤖 AI 分析中...", C.DIM), end="", flush=True)

                # 构建分析上下文
                analysis_context = {
                    "similar_notes": similar_to,
                    "quality": quality,
                    "timeliness": timeliness,
                }

                # 调用 LLM 分析
                suggestion = analyze_note(
                    content, note_name,
                    notes,  # 所有笔记（用于相关笔记匹配）
                    [],     # inbox_notes（全局分析时为空）
                    analysis_context
                )

                if suggestion:
                    print(colored(" ✓", C.GREEN))
                    related = suggestion.get("related_notes", [])
                    action = suggestion.get("action", "improve")

                    # 显示建议
                    if related:
                        related_str = ", ".join([f"[[{n}]]" for n in related[:5]])
                        print(f"    🔗 相关笔记: {colored(related_str, C.CYAN)}")
                    if suggestion.get("summary"):
                        print(f"    📝 摘要: {colored(suggestion.get('summary', ''), C.CYAN)}")

                    # 根据 action 处理
                    if action == "merge" and suggestion.get("duplicate_of"):
                        print(f"    ⚠️  建议合并到: {colored(suggestion.get('duplicate_of', ''), C.RED)}")

                    # 更新笔记
                    if auto_mode:
                        confirm = True
                    else:
                        confirm = input(colored("    确认更新？(y/n): ", C.YELLOW)).strip().lower() in ("y", "yes", "")

                    if confirm:
                        try:
                            # 读取并更新 frontmatter
                            content = read_note(note["filepath"])
                            fm, body = parse_frontmatter(content)

                            # 更新 related 字段
                            if related:
                                fm["related"] = merge_frontmatter_list(fm, "related", related)

                            # 更新 tags
                            if suggestion.get("tags"):
                                fm["tags"] = merge_frontmatter_list(fm, "tags", suggestion.get("tags", []))

                            # 更新 summary
                            if suggestion.get("summary"):
                                fm["summary"] = suggestion.get("summary")

                            # 构建新内容
                            body = strip_related_section(body)
                            new_content = build_frontmatter(fm) + "\n\n" + body

                            # 刷新相关笔记链接正文块
                            if related:
                                related = list(dict.fromkeys(related))
                                links = [f"- [[{name}]]" for name in related]
                                new_content += "\n\n---\n## 相关笔记\n" + "\n".join(links)

                            # 写入文件
                            with open(note["filepath"], "w", encoding="utf-8") as f:
                                f.write(new_content)

                            print(colored("    ✅ 已更新关联关系", C.GREEN))
                            updated += 1
                        except Exception as e:
                            print(colored(f"    ❌ 更新失败: {e}", C.RED))
                else:
                    print(colored(" ❌ LLM 返回格式异常", C.RED))

            # 如果质量低，添加标签
            if not dry_run and quality_score < 5:
                try:
                    content = read_note(note["filepath"])
                    fm, body = parse_frontmatter(content)
                    fm["status"] = "needs_improvement"
                    tags = parse_frontmatter_list(fm, "tags")
                    if "待改进" not in tags:
                        tags.append("待改进")
                        fm["tags"] = tags
                    new_content = build_frontmatter(fm) + "\n\n" + body
                    with open(note["filepath"], "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(colored("    ✅ 已添加待改进标签", C.YELLOW))
                except Exception as e:
                    print(colored(f"    ❌ 无法添加标签: {e}", C.RED))

    # 汇总
    print(colored(f"\n{'═' * 50}", C.DIM))
    print(colored("📊 分析完成\n", C.BOLD))

    print(f"  总计: {total} 篇笔记")
    print(f"  ✅ 已更新: {updated} 篇")
    if low_quality:
        print(f"  ⚠️  低质量: {len(low_quality)} 篇 - {', '.join(low_quality[:5])}{'...' if len(low_quality) > 5 else ''}")
    if duplicates:
        print(f"  📎 重复笔记: {len(duplicates)} 组")
        for name, similar in duplicates[:3]:
            print(f"    - {name}: {', '.join([n for n, _ in similar])}")

    if dry_run:
        print(colored("\n🔍 这是预览模式，去掉 --dry-run 参数执行标记", C.YELLOW))


# ── 主流程 ────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    auto_mode = "--auto" in sys.argv
    global_mode = "--global" in sys.argv

    # 全局分析模式
    if global_mode:
        analyze_global(dry_run=dry_run, auto_mode=auto_mode)
        return

    # Inbox 分析模式
    print(colored("\n📚 Obsidian 笔记自动整理工具\n", C.BOLD + C.CYAN))

    # 扫描 Inbox
    inbox_files = list(INBOX_DIR.glob("*.md"))
    if not inbox_files:
        print(colored("✅ Inbox 是空的，没有需要整理的笔记。", C.GREEN))
        return

    print(f"找到 {colored(str(len(inbox_files)), C.YELLOW)} 篇待整理笔记\n")

    # 获取已有笔记列表
    existing_notes = get_existing_notes()
    inbox_notes = get_inbox_notes()

    results = []
    for filepath in inbox_files:
        note_name = filepath.stem
        print(colored(f"{'─' * 50}", C.DIM))
        print(colored(f"📄 {note_name}", C.BOLD))

        content = read_note(filepath)

        # 预分析
        print(colored("  🔍 正在预分析...", C.DIM), end="", flush=True)
        analysis_context = {
            "similar_notes": find_similar_notes(content, existing_notes, limit=3, threshold=0.75),
            "quality": assess_content_quality(content),
            "timeliness": assess_timeliness(content),
        }
        print(colored(" ✓", C.GREEN))

        # 显示预分析结果
        if analysis_context["similar_notes"]:
            similar_str = ", ".join([f"[[{n}]] ({s})" for n, s in analysis_context["similar_notes"]])
            print(f"  📎 相似笔记: {colored(similar_str, C.YELLOW)}")
        print(f"  📊 质量: {colored(str(analysis_context['quality']['score']), C.CYAN)}/10")

        print(colored("  🤖 正在分析...", C.DIM), end="", flush=True)
        suggestion = analyze_note(content, note_name, existing_notes, inbox_notes, analysis_context)

        if not suggestion:
            print(colored(" ❌ LLM 返回格式异常，跳过", C.RED))
            continue

        print(colored(" ✓", C.GREEN))

        # 展示建议
        action_emoji = {"move": "📂", "merge": "🔗", "skip": "⏭️", "improve": "📝"}.get(suggestion.get("action", "move"), "📂")
        print(f"  {action_emoji} 操作: {colored(suggestion.get('action', 'move'), C.CYAN)}")
        print(f"  📂 目标目录: {colored(suggestion.get('directory', '?'), C.CYAN)}")
        print(f"  🏷️  标签: {colored(', '.join(suggestion.get('tags', [])), C.CYAN)}")
        print(f"  🔗 相关笔记: {colored(', '.join(suggestion.get('related_notes', [])) or '无', C.CYAN)}")
        print(f"  📝 摘要: {colored(suggestion.get('summary', ''), C.CYAN)}")

        if suggestion.get("duplicate_of"):
            print(f"  ⚠️  重复于: {colored(suggestion.get('duplicate_of'), C.RED)}")

        if dry_run:
            results.append({"file": note_name, "suggestion": suggestion, "status": "dry-run"})
            continue

        # 确认
        if auto_mode:
            confirm = "y"
        else:
            confirm = input(colored("  确认整理？(y/n): ", C.YELLOW)).strip().lower()

        if confirm in ("y", "yes", ""):
            result = organize_note(filepath, suggestion, dry_run=False)
            results.append({"file": note_name, "suggestion": suggestion, "status": "done"})

            action = suggestion.get("action", "move")
            if action == "merge":
                print(colored(f"  ✅ 已标记待合并到 {suggestion.get('duplicate_of', '')}", C.YELLOW))
            elif action == "skip":
                print(colored("  ⏭️  已跳过", C.DIM))
            elif action == "improve":
                print(colored(f"  ✅ 已添加待改进标签", C.YELLOW))
            else:
                print(colored(f"  ✅ 已移动到 {result['target']}", C.GREEN))
        else:
            results.append({"file": note_name, "suggestion": suggestion, "status": "skipped"})
            print(colored("  ⏭️  已跳过", C.DIM))

        print()

    # 汇总
    print(colored(f"{'─' * 50}", C.DIM))
    done = sum(1 for r in results if r["status"] == "done")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    dry = sum(1 for r in results if r["status"] == "dry-run")

    if dry_run:
        print(colored(f"🔍 预览完成：{dry} 篇笔记有整理建议", C.CYAN))
        print(colored("   去掉 --dry-run 参数执行整理", C.DIM))
    else:
        print(colored(f"✅ 整理完成：{done} 篇已整理，{skipped} 篇已跳过", C.GREEN))


if __name__ == "__main__":
    main()
