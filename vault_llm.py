#!/usr/bin/env python3
"""
共享的 LLM 和工具函数
"""

import json
import math
import urllib.request
from pathlib import Path

VAULT_ROOT = Path(__file__).parent
CONFIG_FILE = VAULT_ROOT / "90-System" / "config.json"
INDEX_EXCLUSIONS_FILE = VAULT_ROOT / "90-System" / "index_exclusions.json"

# LLM 配置缓存
_config_cache = None
_index_exclusions_cache = None


def load_config():
    """加载配置文件（带缓存）"""
    global _config_cache
    if _config_cache is None:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            _config_cache = json.loads(f.read())
    return _config_cache


def default_index_exclusions():
    """默认的索引/QA 排除规则。"""
    return {
        "directories": [
            ".obsidian",
            ".smart-env",
            "70-Templates",
            "80-Attachments",
            "90-System",
            "copilot",
        ],
        "files": [
            "AGENTS.md",
            "CLAUDE.md",
            "README.md",
            "findings.md",
            "progress.md",
            "task_plan.md",
        ],
        "path_prefixes": [],
        "frontmatter_flags": [
            "private",
            "qa_exclude",
        ],
    }


def load_index_exclusions():
    """加载共享索引/QA 排除规则。"""
    global _index_exclusions_cache
    if _index_exclusions_cache is not None:
        return _index_exclusions_cache

    exclusions = default_index_exclusions()
    if INDEX_EXCLUSIONS_FILE.exists():
        with open(INDEX_EXCLUSIONS_FILE, "r", encoding="utf-8") as f:
            configured = json.loads(f.read())
        for key, value in configured.items():
            if isinstance(value, list):
                exclusions[key] = value

    _index_exclusions_cache = exclusions
    return exclusions


def normalize_vault_path(path) -> str:
    """转换为 vault 内 POSIX 相对路径。"""
    path = Path(path)
    try:
        path = path.relative_to(VAULT_ROOT)
    except ValueError:
        pass
    return path.as_posix()


def parse_frontmatter_block(content: str) -> tuple[dict, str]:
    """解析简单 frontmatter，返回 (frontmatter, body)。"""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    fm = {}
    for line in parts[1].strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = parse_frontmatter_value(value.strip())
    return fm, parts[2].strip()


def parse_frontmatter_value(value):
    """解析 frontmatter 标量/JSON 列表。"""
    value = value.strip()
    if not value:
        return ""

    lowered = value.strip('"\'').lower()
    if lowered in {"true", "false"}:
        return lowered == "true"

    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return value


def format_frontmatter_value(value):
    """格式化 frontmatter 值。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_frontmatter_block(fm_dict: dict) -> str:
    """生成 frontmatter 文本。"""
    lines = ["---"]
    for key, value in fm_dict.items():
        lines.append(f"{key}: {format_frontmatter_value(value)}")
    lines.append("---")
    return "\n".join(lines)


def strip_related_section(content: str) -> str:
    """移除正文末尾的相关笔记块。"""
    return re_sub_related_section(content).rstrip()


def re_sub_related_section(content: str) -> str:
    import re
    return re.sub(r'\n---\n## 相关笔记\n.*$', '', content, flags=re.DOTALL)


def is_truthy_frontmatter_value(value) -> bool:
    """判断 frontmatter 标记是否表示启用。"""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().strip('"\'').lower() in {"true", "yes", "1", "on"}


def should_exclude_from_index(path, content: str | None = None, exclusions: dict | None = None) -> bool:
    """判断路径/内容是否应排除在 QA/索引之外。"""
    exclusions = exclusions or load_index_exclusions()
    rel_path = normalize_vault_path(path)
    parts = rel_path.split("/")

    if any(part in set(exclusions.get("directories", [])) for part in parts):
        return True

    if rel_path in set(exclusions.get("files", [])) or Path(rel_path).name in set(exclusions.get("files", [])):
        return True

    for prefix in exclusions.get("path_prefixes", []):
        if rel_path == prefix or rel_path.startswith(f"{prefix.rstrip('/')}/"):
            return True

    if content:
        fm, _ = parse_frontmatter_block(content)
        for flag in exclusions.get("frontmatter_flags", []):
            if is_truthy_frontmatter_value(fm.get(flag)):
                return True

    return False


def normalize_api_url(url, provider):
    """根据 provider 自动补全完整的 API 路径"""
    url = url.rstrip("/")

    if provider == "anthropic":
        if not url.endswith("/messages"):
            if url.endswith("/v1"):
                url += "/messages"
            else:
                url += "/v1/messages"
    else:
        if not url.endswith("/completions"):
            if url.endswith("/v1"):
                url += "/chat/completions"
            elif url.endswith("/chat"):
                url += "/completions"
            else:
                url += "/v1/chat/completions"

    return url


def get_embedding_config():
    """获取 embedding 配置"""
    config = load_config()
    embedding = config.get("embedding", {})
    return {
        "api": embedding.get("api", "http://127.0.0.1:8000/v1"),
        "model": embedding.get("model", "bge-m3-mlx-4bit"),
        "api_key": embedding.get("api_key", "sk-xxxx"),
    }


def call_llm(prompt, temperature=0.1, max_tokens=1000):
    """调用 LLM API，支持 OpenAI 和 Anthropic 格式"""
    config = load_config()
    llm = config["llm"]
    provider = llm.get("provider", "openai")
    api_url = normalize_api_url(llm["api_url"], provider)
    api_key = llm["api_key"]
    model = llm["model"]

    if provider == "anthropic":
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
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
            "temperature": temperature,
            "max_tokens": max_tokens,
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


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """调用 embedding API 获取文本向量"""
    emb_config = get_embedding_config()

    payload = json.dumps({
        "input": texts,
        "model": emb_config["model"]
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{emb_config['api']}/embeddings",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {emb_config['api_key']}",
        },
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    return [item["embedding"] for item in result["data"]]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算余弦相似度"""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def find_similar_notes(content: str, existing_notes: list, limit: int = 3, threshold: float = 0.7) -> list:
    """基于语义相似度找到最相似的笔记

    Returns:
        list: [(note_name, similarity_score), ...]
    """
    if not existing_notes:
        return []

    # 收集所有笔记名称和可用于 embedding 的文本
    note_names = [n["name"] for n in existing_notes]
    note_texts = [build_note_embedding_text(n) for n in existing_notes]

    # 批量获取嵌入向量
    all_texts = [content] + note_texts
    try:
        embeddings = get_embeddings(all_texts)
    except Exception:
        return []

    content_embedding = embeddings[0]
    note_embeddings = embeddings[1:]

    # 计算相似度
    similarities = []
    for name, embedding in zip(note_names, note_embeddings):
        score = cosine_similarity(content_embedding, embedding)
        if score >= threshold:
            similarities.append((name, round(score, 3)))

    # 排序返回
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:limit]


