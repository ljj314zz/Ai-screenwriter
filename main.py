import argparse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

from agno.agent import Agent
from agno.db.in_memory.in_memory_db import InMemoryDb
from dotenv import load_dotenv

load_dotenv()  # 从 .env 加载 OPENAI_API_KEY 等环境变量
# =============== 1) 结构化输出模型（稳定拿结果） ===============


class SeasonBlueprint(BaseModel):
    theme: str = Field(..., description="本季主题或主轴，如：逆袭、复仇、成长、商战等")
    premise: str = Field(..., description="一句话梗概（logline）")
    genre: str = Field(..., description="类型，如 都市/古装/职场/校园/仙侠/科幻 等")
    audience: str = Field(..., description="目标受众，如 男性向/女性向/泛用户 等")
    num_episodes: int = Field(..., gt=0, le=100, description="本季集数")
    episode_duration_minutes: int = Field(
        ..., gt=2, le=30, description="每集时长（分钟）"
    )
    core_conflicts: List[str] = Field(..., description="核心矛盾点、冲突钩子（2-5个）")
    arcs: List[str] = Field(..., description="主线与支线弧线（每条1句话）")
    main_characters: List[str] = Field(
        ..., description="主角团（名称 + 8-15字人设标签）"
    )
    episode_titles: List[str] = Field(
        ..., description="每集的短标题（高信息密度、抓眼球）"
    )

    @validator("episode_titles")
    def titles_len_match(cls, v, values):
        num = values.get("num_episodes")
        if num and len(v) != num:
            raise ValueError(f"episode_titles 数量必须等于 num_episodes（{num}）")
        return v


class SceneBeat(BaseModel):
    index: int = Field(..., description="场景/情节点序号，从 1 开始")
    title: str = Field(..., description="场景标题（短）")
    duration_seconds: int = Field(
        ..., gt=10, lt=600, description="建议时长（秒），适合短剧快节奏剪辑"
    )
    setting: str = Field(..., description="场景地点/时间氛围")
    characters: List[str] = Field(..., description="出场角色")
    synopsis: str = Field(..., description="剧情梗概（2-4句），强调爽点与推进")
    hook: str = Field(..., description="该场景的吸睛卖点/冲突钩子")
    twist: Optional[str] = Field(None, description="可选反转点（如有）")
    golden_line: Optional[str] = Field(None, description="金句/燃点台词（如有）")
    notes: List[str] = Field(
        default_factory=list, description="导演/剪辑提示（如：快切、配乐、特写）"
    )


class EpisodeOutline(BaseModel):
    episode_number: int = Field(..., gt=0, description="第几集")
    title: str = Field(..., description="本集标题")
    target_duration_minutes: int = Field(
        ..., gt=2, le=30, description="本集目标时长（分钟）"
    )
    opening_hook: str = Field(..., description="开场 10-20 秒的钩子（核心冲突/抓眼球）")
    beats: List[SceneBeat] = Field(..., description="场景/情节点序列，强调快节奏与反转")
    cliffhanger: str = Field(..., description="结尾悬念/刺激下一集继续看")
    production_notes: List[str] = Field(
        default_factory=list, description="制作注意事项，如转场/配乐/剪辑节奏"
    )


class ScriptPackage(BaseModel):
    blueprint: SeasonBlueprint
    episodes: List[EpisodeOutline]


# =============== 2) 工具（为模型提供“爽剧套路”和“节奏模板”） ===============

# 简化版套路库（可替换为你的在线检索/RAG）
TROPES_BY_GENRE: Dict[str, List[str]] = {
    "都市": [
        "职场碾压",
        "老同学反差",
        "豪门打脸",
        "社交媒体爆点",
        "反客为主",
        "花式反转",
    ],
    "古装": ["错位身份", "家国大义", "权谋反噬", "以弱胜强", "庙堂与江湖", "天降贵人"],
    "职场": ["数据说话", "夺权之争", "越级通天", "背锅与反背锅", "临门一脚逆转"],
    "校园": ["学霸杠上学渣", "社团竞赛", "黑马崛起", "暗恋明牌", "宿敌组队"],
    "仙侠": ["灵根逆天", "宗门争锋", "秘境奇遇", "强者之路", "因果循环"],
    "科幻": ["时间回溯", "平行世界", "身份替换", "脑机接口", "真相反噬"],
}


