#!/usr/bin/env python3
"""
Conservative formatter for imported vault notes.

It fixes high-confidence import artifacts:
- duplicated frontmatter list fields such as related/tags
- unfenced command/config/SQL/Java/Python snippets
- trailing exported line numbers inside inferred code blocks
- duplicated trailing "related notes" body sections
"""

from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [
    "00-Inbox",
    "10-Projects",
    "20-Areas",
    "30-Resources",
    "40-Archives",
    "50-Daily",
    "60-MOC",
]

LIST_FIELDS = {"related", "tags"}

COMMAND_RE = re.compile(
    r"^\s*(sudo|su|docker|kubectl|tar|unzip|zip|mv|cp|rm|mkdir|chmod|chown|"
    r"vim?|nano|cat|grep|awk|sed|curl|wget|ssh|scp|systemctl|sysctl|"
    r"firewall-cmd|iptables|conda|pip|python3?|java|mvn|npm|yarn|pnpm|git|"
    r"mysql|psql|disql|dmctl|cd|ls|\.\/)\b"
)
SQL_RE = re.compile(
    r"^\s*(SELECT|FROM|WHERE|AND|OR|INSERT|INTO|UPDATE|DELETE|CREATE|ALTER|DROP|"
    r"ORDER\s+BY|GROUP\s+BY|HAVING|JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|INNER\s+JOIN|"
    r"VALUES|SET|DECLARE|BEGIN|END|COMMIT|ROLLBACK|MERGE|CALL|WITH\s+[A-Za-z_][A-Za-z0-9_]*\s+AS|UNION|"
    r"COMMENT\s+ON|START\s+WITH|INCREMENT\s+BY|NOCACHE|NOCYCLE|CONSTRAINT)\b",
    re.IGNORECASE,
)
CONFIG_RE = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_.-]*\s*[:=]\s*.+")
ASSIGNMENT_RE = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_.\[\]'\"]*\s*=\s*.+")
TUPLE_ASSIGNMENT_RE = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_,\s]*\s*=\s*.+")
PYTHON_RE = re.compile(r"^\s*(from\s+\S+\s+import|import\s+\S+|print\(|with\s+open\(|\w+\s*=\s*.+)")
SQL_KEYWORD_NUMBER_RE = re.compile(
    r"^(\s*)(SELECT|FROM|WHERE|AND|OR|INSERT|INTO|VALUES|UPDATE|DELETE|CREATE|ALTER|DROP|"
    r"COMMENT|START|INCREMENT|NOCACHE|NOCYCLE|UNION|CASE|WHEN|THEN|ELSE|END)(\d{1,3})(\s*)$",
    re.IGNORECASE,
)
SQL_FRAGMENT_NUMBER_RE = re.compile(
    r"^\s*(?:"
    r"[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*,?\d{1,3}|"
    r"'.*'\d{1,3}|"
    r"WHEN\b.*\d{1,3}|"
    r"ELSE\d{1,3}|"
    r"END\b.*\d{1,3}"
    r")\s*$",
    re.IGNORECASE,
)
CODE_MARKER_RE = re.compile(
    r"^\s*(?P<lang>python|java|javascript|js|sql|shell|bash|xml|json)\s+"
    r"(?:\u590d\u5236\u4ee3\u7801|copy code)\s*(?P<rest>.*)$",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes")
    return parser.parse_args()


def iter_note_files() -> list[Path]:
    files: list[Path] = []
    for dirname in TARGET_DIRS:
        root = VAULT_ROOT / dirname
        if root.exists():
            files.extend(sorted(root.rglob("*.md")))
    return sorted(files)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return parts[1].strip("\n"), parts[2].lstrip("\n")


def parse_list_value(value: str) -> list[str] | None:
    value = value.strip()
    if value.startswith("["):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
    if value:
        return [value.strip().strip('"').strip("'")]
    return []


def merge_unique(existing: list[str], new_values: list[str]) -> list[str]:
    merged: list[str] = []
    for item in existing + new_values:
        item = item.strip()
        if item and item not in merged:
            merged.append(item)
    return merged


def normalize_frontmatter(fm_text: str | None) -> tuple[str | None, list[str]]:
    if fm_text is None:
        return None, []

    values: OrderedDict[str, str | list[str]] = OrderedDict()
    raw_lines: list[str] = []

    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raw_lines.append(line)
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in LIST_FIELDS:
            parsed = parse_list_value(value)
            if parsed is None:
                values[key] = value
            else:
                current = values.get(key, [])
                current_list = current if isinstance(current, list) else parse_list_value(str(current)) or []
                values[key] = merge_unique(current_list, parsed)
        else:
            values[key] = value

    related = values.get("related", [])
    related_list = related if isinstance(related, list) else parse_list_value(str(related)) or []

    lines = ["---"]
    for key, value in values.items():
        if isinstance(value, list):
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        elif value == "":
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {value}")
    lines.extend(raw_lines)
    lines.append("---")
    return "\n".join(lines), related_list


def strip_related_section(body: str) -> str:
    return re.sub(r"\n*---\n## \u76f8\u5173\u7b14\u8bb0\n.*\Z", "", body, flags=re.DOTALL).rstrip()


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def is_numeric_artifact(line: str) -> bool:
    stripped = line.strip()
    return bool(re.fullmatch(r"\d{1,3}|(\d+\.)+", stripped))


def is_code_like(line: str, in_run: bool = False) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("```"):
        return False
    if SQL_KEYWORD_NUMBER_RE.match(line):
        return True
    if SQL_FRAGMENT_NUMBER_RE.match(line):
        return True
    if CODE_MARKER_RE.match(stripped):
        return True
    if COMMAND_RE.match(stripped) or SQL_RE.match(stripped):
        return True
    if PYTHON_RE.match(stripped):
        return True
    if stripped.startswith(("<", "</", "<?", "<!", "{", "}", "[", "]")):
        return True
    if stripped.startswith(("# ", "-- ")):
        return in_run or bool(re.search(r"\d{1,3}$", stripped))
    if stripped.endswith(("\\", ";", "{", "}", ")", "};")) and not has_cjk(stripped):
        return True
    if CONFIG_RE.match(stripped) and not re.match(r"^[\u4e00-\u9fff]+[:：]", stripped):
        return True
    if ASSIGNMENT_RE.match(stripped) or TUPLE_ASSIGNMENT_RE.match(stripped):
        return True
    if re.match(r'^\s*["\'][A-Za-z_][A-Za-z0-9_.-]*["\']\s*:', stripped):
        return True
    if in_run and not has_cjk(stripped):
        ascii_count = sum(ord(ch) < 128 for ch in stripped)
        return ascii_count / max(len(stripped), 1) > 0.65
    return False


def normalize_marker(line: str) -> tuple[str, str | None]:
    match = CODE_MARKER_RE.match(line.strip())
    if not match:
        return line, None
    lang = match.group("lang").lower()
    if lang == "js":
        lang = "javascript"
    rest = match.group("rest").strip()
    return rest, lang


def strip_export_line_numbers(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        raw = line.rstrip()
        keyword_match = SQL_KEYWORD_NUMBER_RE.match(raw)
        if keyword_match:
            cleaned.append(f"{keyword_match.group(1)}{keyword_match.group(2)}{keyword_match.group(4)}".rstrip())
            continue
        spaced_line_number = re.match(r"^(.*[;,)'])\s+(\d{1,3})$", raw)
        if spaced_line_number and int(spaced_line_number.group(2)) <= 300:
            cleaned.append(spaced_line_number.group(1).rstrip())
            continue
        then_zero_line_number = re.match(r"^(.*\bTHEN\s+0)(\d{1,3})$", raw, re.IGNORECASE)
        if then_zero_line_number:
            cleaned.append(then_zero_line_number.group(1).rstrip())
            continue
        sql_word_line_number = re.match(r"^(.*\b(?:THEN|ELSE|END|CASE|AS)\s*)(\d{1,3})$", raw, re.IGNORECASE)
        if sql_word_line_number and int(sql_word_line_number.group(2)) <= 300:
            if re.search(r"\bTHEN\s*$", sql_word_line_number.group(1), re.IGNORECASE) and sql_word_line_number.group(2) in {"0", "1"}:
                cleaned.append(raw)
                continue
            cleaned.append(sql_word_line_number.group(1).rstrip())
            continue
        dotted_identifier_line_number = re.match(
            r"^(\s*[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*?[A-Za-z_])(\d{1,3})(\s*)$",
            raw,
        )
        if dotted_identifier_line_number and int(dotted_identifier_line_number.group(2)) <= 300:
            cleaned.append(f"{dotted_identifier_line_number.group(1)}{dotted_identifier_line_number.group(3)}".rstrip())
            continue
        comment_close_line_number = re.match(r"^(.*\*/)(\d{1,3})$", raw)
        if comment_close_line_number and int(comment_close_line_number.group(2)) <= 300:
            cleaned.append(comment_close_line_number.group(1).rstrip())
            continue
        if is_numeric_artifact(raw):
            digits = re.findall(r"\d+", raw)
            if digits and int(digits[-1]) <= 300:
                continue

        match = re.search(r"(?<!\d)(\d{1,3})$", raw)
        if match:
            number = match.group(1)
            prefix = raw[: -len(number)]
            if not prefix.strip():
                cleaned.append(raw)
                continue
            if number.startswith("0") and len(number) > 1:
                cleaned.append(raw)
                continue
            if prefix[-1:] in {".", "_", "-"}:
                cleaned.append(raw)
                continue
            if prefix[-1:].isspace() or prefix[-1:] in {"=", "<", ">", "+", "*", "/", "%"}:
                cleaned.append(raw)
                continue
            if prefix[-1:].isalnum():
                cleaned.append(raw)
                continue
            if re.search(r"[A-Za-z_]\d{2,}$", prefix):
                cleaned.append(raw)
                continue
            if int(number) <= 300:
                raw = prefix.rstrip()
        cleaned.append(raw)
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    return cleaned


def has_unclosed_single_quote(line: str) -> bool:
    escaped = False
    count = 0
    for ch in line:
        if ch == "'" and not escaped:
            count += 1
        escaped = ch == "\\" and not escaped
    return count % 2 == 1


def join_wrapped_sql_strings(lines: list[str]) -> list[str]:
    joined: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        while (
            has_unclosed_single_quote(line)
            and not line.strip().startswith("--")
            and i + 1 < len(lines)
        ):
            next_line = lines[i + 1].strip()
            if not next_line:
                break
            left = line.rstrip()
            separator = "" if left.endswith("-") or (has_cjk(left[-1:]) and has_cjk(next_line[:1])) else " "
            line = f"{line}{separator}{next_line}"
            i += 1
        joined.append(line)
        i += 1
    return joined


def compact_cjk_spaces_in_sql_strings(lines: list[str]) -> list[str]:
    compacted: list[str] = []
    pattern = re.compile(r"([\u4e00-\u9fff])\s+([\u4e00-\u9fff])")

    for line in lines:
        pieces = re.split(r"('(?:[^']|'')*')", line)
        for index, piece in enumerate(pieces):
            if piece.startswith("'") and piece.endswith("'"):
                pieces[index] = pattern.sub(r"\1\2", piece)
        compacted.append("".join(pieces))
    return compacted


def normalize_code_block_lines(lines: list[str], lang: str) -> list[str]:
    cleaned = strip_export_line_numbers(lines)
    if lang == "sql" or any(SQL_RE.match(line.strip()) for line in cleaned):
        cleaned = join_wrapped_sql_strings(cleaned)
        cleaned = compact_cjk_spaces_in_sql_strings(cleaned)
    return cleaned


def infer_language(lines: list[str], explicit: str | None = None) -> str:
    if explicit:
        return explicit
    joined = "\n".join(lines)
    sql_hits = sum(1 for line in lines if SQL_RE.match(line.strip()))
    if sql_hits >= 2 or re.search(r"\b(from|where|select|insert|update|delete)\b", joined, re.IGNORECASE):
        return "sql"
    if any(line.lstrip().startswith(("<", "</", "<?", "<!")) for line in lines):
        return "xml"
    if any(
        re.search(r"\b(import|def|with open|print\(|pipeline\(|from_pretrained|context_vectors|retrieved_docs|np\.)", line)
        for line in lines
    ):
        return "python"
    if any(COMMAND_RE.match(line.strip()) or line.strip().startswith("./") for line in lines):
        return "bash"
    if any(re.search(r"\b(public|private|class|new |return |HttpURLConnection)\b", line) for line in lines):
        return "java"
    if any(CONFIG_RE.match(line.strip()) for line in lines):
        return "yaml"
    return ""


def parse_fence(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("```"):
        return None
    return stripped[3:].strip().lower()


def is_sqlish_lines(lines: list[str], lang: str = "") -> bool:
    if lang == "sql":
        return True
    if lang and lang != "sql":
        return False
    return any(SQL_RE.match(line.strip()) for line in lines)


def is_loose_sql_continuation(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("---", "## ")):
        return False
    if SQL_RE.match(stripped):
        return True
    if stripped.startswith(("--", "'", '"', "NULL", "null", ")", ",")):
        return True
    if stripped.endswith((",", ");", ")", ";")) and not has_cjk(stripped):
        return True
    if re.match(r"^[A-Z0-9_\"'()., /:-]+$", stripped) and len(stripped) > 3:
        return True
    return False


def collect_fence(lines: list[str], start: int) -> tuple[str, list[str], int]:
    lang = parse_fence(lines[start]) or ""
    content: list[str] = []
    i = start + 1
    while i < len(lines):
        if lines[i].strip().startswith("```"):
            return lang, content, i + 1
        content.append(lines[i])
        i += 1
    return lang, content, i


def repair_split_sql_fences(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0

    while i < len(lines):
        lang = parse_fence(lines[i])
        if lang is None:
            out.append(lines[i])
            i += 1
            continue

        block_lang, content, next_i = collect_fence(lines, i)
        if not is_sqlish_lines(content, block_lang):
            out.append(lines[i])
            out.extend(normalize_code_block_lines(content, block_lang))
            out.append("```")
            i = next_i
            continue

        merged = normalize_code_block_lines(content, "sql")
        i = next_i
        trailing_blank = False

        while True:
            blanks: list[str] = []
            while i < len(lines) and not lines[i].strip():
                blanks.append(lines[i])
                i += 1

            if i < len(lines) and parse_fence(lines[i]) is not None:
                next_lang, next_content, after = collect_fence(lines, i)
                if is_sqlish_lines(next_content, next_lang) or merged:
                    merged.extend(normalize_code_block_lines(next_content, "sql"))
                    i = after
                    continue

            loose: list[str] = []
            while (
                i < len(lines)
                and parse_fence(lines[i]) is None
                and (
                    is_loose_sql_continuation(lines[i])
                    or (
                        loose
                        and has_unclosed_single_quote(loose[-1])
                        and not loose[-1].strip().startswith("--")
                    )
                    or (
                        not loose
                        and merged
                        and has_unclosed_single_quote(merged[-1])
                        and not merged[-1].strip().startswith("--")
                    )
                )
            ):
                loose.append(lines[i])
                i += 1

            if loose:
                merged.extend(normalize_code_block_lines(loose, "sql"))
                continue

            if blanks:
                trailing_blank = True
            break

        out.append("```sql")
        out.extend(compact_cjk_spaces_in_sql_strings(join_wrapped_sql_strings(merged)))
        out.append("```")
        if trailing_blank:
            out.append("")

    return "\n".join(out)


def should_fence(run: list[str]) -> bool:
    nonempty = [line for line in run if line.strip()]
    if not nonempty:
        return False
    if any(CODE_MARKER_RE.match(line.strip()) for line in nonempty):
        return True
    if len(nonempty) >= 2:
        return True
    line = nonempty[0].strip()
    return bool(
        COMMAND_RE.match(line)
        or SQL_RE.match(line)
        or CONFIG_RE.match(line)
        or ASSIGNMENT_RE.match(line)
        or TUPLE_ASSIGNMENT_RE.match(line)
        or PYTHON_RE.match(line)
    )


def append_blank_if_needed(out: list[str]) -> None:
    if out and out[-1].strip():
        out.append("")


def format_body(body: str) -> str:
    body = body.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    lines = body.split("\n")
    out: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        if line.strip().startswith("```"):
            append_blank_if_needed(out)
            out.append(line)
            i += 1
            while i < len(lines):
                out.append(lines[i].rstrip())
                if lines[i].strip().startswith("```"):
                    i += 1
                    break
                i += 1
            if i < len(lines) and lines[i].strip():
                out.append("")
            continue

        if not line.strip():
            if out and out[-1].strip():
                out.append("")
            i += 1
            continue

        if is_numeric_artifact(line):
            i += 1
            continue

        if is_code_like(line):
            run: list[str] = []
            explicit_lang: str | None = None
            while i < len(lines):
                current = lines[i].rstrip()
                normalized, marker_lang = normalize_marker(current)
                if marker_lang:
                    explicit_lang = marker_lang
                    current = normalized
                if not current.strip():
                    break
                if is_code_like(current, in_run=bool(run)) or is_numeric_artifact(current):
                    run.append(current)
                    i += 1
                    continue
                break

            if should_fence(run):
                cleaned = strip_export_line_numbers(run)
                if cleaned:
                    append_blank_if_needed(out)
                    lang = infer_language(cleaned, explicit_lang)
                    out.append(f"```{lang}".rstrip())
                    out.extend(cleaned)
                    out.append("```")
                    if i < len(lines) and lines[i].strip():
                        out.append("")
                continue

            out.extend(run)
            continue

        out.append(line)
        i += 1

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_note(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    fm_text, body = split_frontmatter(text)
    fm_block, related = normalize_frontmatter(fm_text)
    body = strip_related_section(body)
    body = format_body(body)
    body = repair_split_sql_fences(body)

    parts: list[str] = []
    if fm_block:
        parts.append(fm_block)
    if body:
        parts.append(body)
    if related:
        related_links = "\n".join(f"- [[{name}]]" for name in related)
        parts.append(f"---\n## \u76f8\u5173\u7b14\u8bb0\n{related_links}")
    return "\n\n".join(parts).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    changed: list[Path] = []
    for path in iter_note_files():
        original = path.read_text(encoding="utf-8")
        formatted = format_note(original)
        if formatted != original:
            changed.append(path)
            if args.apply:
                path.write_text(formatted, encoding="utf-8")

    mode = "updated" if args.apply else "would update"
    print(f"{mode}: {len(changed)} files")
    for path in changed:
        print(path.relative_to(VAULT_ROOT).as_posix())


if __name__ == "__main__":
    main()
