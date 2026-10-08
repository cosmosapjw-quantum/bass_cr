"""H5 report's G(p)=C p^-2 radial dp measure; no actual state is manufactured."""
from .core import ContractError,nonnegative

def powerlaw_p_minus2_weights(edges):
    """Exact probability masses on supplied momentum bins.

    G(p)=integral p^2 f(p,Omega)dOmega and integral G dp=n_CR. The
    returned normalized masses sum to one; n_CR is multiplied exactly once by
    a downstream rate. These bin masses are NOT a certified quadrature of an
    energy-dependent rate, and do not pin the H5 state bytes or energy mapping.
    """
    if not isinstance(edges,(list,tuple)) or len(edges)<2:raise ContractError('at least two momentum edges required')
    p=tuple(map(nonnegative,edges))
    if p[0]==0 or any(a>=b for a,b in zip(p,p[1:])):raise ContractError('positive ordered momentum edges required')
    norm=1/p[0]-1/p[-1]
    return tuple((1/a-1/b)/norm for a,b in zip(p,p[1:]))