def build_note_embedding_text(note: dict, max_length: int = 1500) -> str:
    """构造笔记相似度检测的 embedding 文本。"""
    parts = [note.get("name", "")]

    if note.get("summary"):
        parts.append(str(note["summary"]))

    note_content = note.get("content")
    if note_content is None and note.get("path"):
        note_path = VAULT_ROOT / note["path"]
        try:
            note_content = note_path.read_text(encoding="utf-8")
        except Exception:
            note_content = ""

    if note_content:
        fm, body = parse_frontmatter_block(str(note_content))
        if fm.get("summary"):
            parts.append(str(fm["summary"]))
        parts.append(strip_related_section(body)[:max_length])

    return "\n".join(p for p in parts if p).strip()


def assess_content_quality(content: str) -> dict:
    """评估内容质量

    Returns:
        dict: {"score": 1-10, "issues": [str], "strengths": [str]}
    """
    score = 5
    issues = []
    strengths = []

    # 检查长度
    if len(content) < 100:
        issues.append("内容过短")
        score -= 2
    elif len(content) > 500:
        strengths.append("内容详实")
        score += 1

    # 检查是否有结构（标题、列表、代码块）
    has_headers = "## " in content or "### " in content
    has_lists = "- " in content or "* " in content or "1. " in content
    has_code = "```" in content

    if has_headers:
        strengths.append("有结构化标题")
        score += 1
    if has_lists:
        strengths.append("有列表内容")
        score += 1
    if has_code:
        strengths.append("包含代码")
        score += 1

    # 检查 frontmatter
    if content.startswith("---"):
        strengths.append("有 frontmatter")
        score += 1

    # 检查是否只有链接
    if len(content.replace("[[", "").replace("]]", "").strip()) < 50:
        issues.append("内容过少，几乎只有链接")
        score -= 2

    return {
        "score": max(1, min(10, score)),
        "issues": issues,
        "strengths": strengths
    }


def assess_timeliness(content: str) -> dict:
    """判断内容时效性

    Returns:
        dict: {"is_time_sensitive": bool, "reason": str}
    """
    import re

    is_time_sensitive = False
    reason = "通用知识，无时效性"

    # 检查是否包含具体日期（最近一年内）
    date_patterns = [
        r"202[3-6]年\d{1,2}月",  # 2023-2026年X月
        r"\d{4}-\d{2}-\d{2}",      # YYYY-MM-DD
        r"本月|上月|本月|本周|今日|昨天",
        r"最新|刚刚|最近更新",
    ]

    for pattern in date_patterns:
        if re.search(pattern, content):
            is_time_sensitive = True
            reason = "包含近期日期或时效性描述"
            break

    # 检查是否是教程/指南（通常更持久）
    guide_indicators = ["如何", "教程", "指南", "步骤", "安装", "配置", "设置"]
    if any(ind in content for ind in guide_indicators) and not is_time_sensitive:
        reason = "教程类内容，较为持久"
        is_time_sensitive = False

    # 检查是否是会议/日程（通常过时很快）
    meeting_indicators = ["会议", "待办", "todo", "TODO", "deadline", "日程"]
    if any(ind in content for ind in meeting_indicators):
        is_time_sensitive = True
        reason = "包含待办或日程内容，可能需要归档"

    return {
        "is_time_sensitive": is_time_sensitive,
        "reason": reason
    }


def parse_frontmatter_list(fm: dict, key: str, default: list = None) -> list:
    """从 frontmatter 解析列表字段"""
    if default is None:
        default = []
    value = fm.get(key, "[]")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default
    elif isinstance(value, list):
        return value
    return default


def merge_frontmatter_list(fm: dict, key: str, new_values: list) -> list:
    """合并新值到 frontmatter 列表字段"""
    existing = parse_frontmatter_list(fm, key)
    return list(set(existing + new_values))


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
