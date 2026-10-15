"""Reproduce local pure-recomb order and high-opacity source survivor diagnostics."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def make(source:Path,dst:Path):
    data=json.loads(source.read_text())
    fig,ax=plt.subplots(figsize=(6.9,4.3))
    for T,style in (('4000.0','-'),('9000.0','--')):
        for method,sym in (('frozen','o'),('midpoint','s')):
            rows=data['RR_independent_DOP853'][T][method]['rows']
            ax.loglog([r['n'] for r in rows],
                      [abs(r['xhi_error']) for r in rows],
                      sym+style,label=f"T0={T} K, {method}")
    ax.set_xlabel('Number of proper time steps')
    ax.set_ylabel('Absolute x_HI error vs independent DOP853')
    ax.set_title('C14: 1st to 2nd order in local H/He recombination')
    ax.grid(which="both",alpha=.3);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(dst/'RR_ORDER.png',dpi=170)
    plt.close(fig)
    src=data['source_toy']['positive_exponential_Duhamel']
    fig,ax=plt.subplots(figsize=(6.9,4.3))
    steps=[r['steps'] for r in src]
    exact=src[0]['exact_constant_coeff_survivor_per_H'][0]
    # Plot smaller upper-limit underflows with safe floor for legibility.
    plotted=[max(r['survivor_midpoint_per_H'][0],1e-35) for r in src]
    ax.semilogx(steps,[exact]*len(steps),'k--',label='exact continuous emission')
    ax.semilogx(steps,[r['survivor_Duhamel_per_H'][0] for r in src],
                'o-',label='positive Duhamel')
    ax.semilogx(steps,plotted,'s-',label='midpoint birth, floor 1e-35')
    ax.set_yscale('log')
    ax.set_xlabel('Time intervals over fixed proper window')
    ax.set_ylabel('Surviving 13.61 eV photons / original H')
    ax.set_title('C14: strong-opacity source birth survivor (frozen gas)')
    ax.legend(fontsize=8);ax.grid(which='both',alpha=.3)
    fig.tight_layout();fig.savefig(dst/'DUHAMEL_SOURCE.png',dpi=170)
    plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('source',type=Path);p.add_argument('destination',type=Path)
    d=p.parse_args();make(d.source,d.destination)
