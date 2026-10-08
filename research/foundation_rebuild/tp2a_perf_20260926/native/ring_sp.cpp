// Same s+p polynomial values and weak gradients as the NumPy path.
// C ABI uses interleaved real/imaginary doubles, not std::complex ABI.
// No OpenMP, fast-math, global mutable state, Python API or hidden allocation.
#include <cmath>
#include <cstddef>

extern "C" int bass_ring_sp_v1(std::size_t nr, std::size_t nf, std::size_t nc,
    const double* xyz, const double* a, const double* ar,
    const double* coeff, const double* vel,
    double* B, double* G, double* D) noexcept {
    if (!nr || !nf || !nc || !xyz || !a || !ar || !coeff || !vel || !B || !G || !D) return 1;
    const std::size_t block=nr*nf*nc;
    const double v2=vel[0]*vel[0]+vel[1]*vel[1]+vel[2]*vel[2];
    for (std::size_t r=0;r<nr;++r) for(std::size_t f=0;f<nf;++f) {
        const auto p=r*nf+f; const double* x=xyz+3*p;
        for(std::size_t c=0;c<nc;++c) {
            const double* q=coeff+8*c;
            double sr=q[0],si=q[1];
            for(int j=0;j<3;++j){sr+=q[2+2*j]*x[j];si+=q[3+2*j]*x[j];}
            const double av=a[r*nc+c],drv=ar[r*nc+c];
            const double fr=av*sr,fi=av*si;
            const std::size_t k=p*nc+c;
            B[2*k]=fr;B[2*k+1]=fi;
            double dr=0,di=0;
            for(int j=0;j<3;++j){
                const double gr=av*q[2+2*j]+drv*sr*x[j];
                const double gi=av*q[3+2*j]+drv*si*x[j];
                dr-=vel[j]*gr;di-=vel[j]*gi;
                G[2*(j*block+k)]=gr-vel[j]*fi;
                G[2*(j*block+k)+1]=gi+vel[j]*fr;
            }
            D[2*k]=dr+0.5*v2*fi;D[2*k+1]=di-0.5*v2*fr;
        }
    }
    return 0;
}
