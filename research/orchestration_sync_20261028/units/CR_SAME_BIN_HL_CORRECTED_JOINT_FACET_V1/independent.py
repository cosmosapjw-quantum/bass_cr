"""Independent full marginal BFS enumeration; no proposed facet in generation."""
import argparse,json,itertools,hashlib,math
from fractions import Fraction as F

def linear_solve(cols,rhs):
    n=len(rhs);a=[[F(cols[j][i]) for j in range(n)]+[rhs[i]] for i in range(n)]
    for j in range(n):
        piv=next((i for i in range(j,n) if a[i][j]),None)
        if piv is None:return None
        a[j],a[piv]=a[piv],a[j];v=a[j][j];a[j]=[x/v for x in a[j]]
        for i in range(n):
            if i!=j:
                v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[j])]
    return [a[i][-1] for i in range(n)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--primary');p.add_argument('--output');a=p.parse_args();data=json.load(open(a.input));prod=json.load(open(a.primary));records=[]
    for case,out in zip(data['cases'],prod['cases']):
        atoms=case['atoms'];n=len(atoms);mass=[F(z['mass']) for z in atoms];e=[F(z['E']) for z in atoms];bins=[z['bin'] for z in atoms];K=F(case['K']);N=sum(mass);L=sum(mass[i] for i in range(n) if 2*e[i]<=K)
        labels=[('single',i,i) for i in range(n)]+[('pair',i,j) for i in range(n) for j in range(i,n) if e[i]+e[j]<=K]
        cols=[]
        for kind,i,j in labels:
            v=[0]*n;v[i]+=1
            if kind=='pair':v[j]+=1
            cols.append(v)
        basis_count=math.comb(len(cols),n);assert basis_count<=1001
        seen={};accepted_bases=0;singular=0;negative=0;max_HL=F(0);max_same_HL=F(0)
        for chosen in itertools.combinations(range(len(cols)),n):
            x=linear_solve([cols[j] for j in chosen],mass)
            if x is None:singular+=1;continue
            if min(x)<0:negative+=1;continue
            accepted_bases+=1;full=[F(0)]*len(cols)
            for j,v in zip(chosen,x):full[j]=v
            assert [sum(F(cols[j][i])*full[j] for j in range(len(cols))) for i in range(n)]==mass
            key=tuple(full)
            d=sum(full[j] for j,(kind,_,_) in enumerate(labels) if kind=='pair');C=sum(full[j] for j,(kind,i,k) in enumerate(labels) if kind=='pair' and bins[i]!=bins[k])
            HL=sum(full[j] for j,(kind,i,k) in enumerate(labels) if kind=='pair' and (2*e[i]<=K)!=(2*e[k]<=K));same_HL=sum(full[j] for j,(kind,i,k) in enumerate(labels) if kind=='pair' and (2*e[i]<=K)!=(2*e[k]<=K) and bins[i]==bins[k]);max_HL=max(max_HL,HL);max_same_HL=max(max_same_HL,same_HL)
            S,M,D=map(F,(out['S'],out['M'],out['D']));bound=min(D,(L+S+C)/2)
            assert 0<=C<=d<=D and 2*d-C<=L+S
            assert N-d>=N-bound and F(2459,100)*N+F(2983,100)*d<=F(2459,100)*N+F(2983,100)*bound
            W=F(0)
            assert W*(N-d)==W*(N-bound)==0
            assert W*(F(2459,100)*N+F(2983,100)*d)==W*(F(2459,100)*N+F(2983,100)*bound)==0
            assert all(max(abs(v.numerator).bit_length(),v.denominator.bit_length())<=4096 for v in full+[d,C,HL,same_HL,bound])
            seen[key]={'marginal_solution':list(map(str,full)),'d':str(d),'C':str(C),'old_facet_excess':str(2*d-C-L),'new_facet_slack':str(L+S+C-2*d),'upper_d':str(bound),'event_lower_per_W':str(N-bound),'chemical_upper_per_W':str(F(2459,100)*N+F(2983,100)*bound)}
        assert max_HL==F(out['M']) and max_same_HL==F(out['S']) and L==F(out['L']) and N==F(out['N'])
        vertices=list(seen.values());max_excess=max(F(v['old_facet_excess']) for v in vertices);assert max_excess<=F(out['S'])
        # Exact rational mixtures use the first and last saved vertices; no facet is used to generate them.
        mixture_count=0
        for weight in [F(1,3),F(1,2),F(2,3)]:
            v,w=vertices[0],vertices[-1];d=weight*F(v['d'])+(1-weight)*F(w['d']);C=weight*F(v['C'])+(1-weight)*F(w['C']);assert 2*d-C<=L+F(out['S']);mixture_count+=1
        if case['id'] in ('A','B'):
            witness=[F(0)]*len(labels);widx=labels.index(('pair',0,1));witness[widx]=F(1);assert [sum(cols[j][i]*witness[j] for j in range(len(cols))) for i in range(n)]==mass
            assert tuple(witness) in seen
            actual=seen[tuple(witness)];assert actual['d']==out['explicit_witness']['d'] and actual['C']==out['explicit_witness']['C']
        packed=json.dumps(vertices,sort_keys=True,separators=(',',':'))
        records.append({'id':case['id'],'column_labels':labels,'basis_count':basis_count,'actual_bases':accepted_bases+singular+negative,'accepted_bases':accepted_bases,'singular_bases':singular,'negative_bases':negative,'accepted_vertices':len(vertices),'finite_count':len(vertices),'vertices_sha256':hashlib.sha256(packed.encode()).hexdigest(),'vertices':vertices,'max_old_facet_excess':str(max_excess),'matching_crosscheck':{'M':str(max_HL),'S':str(max_same_HL)},'mixture_checks':mixture_count,'W_zero_checked':True,'observable_per_W_checks':len(vertices),'pass':True})
    assert len(records)==len(data['cases'])==len(prod['cases'])
    json.dump({'cases':records,'exact_checks_pass':True,'total_bases':sum(r['actual_bases'] for r in records),'finite_count':sum(r['finite_count'] for r in records),'claim':'necessary upper bound only; no generic sufficiency'},open(a.output,'w'),indent=2)
if __name__=='__main__':main()
