"""Independent Edmonds-Karp oracle + adversarial threshold fixtures.
The oracle has no imports of the production capacity solver inside its flow routine.
"""
import sys,unittest,random
from pathlib import Path
from fractions import Fraction as F
from collections import deque,defaultdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from samebin_capacity import Atom,solve,bounds

def independent_flow(rows,cap,within_same_bin=True):
    # Build the entire positive-mass bipartite network with no Ferrers logic.
    # Node labels deliberately do not share production grouping or ordering.
    lows=[(i,a) for i,a in enumerate(rows) if a.coefficient>0 and 2*a.energy_eV<=cap]
    highs=[(i,a) for i,a in enumerate(rows) if a.coefficient>0 and 2*a.energy_eV>cap]
    graph=defaultdict(dict); src='s';sink='t'
    def edge(u,v,c):
        graph[u][v]=graph[u].get(v,F(0))+c
        graph[v].setdefault(u,F(0))
    infinity=sum((x.coefficient for x in rows),F(0))+1
    for i,h in highs:
        u=('h',i);edge(src,u,h.coefficient)
        for j,l in lows:
            if h.energy_eV+l.energy_eV<=cap and (not within_same_bin or h.partition==l.partition):
                edge(u,('l',j),infinity)
    for j,l in lows:edge(('l',j),l.coefficient)
    total=F(0)
    while True:
        par={src:None};q=deque([src])
        while q and sink not in par:
            u=q.popleft()
            for v,c in graph[u].items():
                if c>0 and v not in par:
                    par[v]=u;q.append(v)
        if sink not in par:break
        v=sink;step=None
        while v!=src:
            u=par[v]; step=graph[u][v] if step is None else min(step,graph[u][v]);v=u
        v=sink
        while v!=src:
            u=par[v];graph[u][v]-=step;graph[v][u]+=step
        total+=step
    return total

class Tests(unittest.TestCase):
    def row(self,k,e,c,b):return Atom(str(k),F(e),F(c),b)
    def test_same_bin_counterexample(self):
        a=[self.row('low',0,1,0),self.row('high',3,1,0)]
        t=solve(a,4)
        self.assertEqual(t['S'],1)
        self.assertEqual(bounds(a,4,0)['d_max_necessary'],1)
        self.assertEqual(2*1-0,1+1)
    def test_cross_only_old_S_zero(self):
        a=[self.row('low',0,1,0),self.row('high',3,1,1)]
        self.assertEqual(solve(a,4)['S'],0)
        self.assertEqual(solve(a,4,False)['S'],1)
        self.assertEqual(bounds(a,4,1)['d_max_necessary'],1)
    def test_weighted_hall_deficiency(self):
        a=[self.row('h9',9,2,0),self.row('h8',8,2,0),
           self.row('l0',0,1,0),self.row('l1',1,1,0)]
        v=solve(a,10)
        self.assertEqual(v['S'],2)
        self.assertEqual(v['group_certs'][0]['deficiency'],2)
        self.assertEqual(v['dual'],independent_flow(a,F(10)))
    def test_rational_exactness(self):
        a=[self.row('h1',F(7,2),F(1,7),0),self.row('h2',F(9,2),F(3,13),0),
           self.row('l1',0,F(1,3),0)]
        self.assertEqual(solve(a,5)['S'],F(1,3))
    def test_boundary_2E_equal_K_is_low(self):
        a=[self.row('eq',2,1,0),self.row('h',3,1,0)]
        self.assertEqual(solve(a,4)['S'],0)
        self.assertEqual(solve(a,5)['S'],1)
    def test_float_refusal(self):
        with self.assertRaises(TypeError):Atom.parse(dict(key='x',energy_eV=1.0,coefficient='1',partition=0))
    def test_direct_constructor_exact_guard(self):
        with self.assertRaises(TypeError):Atom('x',0.25,F(1),0)
        with self.assertRaises(TypeError):Atom('x',F(1),0.25,0)
    def test_duplicate_refusal(self):
        a=[self.row('same',0,1,0),self.row('same',4,1,0)]
        with self.assertRaises(ValueError):solve(a,5)
    def test_negative_and_label_refusal(self):
        with self.assertRaises(ValueError):self.row('x',-1,2,0)
        with self.assertRaises(ValueError):self.row('x',0,-2,0)
        with self.assertRaises(ValueError):self.row('x',0,1,-1)
    def test_zero_masses(self):
        a=[self.row('l',0,0,0),self.row('h',3,0,0)]
        self.assertEqual(solve(a,4)['S'],0)
    def test_random_flow_oracle(self):
        rg=random.Random(20261029)
        seen=0;nonzero=0;different=0
        for n in range(1,11):
            for t in range(23):
                a=[self.row('atom%02d'%i,F(rg.randint(0,16),2),F(rg.randint(0,7),rg.randint(1,9)),rg.randrange(3)) for i in range(n)]
                K=F(rg.randint(0,20),2)
                for within in (True,False):
                    got=solve(a,K,within)
                    ref=independent_flow(a,K,within)
                    self.assertEqual((got['S'],got['dual']),(ref,ref),msg=(n,t,within))
                    self.assertEqual(sum((v for _,_,v in got['pairs']),F(0)),ref)
                    seen+=1
                    nonzero+=int(ref>0)
                if solve(a,K,False)['S']!=solve(a,K,True)['S']:different+=1
        self.assertEqual(seen,460)
        self.assertGreater(nonzero,0)
        self.assertGreater(different,0)

if __name__=='__main__':unittest.main(verbosity=2)