def get_tropes(genre: str) -> List[str]:
    """返回该类型常见的爽点/套路关键词（用于启发式引导）。"""
    g = (genre or "").strip()
    return TROPES_BY_GENRE.get(g, TROPES_BY_GENRE["都市"])


def rhythm_template(pacing: str = "fast") -> Dict[str, Any]:
    """
    返回一个场景节奏模板（比例表 + 建议镜头语言）。
    - fast: 极快节奏；每 20-60 秒一个钩子；高密度冲突/反转。
    - punchy: 中高速；每 45-90 秒一个钩子；强过门音乐与金句。
    """
    if pacing == "fast":
        return {
            "name": "fast",
            "beat_ratios": [0.08, 0.12, 0.18, 0.22, 0.20, 0.20],  # 比例和为 1
            "directing_tips": [
                "开场即冲突，台词短促，快切；10-20s 内给出核心钩子",
                "多用中近景+特写，强化表情管理与反应",
                "每一两场景嵌入反转或信息揭示",
                "用配乐/鼓点推动节奏；空拍留白不超过 3 秒",
            ],
        }
    return {
        "name": "punchy",
        "beat_ratios": [0.12, 0.18, 0.20, 0.20, 0.15, 0.15],
        "directing_tips": [
            "开场 20-30s 设置强钩子",
            "用过门音乐分隔段落，制造“段落爽点”",
            "每 1 分钟至少一个信息跃迁或小反转",
        ],
    }


def catchy_titles(seed: str, count: int = 5) -> List[str]:
    """从主题/梗概生成 5 个抓眼的备选标题（短、信息密度高）。"""
    base = seed.strip().replace(" ", "")
    variants = [
        f"{base}：当场翻盘",
        f"{base}！三招打脸",
        f"{base}，一夜逆袭",
        f"{base}：局中有局",
        f"{base}·反客为主",
    ]
    return variants[: max(1, min(count, len(variants)))]


# =============== 3) 构造 Agno Agent（开启高级能力） ===============


def make_generator_agent(session_id: str = "shuangju-session") -> Agent:
    db = InMemoryDb()  # 进程内持久，避免 Memory 警告；生产可替换为你的 DB 实现
    agent = Agent(
        name="ShuangjuWriter",
        role=(
            "你是资深短剧编剧/叙事设计师，擅长极致爽点设计、快节奏推进、"
            "高密度反转与金句输出，懂得为剪辑和配乐预留空间。"
        ),
        instructions=(
            "- 输出必须高信息密度、极简短句、强动词；\n"
            "- 每 20-60 秒制造一个钩子或反转；\n"
            "- 每集结尾必须有 cliffhanger；\n"
            "- 贴合目标受众与平台观影习惯（竖屏/快节奏/字幕友好）。\n"
            "- 善用工具：get_tropes/ rhythm_template/ catchy_titles 来优化结构。"
        ),
        description="短剧（爽剧）生成器：从主题到整季，再到每集大纲与场景节拍。",
        expected_output="结构化 JSON，字段完备，可直接用于拍摄脚本细化与后续编排。",
        # 结构化与思考
        parse_response=True,
        use_json_mode=True,
        reasoning=False,
        reasoning_min_steps=1,
        reasoning_max_steps=4,
        # 记忆与历史
        db=db,
        enable_user_memories=True,
        enable_agentic_memory=True,
        enable_session_summaries=True,
        read_chat_history=True,
        add_session_state_to_context=True,
        # 工具
        tools=[get_tropes, rhythm_template, catchy_titles],
        tool_call_limit=6,
        tool_choice="auto",
        # 上下文增强
        add_name_to_context=True,
        add_datetime_to_context=True,
        timezone_identifier="Asia/Shanghai",
        # 事件/流式
        stream=False,
        stream_intermediate_steps=False,
        store_events=False,
        # 会话
        session_id=session_id,
        session_state={"notes": []},
    )
    return agent


