"""Source-bound FT03 formal algebra; no coefficient evaluation or time solver.

The coefficient functions are symbolic placeholders with the source's units.
They are not mock providers and are never passed to a native consumer.
"""
import sympy as s


def build():
    x=s.Matrix(s.symbols('x_H x_HeII x_HeIII', real=True))
    t=s.Symbol('T',positive=True)
    nh,nhe,c,kb,ev,h=s.symbols('nH nHe c kB ev h',positive=True)
    old_x=s.Matrix(s.symbols('x0_H x0_HeII x0_HeIII',real=True))
    old_u=s.Symbol('u0',nonnegative=True)
    old_n=s.Matrix(s.symbols('N0_0:3',nonnegative=True))
    native_n=s.Matrix(s.symbols('Nhat_0:3',nonnegative=True))
    chi=s.Matrix(s.symbols('chi0:3',positive=True))
    energy=s.Matrix(s.symbols('E0:3',positive=True))
    sigma=s.Matrix(3,3,lambda a,g:s.Symbol(f'sigma{a}{g}',nonnegative=True))
    lower=s.Matrix([1-x[0],1-x[1]-x[2],x[1]])
    nuclei=s.Matrix([nh,nhe,nhe])
    electron=nh*x[0]+nhe*(x[1]+2*x[2])
    particles=nh+nhe+electron
    u=s.Rational(3,2)*kb*particles*t
    alpha=s.Matrix([s.Function(f'alpha{a}')(t) for a in range(3)])
    beta=s.Matrix([s.Function(f'beta{a}')(t) for a in range(3)])
    kinetic=s.Matrix([s.Function(f'LambdaRR{a}')(t) for a in range(3)])
    dr=s.Matrix([s.Function(f'alphaDR{k}')(t) for k in range(2)])
    dr_energy=s.Matrix(s.symbols('epsilonDR0:2',positive=True))
    opacity=s.Matrix([sum(nuclei[a]*lower[a]*c*sigma[a,g] for a in range(3)) for g in range(3)])
    denom=s.Matrix([1+h*opacity[g] for g in range(3)])
    eliminated=s.Matrix([old_n[g]/denom[g] for g in range(3)])
    combine=s.Matrix([[1,0,0],[0,1,-1],[0,0,1]])

    def rhs(photons):
        photo=s.Matrix(3,3,lambda a,g:nuclei[a]*lower[a]*c*sigma[a,g]*photons[g])
        collision=s.Matrix([nuclei[a]*lower[a]*electron*beta[a] for a in range(3)])
        rr=s.Matrix([nuclei[a]*x[a]*electron*alpha[a] for a in range(3)])
        dielectronic=s.Matrix([nhe*x[1]*electron*dr[k] for k in range(2)])
        per_capita=s.Matrix([lower[a]*(sum(c*sigma[a,g]*photons[g] for g in range(3))+electron*beta[a])-x[a]*electron*alpha[a] for a in range(3)])
        per_capita[1]-=x[1]*electron*sum(dr)
        fractions=combine*per_capita
        heat=sum(photo[a,g]*(energy[g]-chi[a])*ev for a in range(3) for g in range(3))
        thermal=heat-sum(collision[a]*chi[a]*ev+nuclei[a]*x[a]*electron*kinetic[a] for a in range(3))-sum(dielectronic[k]*dr_energy[k] for k in range(2))
        escape=sum(rr[a]*chi[a]*ev+nuclei[a]*x[a]*electron*kinetic[a] for a in range(3))+sum(dielectronic[k]*(chi[1]*ev+dr_energy[k]) for k in range(2))
        photon=s.Matrix([-sum(photo[a,g] for a in range(3)) for g in range(3)])
        return dict(fractions=fractions,thermal=thermal,escape=escape,photon=photon,photo=photo,collision=collision,rr=rr,dr=dielectronic)

    reduced_rhs=rhs(eliminated);stored_rhs=rhs(native_n)
    reduced=s.Matrix(list(x-old_x-h*reduced_rhs['fractions'])+[u-old_u-h*reduced_rhs['thermal']])
    direct=s.Matrix(list(x-old_x-h*stored_rhs['fractions'])+[u-old_u-h*stored_rhs['thermal']])
    photon_residual=s.Matrix([denom[g]*native_n[g]-old_n[g] for g in range(3)])
    m=combine*s.Matrix(3,3,lambda a,g:lower[a]*c*sigma[a,g])
    heat_row=s.Matrix(1,3,lambda _,g:sum(nuclei[a]*lower[a]*c*sigma[a,g]*(energy[g]-chi[a])*ev for a in range(3)))
    coupling=m.col_join(heat_row)
    return locals()


def chain_jacobian(q):
    """Independent chain form: explicit population + EOS/rate + photon terms."""
    v=s.Matrix(s.symbols('V0:3',nonnegative=True))
    rates=q['rhs'](v)
    out=s.zeros(4,4)
    z=list(q['x'])+[q['t']]
    f=s.Matrix(list(rates['fractions'])+[rates['thermal']])
    u=q['u']
    for i in range(4):
        for j in range(4):
            baseline=(s.Integer(i==j) if i<3 else s.diff(u,z[j]))
            fixed=s.diff(f[i],z[j]).subs(dict(zip(v,q['eliminated'])))
            photon=sum(s.diff(f[i],v[g])*s.diff(q['eliminated'][g],z[j]) for g in range(3))
            out[i,j]=baseline-q['h']*(fixed+photon)
    return out
