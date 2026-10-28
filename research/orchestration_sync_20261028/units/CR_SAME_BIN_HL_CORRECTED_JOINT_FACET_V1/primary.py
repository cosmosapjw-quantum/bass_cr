"""Same-bin HL matching cut certificate and corrected joint upper bound."""
import argparse,json,re
from fractions import Fraction as F

def rational(s):
    if not isinstance(s,str) or not re.fullmatch(r'[+-]?\d+(?:/[1-9]\d*)?',s):raise ValueError('exact rational required')
    x=F(s)
    if max(abs(x.numerator).bit_length(),x.denominator.bit_length())>64:raise ValueError('input bit limit')
    return x

def parse(c):
    z=c['atoms'];k=rational(c['K'])
    if len(z)>4 or not z or k<0:raise ValueError('domain size/K')
    if len({a['key'] for a in z})!=len(z):raise ValueError('duplicate key')
    e=[rational(a['E']) for a in z];mass=[rational(a['mass']) for a in z];bins=[a['bin'] for a in z]
    if any(type(b) is not int for b in bins) or min(e+mass)<0:raise ValueError('atom domain')
    return e,mass,bins,k

def cut_match(e,mass,bins,k,same):
    n=len(e);lo=[i for i in range(n) if 2*e[i]<=k];hi=[i for i in range(n) if 2*e[i]>k];N=sum(mass);edges=[(h,l) for h in hi for l in lo if e[h]+e[l]<=k and (not same or bins[h]==bins[l])];cuts=[]
    for mask in range(1<<n):
        source={i for i in range(n) if mask>>i&1};capacity=sum(mass[h] for h in hi if h not in source)+sum(mass[l] for l in lo if l in source)+N*sum(h in source and l not in source for h,l in edges);cuts.append(capacity)
    m=min(cuts);return m,{'cut_count':len(cuts),'mincut_source_masks':[i for i,x in enumerate(cuts) if x==m],'allowed_HL_edges':edges}

def solve(case):
    e,m,b,k=parse(case);N=sum(m);L=sum(x for i,x in enumerate(m) if 2*e[i]<=k);M,mc=cut_match(e,m,b,k,False);S,sc=cut_match(e,m,b,k,True);D=(L+M)/2
    vals=[N,L,M,S,D]
    if any(max(abs(x.numerator).bit_length(),x.denominator.bit_length())>4096 for x in vals):raise ValueError('derived bit limit')
    out={'id':case['id'],'N':str(N),'L':str(L),'M':str(M),'S':str(S),'D':str(D),'all_HL_cut':mc,'same_bin_HL_cut':sc,'upper_bound':'min(D,(L+S+C)/2)','event_lower_per_W':'N-min(D,(L+S+C)/2)','chemical_upper_per_W':'(2459/100)*N+(2983/100)*min(D,(L+S+C)/2)','units':{'N_d_C_L_S_D':'m^-3 s^-2','E_K':'eV','W':'s^2','events':'m^-3','chemical_energy':'eV m^-3'}}
    if case['id'] in ('A','B'):
        d=F(1);C=F(int(b[0]!=b[1]));bound=min(D,(L+S+C)/2)
        out['explicit_witness']={'pair':[0,1],'pair_mass':'1','d':str(d),'C':str(C),'old_facet_excess':str(2*d-C-L),'new_facet_slack':str(L+S+C-2*d),'bound':str(bound),'event_lower_per_W':str(N-bound),'chemical_upper_per_W':str(F(2459,100)*N+F(2983,100)*bound)}
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--output');a=p.parse_args();data=json.load(open(a.input));assert len(data['cases'])<=9
    rows=[solve(c) for c in data['cases']];controls=[]
    for c in data['rejections']:
        try:solve(c)
        except (ValueError,ZeroDivisionError) as e:controls.append({'id':c['id'],'rejected':True,'reason':str(e)})
        else:raise AssertionError('rejection accepted: '+c['id'])
    json.dump({'cases':rows,'rejection_controls':controls,'accepted_count':len(rows),'rejected_count':len(controls)},open(a.output,'w'),indent=2)
if __name__=='__main__':main()
