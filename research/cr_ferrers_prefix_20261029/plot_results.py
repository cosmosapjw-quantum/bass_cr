from pathlib import Path
import json, statistics
import matplotlib.pyplot as plt
p=Path(__file__).parent
prefix=[json.loads((p/f'BENCHMARK_SOURCE_TRIAL{i}.json').read_text())['wall_seconds'] for i in (1,2,3)]
parent=[json.loads((p/f'BENCHMARK_PARENT_TRIAL{i}.json').read_text())['wall_seconds'] for i in (1,2,3)]
fig,ax=plt.subplots(figsize=(6.2,3.7))
ax.plot([1,2,3],parent,marker='o',label='PR123 explicit HL graph')
ax.plot([1,2,3],prefix,marker='s',label='Prefix segment network')
ax.set(xlabel='Paired run index',ylabel='End-to-end wall time (s)',title='Original 3201-atom K=3 eV, three budgets')
ax.set_xticks([1,2,3]);ax.grid(alpha=.25);ax.legend(loc='upper right',fontsize=8)
fig.tight_layout();fig.savefig(p/'PERFORMANCE_PAIRED.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(6.2,3.5))
ax.bar(['Original HL edges','Prefix graph arcs'],[102831,4307]);ax.set_yscale('log');ax.set_ylim(1500,350000);ax.set_ylabel('Forward arc count (log scale)');ax.set_title('Exact Ferrers-prefix graph representation')
for i,v in enumerate((102831,4307)):ax.text(i,v*1.07,f'{v:,}',ha='center',fontsize=10)
fig.tight_layout();fig.savefig(p/'GRAPH_COMPRESSION.png',dpi=160);plt.close(fig)
print('saved figure widths',[(x,(p/x).stat().st_size) for x in ('PERFORMANCE_PAIRED.png','GRAPH_COMPRESSION.png')]);print('ratio of medians',statistics.median(parent)/statistics.median(prefix))