# =============== 4) 任务流程（蓝图 -> 每集大纲 -> 汇总） ===============


def gen_season_blueprint(
    agent: Agent,
    theme_or_plot: str,
    genre: str,
    audience: str,
    num_episodes: int,
    minutes_per_ep: int,
) -> SeasonBlueprint:
    # 切到蓝图输出
    agent.output_schema = SeasonBlueprint

    prompt = f"""
用户输入主题/情节：{theme_or_plot}
请你基于“爽剧”叙事风格，产出本季《蓝图》：
- genre：{genre}
- audience：{audience}
- num_episodes：{num_episodes}
- episode_duration_minutes：{minutes_per_ep}

要求：
1) premise 一句话高概括，带冲突与反差；
2) core_conflicts 2-5 条（强动词、抓眼球）；
3) arcs 覆盖主线+1-2条支线，且每条 1 句话；
4) main_characters：主角团简短人设标签；
5) episode_titles：给出 {num_episodes} 个抓眼短标题，长度 8-14 字为宜；
6) 可调用工具 get_tropes/ rhythm_template/ catchy_titles 优化输出；
7) 严格输出为 JSON（Agno 已启用结构化）。
"""
    res = agent.run(prompt)
    data = res.content  # 已结构化为 SeasonBlueprint
    if isinstance(data, dict):
        return SeasonBlueprint(**data)
    if isinstance(data, SeasonBlueprint):
        return data
    # 如果模型偶发输出不完全结构化，尝试二次构造
    return SeasonBlueprint.parse_obj(data)  # type: ignore


def gen_episode_outline(
    agent: Agent,
    blueprint: SeasonBlueprint,
    episode_number: int,
) -> EpisodeOutline:
    agent.output_schema = EpisodeOutline

    ep_title = blueprint.episode_titles[episode_number - 1]
    minutes = blueprint.episode_duration_minutes
    prompt = f"""
现在基于本季蓝图，请产出第 {episode_number} 集的大纲，严格结构化：
- theme：{blueprint.theme}
- premise：{blueprint.premise}
- genre：{blueprint.genre}
- audience：{blueprint.audience}
- title（建议沿用或优化）：{ep_title}
- target_duration_minutes：{minutes}
- arcs：{"; ".join(blueprint.arcs)}
- main_characters：{"; ".join(blueprint.main_characters)}
- 核心冲突：{"; ".join(blueprint.core_conflicts)}

要求（爽剧特化）：
1) opening_hook：前 10-20 秒强钩子；
2) beats：6-10 个场景/情节点；每个 beat 提供：setting、synopsis、hook、可选 twist、可选 golden_line、剪辑 notes；
3) 每个 beat 标注建议 duration_seconds（总时长约= {minutes} 分钟）；
4) 每 20-60 秒制造一个“信息跃迁/反转/爽点”；多用“反差、碾压、翻盘”；
5) 结尾 cliffhanger 必须刺激“下一集继续看”；
6) 可调用工具 rhythm_template('fast') 获取节奏比例与导演提示；
7) 严格输出 JSON（Agno 已启用结构化）。
"""
    res = agent.run(prompt)
    data = res.content
    if isinstance(data, dict):
        return EpisodeOutline(**data)
    if isinstance(data, EpisodeOutline):
        return data
    return EpisodeOutline.parse_obj(data)  # type: ignore


def compile_script_package(
    blueprint: SeasonBlueprint,
    episodes: List[EpisodeOutline],
) -> ScriptPackage:
    return ScriptPackage(blueprint=blueprint, episodes=episodes)


# =============== 5) 导出 Markdown（方便发头条或发给团队） ===============


