#!/usr/bin/env python3
"""
有道云笔记导入脚本
将导出的 .note.pdf 文件转换为 Markdown 并导入到 Obsidian vault
支持 AI 分析笔记关联并添加双链

用法:
  python import_youdao.py /path/to/exported/folder              # 导入笔记
  python import_youdao.py /path/to/exported/folder --dry-run    # 预览模式
  python import_youdao.py --link                                # AI 分析关联并添加双链
  python import_youdao.py --link --dry-run                      # 预览关联分析
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from pypdf import PdfReader

VAULT_ROOT = Path(__file__).parent
CONFIG_FILE = VAULT_ROOT / "90-System" / "config.json"

# 有道云笔记目录 -> Obsidian PARA 映射
FOLDER_MAPPING = {
    "工作": "10-Projects",
    "学习": "30-Resources",
    "生活": "20-Areas",
    "来自手机": "00-Inbox",
    "我的资源": "30-Resources",
}

# 跳过的目录（不参与关联分析）
SKIP_DIRS = {"70-Templates", "80-Attachments", "90-System", ".obsidian", "copilot", ".smart-env"}


# ── LLM 配置 ──────────────────────────────────────────────

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.loads(f.read())


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


def call_llm(prompt):
    """调用 LLM API，支持 OpenAI 和 Anthropic 格式"""
    config = load_config()
    llm = config["llm"]
    provider = llm.get("provider", "openai")
    api_url = _normalize_api_url(llm["api_url"], provider)
    api_key = llm["api_key"]
    model = llm["model"]

    if provider == "anthropic":
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2000,
        }).encode("utf-8")

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result["content"][0]["text"]
    else:
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2000,
        }).encode("utf-8")

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]


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


# ── PDF 导入功能 ──────────────────────────────────────────

def extract_text_from_pdf(pdf_path):
    """从 PDF 提取文本"""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"  ⚠️  PDF 读取失败: {e}")
        return None


def clean_filename(name):
    """清理文件名，去掉 .note.pdf 后缀"""
    if name.endswith(".note.pdf"):
        name = name[:-9]
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    return name.strip()


def text_to_markdown(text, title):
    """将纯文本转换为 Markdown 格式"""
    lines = text.split('\n')
    md_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            md_lines.append("")
            continue

        if re.match(r'^[—\-=_]{10,}$', line):
            md_lines.append("---")
            continue

        md_lines.append(line)

    frontmatter = f"""---
title: {title}
source: 有道云笔记
imported: true
---

"""

    return frontmatter + "\n".join(md_lines)


def get_target_folder(youdao_folder, subfolder=None):
    """根据有道云笔记目录确定 Obsidian 目标目录"""
    if youdao_folder in FOLDER_MAPPING:
        return FOLDER_MAPPING[youdao_folder]
    return "30-Resources"


def process_directory(source_dir, dry_run=False):
    """处理整个导出目录"""
    source_path = Path(source_dir)

    if not source_path.exists():
        print(colored(f"❌ 目录不存在: {source_dir}", C.RED))
        return

    print(colored("\n📚 开始导入有道云笔记\n", C.BOLD + C.CYAN))
    print(f"📁 源目录: {source_path}")
    print(f"📁 目标: {VAULT_ROOT}\n")

    total = 0
    success = 0
    skipped = 0
    failed = 0

    for pdf_file in sorted(source_path.rglob("*.note.pdf")):
        total += 1
        rel_path = pdf_file.relative_to(source_path)
        parts = rel_path.parts

        youdao_folder = parts[0] if len(parts) > 1 else ""
        subfolder = parts[1] if len(parts) > 2 else None
        filename = pdf_file.name

        target_dir_name = get_target_folder(youdao_folder, subfolder)
        target_dir = VAULT_ROOT / target_dir_name

        if subfolder and subfolder != filename:
            target_dir = target_dir / clean_filename(subfolder)

        clean_name = clean_filename(filename)
        target_file = target_dir / f"{clean_name}.md"

        print(f"{'─' * 50}")
        print(colored(f"📄 {rel_path}", C.BOLD))
        print(f"   → {target_file.relative_to(VAULT_ROOT)}")

        if dry_run:
            success += 1
            continue

        if target_file.exists():
            print(colored("   ⏭️  已存在，跳过", C.DIM))
            skipped += 1
            continue

        text = extract_text_from_pdf(pdf_file)
        if not text:
            print(colored("   ❌ 提取失败", C.RED))
            failed += 1
            continue

        markdown = text_to_markdown(text, clean_name)
        target_dir.mkdir(parents=True, exist_ok=True)

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(markdown)

        print(colored("   ✅ 已导入", C.GREEN))
        success += 1

    print(colored(f"\n{'═' * 50}", C.DIM))
    print(colored("📊 导入完成:", C.BOLD))
    print(f"   总计: {total} 篇")
    print(colored(f"   成功: {success} 篇", C.GREEN))
    if skipped:
        print(f"   跳过: {skipped} 篇 (已存在)")
    if failed:
        print(colored(f"   失败: {failed} 篇", C.RED))

    if dry_run:
        print(colored("\n🔍 这是预览模式，去掉 --dry-run 参数执行实际导入", C.YELLOW))


# ── 双链关联功能 ──────────────────────────────────────────

def get_all_notes():
    """获取 vault 中所有笔记"""
    notes = []
    for md_file in VAULT_ROOT.rglob("*.md"):
        rel = md_file.relative_to(VAULT_ROOT)
        parts = rel.parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        if md_file.parent == VAULT_ROOT:
            continue
        notes.append({
            "name": md_file.stem,
            "path": str(rel),
            "folder": parts[0] if len(parts) > 1 else "",
        })
    return notes


def read_note_content(filepath, max_length=2000):
    """读取笔记内容（截取前 N 字符）"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # 去掉 frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        return content[:max_length]
    except Exception:
        return ""


