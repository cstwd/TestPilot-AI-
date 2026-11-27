"""Plot the four arms on the shared denominator using standalone Matplotlib."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

report=Path(__file__).resolve().parents[2]/"reports/phase05"
data=json.loads((report/"summary.json").read_bytes())
names=["A   Qwen2.5-Coder 0.5B","B   Template","C   Qwen3.8-27B initial","D   Qwen3.8-27B + feedback"]
rows=list(data["groups"].values())
fig,ax=plt.subplots(figsize=(9.6,4.5),layout="constrained")
fig.patch.set_facecolor("#f7f8fa")
ax.set_facecolor("#f7f8fa")
bars=ax.barh(names,[row["all_manifest_detection"] for row in rows],height=.50,
             color=["#657b8b","#718096","#276c90","#138477"],zorder=2)
ax.invert_yaxis()
ax.set_title("Mutation detection by test suite",loc="left",weight="bold",fontsize=16,pad=16)
ax.set_xlabel("Share of all 117 preregistered mutant opportunities detected (%)",labelpad=10)
ax.set_xticks(range(0,101,10))
ax.set_xlim(0,111)
ax.set_axisbelow(True)
ax.grid(axis="x",alpha=.2)
ax.axvline(55,color="#58727f",linestyle="--",linewidth=.8,label="Initial reference target 55%")
ax.axvline(70,color="#366a60",linestyle=":",linewidth=1,label="Final reference target 70%")
ax.legend(loc="lower right",bbox_to_anchor=(1,1.01),frameon=False,fontsize=8,ncol=2)
ax.spines[:].set_visible(False)
ax.tick_params(length=0,pad=7)
ax.bar_label(bars,labels=[f"{r['killed']}/117 · {r['all_manifest_detection']:.2f}%" for r in rows],padding=6,fontsize=9)
fig.savefig(report/"mutation-score.png",dpi=180)
fig.savefig(report/"mutation-score.svg")
