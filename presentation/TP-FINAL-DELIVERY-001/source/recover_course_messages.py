"""Recover explicitly named course inputs and final responses, recording exact message hashes."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
folder = root / "03_TEAM_COLLABORATION/transcripts"
folder.mkdir(parents=True,exist_ok=True)
session_id="01a21af4-befa-78a1-8c50-f4960edbdac0"
session_path=next((Path.home()/".codex/sessions/2026/11/27").glob("*"+session_id+".jsonl"))
pairs={"01":(13,683),"02":(693,1817),"03":(1824,2726),"04":(2733,4167),"05":(4180,5078),"06":(5087,6151)}
items={n:(phase,role) for phase,(a,b) in pairs.items() for n,role in [(a,"user"),(b,"assistant")]}
manifest=[]
for n,line in enumerate(session_path.open(encoding="utf-8"),1):
    if n not in items:
        continue
    phase,role=items[n]
    entry=json.loads(line)
    msg=entry["payload"]
    assert entry["type"]=="response_item" and msg["type"]=="message" and msg["role"]==role
    if role=="assistant":
        assert msg["phase"]=="final_answer"
    content=msg["content"]
    assert len(content)==1 and content[0]["type"] in ("input_text","output_text")
    data=content[0]["text"].encode("utf-8")
    name=f"TP-PHASE-{phase}-{role}.txt"
    (folder/name).write_bytes(data)
    manifest.append(dict(file=name,session=session_id,event_line=n,timestamp=entry["timestamp"],
                         role=role,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
assert len(manifest)==12
(folder/"message-index.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
rows=[f"| PHASE-{phase} | [原始任务](TP-PHASE-{phase}-user.txt) | [最终回应](TP-PHASE-{phase}-assistant.txt) |" for phase in pairs]
(folder/"README.md").write_text("# 六个阶段的原始输入与最终回应\n\nCodex 从项目历史会话中按消息角色和行号提取 user 输入与对应 assistant 最终答复，保持文字原样。每条消息的时间、来源与 SHA-256 见[索引](message-index.json)。这些记录属于 Codex 逐条会话原文摘取；关键历史过程仍需成功的原生 /export 或教师对等价材料的认可。原生 Claude /export 的归档覆盖另一次失败尝试。\n\n| 阶段 | 输入 | 输出 |\n|---|---|---|\n"+"\n".join(rows)+"\n",encoding="utf-8")