def to_markdown(pkg: ScriptPackage) -> str:
    bp = pkg.blueprint
    md = []
    md.append(f"# 爽剧项目：{bp.theme}")
    md.append("")
    md.append(f"- 类型：{bp.genre}    - 受众：{bp.audience}")
    md.append(
        f"- 集数：{bp.num_episodes}    - 每集：{bp.episode_duration_minutes} 分钟"
    )
    md.append("")
    md.append(f"**一句话梗概（Premise）**：{bp.premise}")
    md.append("")
    md.append("## 核心冲突")
    for i, c in enumerate(bp.core_conflicts, 1):
        md.append(f"{i}. {c}")
    md.append("")
    md.append("## 主线/支线")
    for i, a in enumerate(bp.arcs, 1):
        md.append(f"{i}. {a}")
    md.append("")
    md.append("## 主角团")
    for i, ch in enumerate(bp.main_characters, 1):
        md.append(f"{i}. {ch}")
    md.append("")
    md.append("## 集名")
    for i, t in enumerate(bp.episode_titles, 1):
        md.append(f"{i:02d}. {t}")
    md.append("")

    for ep in pkg.episodes:
        md.append(f"---")
        md.append(
            f"## 第 {ep.episode_number} 集 · {ep.title}（目标 {ep.target_duration_minutes} 分钟）"
        )
        md.append(f"开场钩子：{ep.opening_hook}")
        md.append("")
        md.append("### 场景节拍（Beats）")
        for b in ep.beats:
            md.append(f"- [{b.index}] {b.title} · {b.duration_seconds}s · {b.setting}")
            md.append(f"  - 角色：{', '.join(b.characters)}")
            md.append(f"  - 梗概：{b.synopsis}")
            md.append(f"  - 钩子：{b.hook}")
            if b.twist:
                md.append(f"  - 反转：{b.twist}")
            if b.golden_line:
                md.append(f"  - 金句：{b.golden_line}")
            if b.notes:
                md.append(f"  - 制作提示：{'；'.join(b.notes)}")
        md.append("")
        md.append(f"结尾悬念：{ep.cliffhanger}")
        if ep.production_notes:
            md.append("制作提示：")
            for n in ep.production_notes:
                md.append(f"- {n}")
        md.append("")

    return "\n".join(md)


def save_text(path: str, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# =============== 6) CLI 入口 ===============


def main():
    parser = argparse.ArgumentParser(description="爽剧剧本生成器（基于 Agno）")
    parser.add_argument(
        "--theme",
        type=str,
        required=True,
        help="主题或情节（如：被同学嘲笑的外卖小哥三天变身老板）",
    )
    parser.add_argument("--genre", type=str, default="都市", help="类型（默认：都市）")
    parser.add_argument(
        "--audience", type=str, default="泛用户", help="目标受众（默认：泛用户）"
    )
    parser.add_argument("--episodes", type=int, default=12, help="集数（默认：12）")
    parser.add_argument("--minutes", type=int, default=5, help="每集分钟数（默认：5）")
    parser.add_argument(
        "--max_episodes_to_expand",
        type=int,
        default=3,
        help="为演示仅展开前 N 集（默认：3）",
    )
    parser.add_argument(
        "--outfile", type=str, default="shuangju_script.md", help="导出 Markdown 路径"
    )

    args = parser.parse_args()

    agent = make_generator_agent()
    # Step 1: 蓝图
    blueprint = gen_season_blueprint(
        agent,
        theme_or_plot=args.theme,
        genre=args.genre,
        audience=args.audience,
        num_episodes=args.episodes,
        minutes_per_ep=args.minutes,
    )

    # Step 2: 展开前 N 集大纲（全部展开也可，但内容会很长）
    episodes: List[EpisodeOutline] = []
    to_expand = min(args.max_episodes_to_expand, blueprint.num_episodes)
    for ep_no in range(1, to_expand + 1):
        outline = gen_episode_outline(agent, blueprint, ep_no)
        episodes.append(outline)

    # Step 3: 汇总 + 导出
    pkg = compile_script_package(blueprint, episodes)
    md = to_markdown(pkg)
    save_text(args.outfile, md)

    print(f"\n已生成：{args.outfile}")
    print(
        "（为演示仅展开了前 N 集，想全部生成可把 --max_episodes_to_expand 设置为与 --episodes 相同。）"
    )


if __name__ == "__main__":
    main()
