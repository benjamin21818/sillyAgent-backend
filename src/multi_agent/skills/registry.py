from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SkillSpec:
    """
    技能规格定义。
    
    Attributes:
        name: 技能名称（唯一标识）。
        description: 技能描述，用于显示给用户或 LLM。
        tool_names: 该技能关联的 MCP 工具名称列表。
        trigger_keywords: 触发该技能的关键词列表。
        source_path: 技能定义文件 (SKILL.md) 的路径。
    """
    name: str
    description: str
    tool_names: tuple[str, ...]
    trigger_keywords: tuple[str, ...]
    source_path: Path


def _strip_quotes(s: str) -> str:
    """去除字符串首尾的引号。"""
    s = s.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s


def _parse_front_matter(md_text: str) -> dict[str, str]:
    """
    解析 Markdown 文件头部的 YAML Front Matter。
    
    Args:
        md_text: Markdown 文本内容。
        
    Returns:
        包含元数据的字典，如 name, description 等。
    """
    text = md_text.lstrip()
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines:
        return {}
    if lines[0].strip() != "---":
        return {}

    front_lines: list[str] = []
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            break
        front_lines.append(lines[i])
    else:
        return {}

    out: dict[str, str] = {}
    for line in front_lines:
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = _strip_quotes(v.strip())
        if k:
            out[k] = v
    return out


def _extract_section_lines(md_text: str, heading: str) -> list[str]:
    """
    提取指定标题下的文本行。
    
    Args:
        md_text: Markdown 文本。
        heading: 标题文本（如 "## MCP 工具名称"）。
        
    Returns:
        该标题下的非空行列表，直到遇到下一个标题。
    """
    lines = md_text.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start_idx = i + 1
            break
    if start_idx is None:
        return []

    out: list[str] = []
    for j in range(start_idx, len(lines)):
        s = lines[j].rstrip()
        if s.strip().startswith("#"):
            break
        out.append(s)
    return out


def _parse_tool_names(md_text: str) -> list[str]:
    """解析 SKILL.md 中的 '## MCP 工具名称' 部分，获取关联工具列表。"""
    section = _extract_section_lines(md_text, "## MCP 工具名称")
    names: list[str] = []
    for line in section:
        s = line.strip()
        if not s:
            continue
        # 支持列表项格式 "- tool_name"
        if s.startswith("- "):
            s = s[2:].strip()
        # 去除反引号
        s = s.strip("`").strip()
        if s:
            names.append(s)
    return names


def _parse_trigger_keywords(md_text: str) -> list[str]:
    """解析 SKILL.md 中的 '## 关键词' 和 '## 触发时机' 部分，提取关键词。"""
    keyword_section = _extract_section_lines(md_text, "## 关键词")
    trigger_section = _extract_section_lines(md_text, "## 触发时机")
    keywords: list[str] = []
    for line in keyword_section:
        s = line.strip()
        if not s:
            continue
        if s.startswith("- "):
            s = s[2:].strip()
        s = s.strip()
        if s:
            keywords.append(s)
    for line in trigger_section:
        s = line.strip()
        if not s:
            continue
        if s.startswith("- "):
            s = s[2:].strip()
        s = s.strip()
        if s:
            keywords.append(s)
    return list(dict.fromkeys(keywords))


class SkillRegistry:
    """
    技能注册表，用于加载、管理和检索技能。
    """
    def __init__(self, skills: Iterable[SkillSpec]):
        self._skills = tuple(skills)
        self._skills_by_name = {s.name: s for s in self._skills if s.name}

    @property
    def skills(self) -> tuple[SkillSpec, ...]:
        """获取所有已注册的技能。"""
        return self._skills

    def filter(self, enabled_names: Iterable[str] | None) -> "SkillRegistry":
        """
        根据名称过滤技能，返回新的 SkillRegistry 实例。
        
        Args:
            enabled_names: 启用的技能名称列表。如果为 None 或空，返回自身。
        """
        if not enabled_names:
            return self
        enabled = {n.strip() for n in enabled_names if n and n.strip()}
        return SkillRegistry([s for s in self._skills if s.name in enabled])

    @classmethod
    def load_from_dir(cls, skills_dir: str | Path) -> "SkillRegistry":
        """
        从指定目录加载所有技能 (SKILL.md)。
        
        目录结构约定:
            skills_dir/
                <skill-name>/
                    SKILL.md
        """
        skills_path = Path(skills_dir)
        skills: list[SkillSpec] = []

        if not skills_path.exists():
            return cls([])

        # 遍历所有子目录下的 SKILL.md
        for skill_md in skills_path.glob("*/SKILL.md"):
            try:
                text = skill_md.read_text(encoding="utf-8")
            except Exception:
                continue

            fm = _parse_front_matter(text)
            # 优先使用 front-matter 中的 name，否则使用目录名
            name = (fm.get("name") or skill_md.parent.name).strip()
            description = (fm.get("description") or "").strip()
            
            tool_names = tuple(_parse_tool_names(text))
            trigger_keywords = tuple(_parse_trigger_keywords(text))

            if not tool_names:
                # 没声明工具名的 skill 无法被路由，跳过
                continue

            skills.append(
                SkillSpec(
                    name=name,
                    description=description,
                    tool_names=tool_names,
                    trigger_keywords=trigger_keywords,
                    source_path=skill_md,
                )
            )

        return cls(skills)

    def all_tool_names(self) -> set[str]:
        """获取所有技能包含的所有 MCP 工具名称集合。"""
        out: set[str] = set()
        for s in self._skills:
            out.update(s.tool_names)
        return out

    def select_tool_names(self, user_input: str) -> set[str]:
        """
        依据用户输入做轻量筛选：匹配触发关键词或显式工具名。
        
        Args:
            user_input: 用户的查询文本。
            
        Returns:
            匹配到的工具名称集合。如果没命中任何规则，返回所有工具名称（兜底策略，让 LLM 自己选）。
        """
        text = (user_input or "").strip()
        if not text:
            return self.all_tool_names()

        text_lower = text.lower()
        selected: set[str] = set()

        for s in self._skills:
            # 1) 策略一：用户输入中直接包含了 tool name
            if any(t.lower() in text_lower for t in s.tool_names):
                selected.update(s.tool_names)
                continue

            # 2) 策略二：用户输入命中了技能定义的触发关键词
            for kw in s.trigger_keywords:
                kw_norm = (kw or "").strip()
                if not kw_norm:
                    continue
                # 简单的子串匹配，支持中文
                if kw_norm.lower() in text_lower:
                    print(f"命中关键词 {kw_norm}，关联工具 {s.tool_names}")
                    selected.update(s.tool_names)
                    break

        return selected or self.all_tool_names()

    def format_for_system_prompt(self) -> str:
        """
        格式化技能列表，用于注入到 Agent 的 System Prompt 中。
        
        格式示例:
        - skill: web-search
          - 说明: 搜索网页...
          - 工具: search_web
          - 触发: 联网, 搜索
        """
        if not self._skills:
            return "（无已注册 skills）"

        lines: list[str] = []
        for s in self._skills:
            tools = ", ".join(s.tool_names)
            lines.append(f"- skill: {s.name}")
            if s.description:
                lines.append(f"  - 说明: {s.description}")
            lines.append(f"  - 工具: {tools}")
            if s.trigger_keywords:
                lines.append(f"  - 触发: {', '.join(s.trigger_keywords)}")
        return "\n".join(lines)
