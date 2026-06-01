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
import shutil
import sys
import urllib.request
from pathlib import Path

VAULT_ROOT = Path(__file__).parent
INBOX_DIR = VAULT_ROOT / "00-Inbox"
CONFIG_FILE = VAULT_ROOT / "90-System" / "config.json"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.loads(f.read())


_config = load_config()
PROVIDER = _config["llm"].get("provider", "openai")
API_URL = _config["llm"]["api_url"]
API_KEY = _config["llm"]["api_key"]
MODEL = _config["llm"]["model"]

# 自动补全 API 路径
def _normalize_api_url(url, provider):
    """根据 provider 自动补全完整的 API 路径"""
    url = url.rstrip("/")

    if provider == "anthropic":
        # Anthropic: 需要 /v1/messages
        if not url.endswith("/messages"):
            if url.endswith("/v1"):
                url += "/messages"
            else:
                url += "/v1/messages"
    else:
        # OpenAI: 需要 /v1/chat/completions
        if not url.endswith("/completions"):
            if url.endswith("/v1"):
                url += "/chat/completions"
            elif url.endswith("/chat"):
                url += "/completions"
            else:
                url += "/v1/chat/completions"

    return url

API_URL = _normalize_api_url(API_URL, PROVIDER)

DIRECTORIES = {
    "10-Projects": "进行中的项目，有明确目标和截止日期的事情",
    "20-Areas": "持续关注的领域，没有截止日期但需要长期维护的责任区",
    "30-Resources": "感兴趣的主题、参考资料、学习材料、知识卡片",
    "40-Archives": "已完成或不再活跃的内容",
}

SKIP_DIRS = {"70-Templates", "80-Attachments", "90-System", ".obsidian", "copilot", ".smart-env"}


# ── 终端颜色 ──────────────────────────────────────────────

class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    DIM = "\033[2m"
    END = "\033[0m"


def colored(text, color):
    return f"{color}{text}{C.END}"


# ── 工具函数 ──────────────────────────────────────────────

def get_existing_notes():
    """获取 vault 中所有已有笔记（排除模板和系统目录）"""
    notes = []
    for md_file in VAULT_ROOT.rglob("*.md"):
        rel = md_file.relative_to(VAULT_ROOT)
        parts = rel.parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        if md_file.parent == VAULT_ROOT:
            continue
        name = md_file.stem
        notes.append({
            "name": name,
            "path": str(rel),
            "folder": parts[0] if len(parts) > 1 else "",
        })
    return notes


def read_note(filepath):
    """读取笔记内容"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def parse_frontmatter(content):
    """解析 frontmatter，返回 (frontmatter_dict, body)"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            fm = {}
            for line in fm_text.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    fm[key.strip()] = val.strip()
            return fm, body
    return {}, content


def build_frontmatter(fm_dict):
    """生成 frontmatter 文本"""
    lines = ["---"]
    for k, v in fm_dict.items():
        if isinstance(v, list):
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def call_llm(prompt):
    """调用 LLM API，支持 OpenAI 和 Anthropic 格式"""
    if PROVIDER == "anthropic":
        # Anthropic 格式: /v1/messages
        payload = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1000,
        }).encode("utf-8")

        req = urllib.request.Request(
            API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result["content"][0]["text"]
    else:
        # OpenAI 格式: /v1/chat/completions
        payload = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1000,
        }).encode("utf-8")

        req = urllib.request.Request(
            API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]


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


def analyze_note(note_content, note_name, existing_notes):
    """让 LLM 分析笔记，返回整理建议"""
    notes_list = "\n".join(
        f"  - {n['name']} ({n['folder']})" for n in existing_notes[:100]
    )

    dir_desc = "\n".join(f"  - {k}: {v}" for k, v in DIRECTORIES.items())

    prompt = f"""你是一个笔记整理助手。请分析以下笔记内容，给出整理建议。

## 可选的目标目录
{dir_desc}

## vault 中已有的笔记（用于匹配相关笔记）
{notes_list}

## 待整理的笔记
文件名: {note_name}
内容:
{note_content[:3000]}

## 要求
请返回一个 JSON 对象，格式如下（不要返回其他内容）：
```json
{{
  "directory": "目标目录名（如 30-Resources）",
  "tags": ["标签1", "标签2"],
  "related_notes": ["相关笔记名1", "相关笔记名2"],
  "summary": "一句话摘要"
}}
```

注意：
- directory 必须是以下之一：10-Projects, 20-Areas, 30-Resources, 40-Archives
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

    # 更新 frontmatter
    if "type" not in fm:
        fm["type"] = "note"
    if tags:
        existing_tags = fm.get("tags", "[]")
        if isinstance(existing_tags, str):
            try:
                existing_tags = json.loads(existing_tags)
            except (json.JSONDecodeError, TypeError):
                existing_tags = []
        fm["tags"] = list(set(existing_tags + tags))
    if summary:
        fm["summary"] = summary
    if "created" not in fm:
        fm["created"] = filepath.stem if re.match(r"\d{4}-\d{2}-\d{2}", filepath.stem) else ""

    # 构建新内容
    new_content = build_frontmatter(fm) + "\n\n" + body

    # 添加相关笔记链接
    if related:
        links = [f"[[{name}]]" for name in related]
        new_content += "\n\n---\n## 相关笔记\n" + "\n".join(f"- {link}" for link in links)

    # 移动文件
    target_dir = VAULT_ROOT / directory
    target_path = target_dir / filepath.name

    if dry_run:
        return {
            "source": str(filepath.relative_to(VAULT_ROOT)),
            "target": str(target_path.relative_to(VAULT_ROOT)),
            "tags": tags,
            "related": related,
            "summary": summary,
        }

    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    # 写入新内容到目标位置
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # 删除原文件
    filepath.unlink()

    return {
        "source": str(filepath.relative_to(VAULT_ROOT)),
        "target": str(target_path.relative_to(VAULT_ROOT)),
        "tags": tags,
        "related": related,
        "summary": summary,
    }


# ── 主流程 ────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    auto_mode = "--auto" in sys.argv

    print(colored("\n📚 Obsidian 笔记自动整理工具\n", C.BOLD + C.CYAN))

    # 扫描 Inbox
    inbox_files = list(INBOX_DIR.glob("*.md"))
    if not inbox_files:
        print(colored("✅ Inbox 是空的，没有需要整理的笔记。", C.GREEN))
        return

    print(f"找到 {colored(str(len(inbox_files)), C.YELLOW)} 篇待整理笔记\n")

    # 获取已有笔记列表
    existing_notes = get_existing_notes()

    results = []
    for filepath in inbox_files:
        note_name = filepath.stem
        print(colored(f"{'─' * 50}", C.DIM))
        print(colored(f"📄 {note_name}", C.BOLD))

        content = read_note(filepath)

        print(colored("  🤖 正在分析...", C.DIM), end="", flush=True)
        suggestion = analyze_note(content, note_name, existing_notes)

        if not suggestion:
            print(colored(" ❌ LLM 返回格式异常，跳过", C.RED))
            continue

        print(colored(" ✓", C.GREEN))

        # 展示建议
        print(f"  📂 目标目录: {colored(suggestion.get('directory', '?'), C.CYAN)}")
        print(f"  🏷️  标签: {colored(', '.join(suggestion.get('tags', [])), C.CYAN)}")
        print(f"  🔗 相关笔记: {colored(', '.join(suggestion.get('related_notes', [])) or '无', C.CYAN)}")
        print(f"  📝 摘要: {colored(suggestion.get('summary', ''), C.CYAN)}")

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
