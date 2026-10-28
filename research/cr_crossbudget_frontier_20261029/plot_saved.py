"""Plot saved, exact validated fixture results; no optimizer is imported."""
import json
from fractions import Fraction
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

here=Path(__file__).resolve().parent
data=json.loads((here/'RESULTS.json').read_text())['four_atom_fixture']
x=[float(Fraction(v)) for v in data['budgets']]
y=[float(Fraction(v)) for v in data['exact_dmax']]
upper=[float(Fraction(v)) for v in data['old_necessary_upper']]
fig,ax=plt.subplots(figsize=(7,4.5),layout='constrained')
ax.plot(x,upper,'--',color='#a66f2c',label='Earlier necessary upper bound',linewidth=2)
ax.plot(x,y,'o-',color='#235c91',label='Exact C ≤ c frontier',linewidth=2)
ax.fill_between(x,y,upper,color='#a66f2c',alpha=.12)
ax.annotate('gap = 1/4',xy=(1,1.87),xytext=(1.18,1.7),
            arrowprops={'arrowstyle':'->','color':'#333333'},fontsize=11)
ax.set(xlabel='Cross-bin budget c / w₀',ylabel='Maximum double-event mass d / w₀',
       title='Conditional four-atom example (K = 4 eV)')
ax.set_xlim(-.03,2.05);ax.set_ylim(1.46,2.07)
ax.set_xticks(x);ax.grid(alpha=.2);ax.legend(loc='upper left',fontsize=10)
fig.savefig(here/'frontier.svg');fig.savefig(here/'frontier.png',dpi=150)
print('Saved frontier.svg and frontier.png from RESULTS.json; solver calls=0')
