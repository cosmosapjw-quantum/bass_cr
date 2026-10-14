import importlib.util
import math
import unittest
from fractions import Fraction as F
from pathlib import Path

spec=importlib.util.spec_from_file_location('tail_analysis',Path(__file__).resolve().parents[1]/'src/tail_analysis.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def exact(points,T):
    p=sum(w for t,w in points if t<=T)
    R=sum(w*max(F(0),1-t/T) for t,w in points)
    S=sum(w*max(F(0),1-t/T)**2 for t,w in points)
    mu=sum(t*w for t,w in points); m2=sum(t*t*w for t,w in points)
    return p,R,S,mu,m2


class ScalarTests(unittest.TestCase):
    def test_fraction_oracle(self):
        points=[(F(1),F(1,4)),(F(3),F(1,4)),(F(7),F(1,2))]; T=F(4)
        args=exact(points,T); a=m.analyze_scalar(1,*map(float,args),float(T))
        for name,subset in [('early',[(t,w) for t,w in points if t<=T]),('tail',[(t,w) for t,w in points if t>T]),('tail_residual',[(t-T,w) for t,w in points if t>T])]:
            q=sum(w for t,w in subset); first=sum(t*w for t,w in subset); second=sum(t*t*w for t,w in subset)
            for key,value in [('probability',q),('raw_m1_s',first),('raw_m2_s2',second),('mean_s',first/q),('second_s2',second/q),('variance_s2',second/q-(first/q)**2)]:
                self.assertAlmostEqual(a[name][key],float(value),places=12)
        self.assertTrue(all(x['pass_check'] for x in m.compare_decimal(a,m.decimal_scalar(1,*map(float,args),float(T)),float(T)).values()))

    def test_fraction_mixture(self):
        # Exact finite measures with different birth yield and both partitions occupied.
        points1=[(F(1),F(1,2)),(F(6),F(1,2))]; points2=[(F(2),F(1,4)),(F(8),F(3,4))]; T=F(4)
        c=[m.analyze_scalar(float(h),*map(float,exact(points,T)),float(T)) for h,points in [(F(2),points1),(F(3),points2)]]
        pooled=[(t,w*F(2,5)) for t,w in points1]+[(t,w*F(3,5)) for t,w in points2]
        s=m.analyze_scalar(5,*map(float,exact(pooled,T)),float(T)); mix=m.mixture(c,s,float(T))
        expected={'eventual':F(2,5),'early':F(4,7),'tail':F(4,13),'mean_share':F(14,53)}
        for key,value in expected.items(): self.assertAlmostEqual(mix['weights'][0][key]['value'],float(value),places=12)
        mu=sum(t*w for t,w in pooled); variance=sum(w*(t-mu)**2 for t,w in pooled)
        self.assertAlmostEqual(s['total']['variance_s2'],float(variance),places=12)
        self.assertTrue(all(v['pass_check'] for v in mix['checks'].values()))

    def test_degenerate_zero_events(self):
        for points,name in [([(F(1),F(1))],'tail'), ([(F(6),F(1))],'early')]:
            args=exact(points,F(4)); a=m.analyze_scalar(1,*map(float,args),4)
            self.assertEqual(a[name]['status'],m.UNDEFINED); self.assertIsNone(a[name]['mean_s'])
        self.assertEqual(m.analyze_scalar(0,0,0,0,0,0,4)['status'],'UNDEFINED_ZERO_YIELD')
        a=m.analyze_scalar(1,1,.75,.5625,1,1-1e-14,4)
        self.assertLess(a['total']['variance_s2'],0); self.assertIsNone(a['total']['std_s']); self.assertEqual(a['total']['issue'],'NEGATIVE_VARIANCE_RETAINED')

    def test_malformed(self):
        good=[1,.5,.25,.125,3.5,18.5,4]
        for index,value in [(0,-1),(0,float('nan')),(1,1.1),(2,.8),(3,.8),(4,-1),(5,1),(6,0),(6,float('inf'))]:
            bad=good.copy(); bad[index]=value
            with self.assertRaises(ValueError): m.analyze_scalar(*bad)
        with self.assertRaises(ValueError): m.analyze_scalar(1,0,0,0,1,1,4)


if __name__=='__main__': unittest.main()