def parse_related_notes(response_text):
    """从 LLM 响应中提取关联笔记列表"""
    # 尝试找 JSON 数组
    match = re.search(r'\[.*?\]', response_text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(0))
            if isinstance(result, list):
                return [str(item).strip() for item in result if item]
        except json.JSONDecodeError:
            pass

    # 尝试按行解析
    lines = response_text.strip().split('\n')
    notes = []
    for line in lines:
        line = line.strip().strip('-').strip('*').strip()
        if line and not line.startswith('[') and not line.startswith('{'):
            # 去掉可能的 [[ ]] 包裹
            line = re.sub(r'^\[\[|\]\]$', '', line)
            if line:
                notes.append(line)
    return notes[:5]  # 最多 5 个关联


def add_links_to_note(filepath, related_notes):
    """给笔记添加关联链接"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否已有相关笔记部分
    if "## 相关笔记" in content:
        # 替换已有的相关笔记部分
        content = re.sub(
            r'\n---\n## 相关笔记\n.*$',
            '',
            content,
            flags=re.DOTALL
        )

    # 构建关联笔记链接
    if related_notes:
        links_section = "\n\n---\n## 相关笔记\n"
        for name in related_notes:
            links_section += f"- [[{name}]]\n"
        content += links_section

    # 更新 frontmatter 中的 related 字段
    if related_notes and content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()

            # 添加 related 字段
            related_json = json.dumps(related_notes, ensure_ascii=False)
            fm_text += f"\nrelated: {related_json}"

            content = f"---\n{fm_text}\n---\n\n{body}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def analyze_links(dry_run=False):
    """AI 分析笔记关联并添加双链"""
    import sys
    print(colored("\n🔗 开始分析笔记关联\n", C.BOLD + C.CYAN))
    sys.stdout.flush()

    notes = get_all_notes()
    print(f"📚 找到 {colored(str(len(notes)), C.YELLOW)} 篇笔记\n")
    sys.stdout.flush()

    if len(notes) < 2:
        print(colored("笔记数量不足，无需分析", C.DIM))
        return

    # 构建笔记列表（用于 LLM 参考）
    notes_list = "\n".join(f"- {n['name']} ({n['folder']})" for n in notes)

    success = 0
    failed = 0

    for i, note in enumerate(notes):
        filepath = VAULT_ROOT / note["path"]
        print(f"{'─' * 50}")
        print(colored(f"📄 [{i+1}/{len(notes)}] {note['name']}", C.BOLD))
        sys.stdout.flush()

        # 读取笔记内容
        content = read_note_content(filepath)
        if not content:
            print(colored("   ⏭️  内容为空，跳过", C.DIM))
            sys.stdout.flush()
            continue

        print(colored("   🤖 AI 分析中...", C.DIM), end="", flush=True)
        sys.stdout.flush()

        prompt = f"""你是一个笔记关联分析助手。请分析以下笔记内容，找出与它最相关的其他笔记。

## 所有笔记列表
{notes_list}

## 当前笔记
名称: {note['name']}
路径: {note['path']}
内容摘要:
{content[:1500]}

## 要求
1. 从笔记列表中找出与当前笔记内容最相关的 0-5 篇笔记
2. 考虑技术关联（如 Docker 和 Kubernetes）、主题关联（如都是面试题）、项目关联等
3. 只返回一个 JSON 数组，包含相关笔记的名称，不要返回其他内容
4. 如果没有明显关联，返回空数组 []

示例输出: ["Docker的常用命令", "Kubernetes"]"""

        try:
            response = call_llm(prompt)
            related = parse_related_notes(response)

            if related:
                print(colored(f" ✓ 找到 {len(related)} 个关联", C.GREEN))
                for name in related:
                    print(f"     → [[{name}]]")

                if not dry_run:
                    add_links_to_note(filepath, related)
                    success += 1
            else:
                print(colored(" ✓ 无关联", C.DIM))
                success += 1

            sys.stdout.flush()

        except Exception as e:
            print(colored(f" ❌ 失败: {e}", C.RED))
            failed += 1
            sys.stdout.flush()

    # 汇总
    print(colored(f"\n{'═' * 50}", C.DIM))
    print(colored("📊 关联分析完成:", C.BOLD))
    print(f"   分析: {success} 篇")
    if failed:
        print(colored(f"   失败: {failed} 篇", C.RED))
    sys.stdout.flush()

    if dry_run:
        print(colored("\n🔍 这是预览模式，去掉 --dry-run 参数执行实际关联", C.YELLOW))
        sys.stdout.flush()


# ── 主流程 ────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(colored("\n📚 有道云笔记导入工具\n", C.BOLD + C.CYAN))
        print("用法:")
        print("  导入笔记:   python import_youdao.py <导出目录>")
        print("  分析关联:   python import_youdao.py --link")
        print("  预览模式:   加 --dry-run 参数")
        sys.exit(1)

    if "--link" in sys.argv:
        dry_run = "--dry-run" in sys.argv
        analyze_links(dry_run=dry_run)
    else:
        source_dir = sys.argv[1]
        dry_run = "--dry-run" in sys.argv
        process_directory(source_dir, dry_run=dry_run)


if __name__ == "__main__":
    main()
