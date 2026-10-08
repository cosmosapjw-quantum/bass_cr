"""Exact arithmetic on recorded source components, not an ODE certification.

The atomic coefficients are supplied by the pinned native evaluator. Treating
its recorded numbers as Fractions preserves the decomposition, not fit accuracy.
"""
from fractions import Fraction as F

FIELDS = ('h_dt_s','heii_dt_s','heiii_dt_s','w_dt_erg_h_s',
          'electron_dt_per_h_s','temperature_dt_k_s')

class ContractError(ValueError):
    pass

def compose_sources(photo, nonphoto):
    if photo is None or nonphoto is None:
        raise ContractError('BOTH_PHOTO_AND_NONPHOTO_REQUIRED')
    if photo.keys() != nonphoto.keys():
        raise ContractError('SOURCE_KEYS_DIFFER')
    if any(not isinstance(v,F) for v in (*photo.values(),*nonphoto.values())):
        raise ContractError('EXACT_RECORDED_NUMBERS_REQUIRED')
    return {k:photo[k]+nonphoto[k] for k in photo}

def difference(a,b):
    if a.keys()!=b.keys(): raise ContractError('SOURCE_KEYS_DIFFER')
    return {k:b[k]-a[k] for k in a}

def component(s, frac, wdot):
    """EOS maps a three-fraction derivative and energy/H/s to Ce and Tdot."""
    if s['n_h']<=0 or s['n_he']<0 or s['kb_erg_k']<=0 or s['w_erg_h']<=0:
        raise ContractError('GAS_DOMAIN')
    f=s['n_he']/s['n_h']
    D=1+f+s['h']+f*(s['y']+2*s['z'])
    if D<=0: raise ContractError('PARTICLE_DOMAIN')
    ce=frac[0]+f*(frac[1]+2*frac[2])
    temp=F(2,3)/(s['kb_erg_k']*D)*(wdot-s['w_erg_h']*ce/D)
    return dict(zip(FIELDS,(*frac,wdot,ce,temp)))

def photo_vector(projection):
    return {k:projection['heat_erg_h_s' if k=='w_dt_erg_h_s' else k] for k in FIELDS}

def nonphoto_components(s,p):
    """Project actual volumetric event/sink records; do not re-evaluate rates.

    Missing processes are errors, not zeros. Event arrays are HI/HeI/HeII
    ionizations and inverse captures; cooling fields have erg/cm^3/s units.
    """
    nh=s['n_h']; nhe=s['n_he']; zero=F(0)
    def event(r,i,inverse=False):
        if r<0: raise ContractError('NEGATIVE_EVENT')
        out=[zero,zero,zero]
        if i==0: out[0]=r/nh
        else:
            if nhe==0:
                if r!=0: raise ContractError('EVENT_WITHOUT_HELIUM')
            elif i==1: out[1]=r/nhe
            else: out[1]=-r/nhe;out[2]=r/nhe
        return [-x for x in out] if inverse else out
    out={}
    for i in range(3):
        out[f'CI{i}']=component(s,event(p[f'ci{i}'],i),-p[f'ci_sink{i}']/nh)
        out[f'RR{i}']=component(s,event(p[f'rr{i}'],i,True),-p[f'rr_sink{i}']/nh)
        out[f'CE{i}']=component(s,[zero]*3,-p[f'ce_sink{i}']/nh)
    out['DR']=component(s,event(p['dr'],1,True),-p['dr_sink']/nh)
    out['freefree']=component(s,[zero]*3,-p['freefree']/nh)
    out['CMB']=component(s,[zero]*3,p['cmb']/nh)
    out['expansion']=component(s,[zero]*3,-p['work']/nh)
    # RCT: HeIII + HI -> HeII + HII. Direct free-electron increment is zero.
    r=p['rct_rate']; fr=event(r,0)
    if nhe==0:
        if r: raise ContractError('RCT_WITHOUT_HELIUM')
    else: fr[1]=r/nhe;fr[2]=-r/nhe
    out['RCT']=component(s,fr,p['rct_heat']/nh)
    if out['RCT']['electron_dt_per_h_s']!=0:
        raise ArithmeticError('RCT_CHARGE_IDENTITY')
    return out

def sum_components(parts):
    acc={k:F(0) for k in FIELDS}
    for p in parts.values(): acc=compose_sources(acc,p)
    return acc

def four_way_total(photo_threeway, na, nb):
    """Nonphoto is independent of the reader at a fixed matter state.

    Add it once to R12's symmetric reader / spectral-history / matter-state
    decomposition. Returns exact attributions, not causal derivatives.
    """
    delta=difference(na,nb)
    parts={k:dict(v) for k,v in photo_threeway.items() if k!='total'}
    parts['nonphoto_state']=delta
    total={k:F(0) for k in delta}
    for row in parts.values(): total=compose_sources(total,row)
    expected=compose_sources(photo_threeway['total'],delta)
    if total!=expected: raise ArithmeticError('TOTAL_SOURCE_DECOMPOSITION')
    return {'terms':parts,'total':total}


def photo_input_vector(s, gamma, heat_per_absorber):
    """Exact interpretation of the rounded native photo inputs; no rate calls."""
    if len(gamma)!=3 or len(heat_per_absorber)!=3:
        raise ContractError('THREE_ABSORBERS_REQUIRED')
    if any(g<0 or h<0 or (g==0 and h!=0) for g,h in zip(gamma,heat_per_absorber)):
        raise ContractError('PHOTO_INPUT_DOMAIN')
    h,y,z=s['h'],s['y'],s['z'];f=s['n_he']/s['n_h']
    fr=[(1-h)*gamma[0], (1-y-z)*gamma[1]-y*gamma[2],y*gamma[2]]
    nu=[1-h,f*(1-y-z),f*y]
    heat=sum((n*v for n,v in zip(nu,heat_per_absorber)),F(0))
    return component(s,fr,heat)


def cmb_temperature_secant(sa, sb, tcmb, prefactor):
    """Exact finite difference of K*Tcmb^4*(Xe/D)*(Tcmb-T).

    K is the caller-supplied source coefficient 2*A_C/(3*kB). Matched density,
    nuclear ratio and constants are required. No atomic data or model is chosen.
    """
    for key in ('n_h','n_he','kb_erg_k'):
        if sa[key]!=sb[key]: raise ContractError('CMB_BACKGROUND_MISMATCH')
    if tcmb<=0 or prefactor<0: raise ContractError('CMB_DOMAIN')
    f=sa['n_he']/sa['n_h']
    def values(s):
        xe=s['h']+f*(s['y']+2*s['z']); D=1+f+xe
        if D<=0: raise ContractError('PARTICLE_DOMAIN')
        return xe,D,F(2,3)*s['w_erg_h']/s['kb_erg_k']/D
    xa,da,ta=values(sa);xb,db,tb=values(sb)
    ra,rb=xa/da,xb/db
    dr=(1+f)*(xb-xa)/(da*db)
    rate=prefactor*tcmb**4
    electron=rate*(tcmb-(ta+tb)/2)*dr
    thermal=-rate*(ra+rb)/2*(tb-ta)
    total=rate*(rb*(tcmb-tb)-ra*(tcmb-ta))
    if electron+thermal!=total: raise ArithmeticError('CMB_SECANT_IDENTITY')
    return dict(electron_share=electron,temperature=thermal,total=total,
                delta_Xe=xb-xa,delta_T=tb-ta)
