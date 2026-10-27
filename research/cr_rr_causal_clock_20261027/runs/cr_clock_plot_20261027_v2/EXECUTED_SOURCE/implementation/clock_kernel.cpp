// CR_RR_CAUSAL_ERLANG_CLOCK_V1: FP64 solves, exact-target residual bounds.
// No entry point loads files, launches workers, rebuilds K, or changes fenv.
#ifndef CR_STRICT_BUILD
#error "Build requires -DCR_STRICT_BUILD=1 and the reviewed strict FP flags."
#endif
#ifndef CR_LAPACK_LP64
#error "Build requires -DCR_LAPACK_LP64=1 and GNU LP64 LAPACK."
#endif
#if defined(__FAST_MATH__) || (defined(__FINITE_MATH_ONLY__) && __FINITE_MATH_ONLY__ > 0)
#error "Fast math is forbidden."
#endif
#if !defined(__x86_64__) || !defined(__GNUC__)
#error "This arithmetic qualification targets GNU x86_64 only."
#endif

#include <algorithm>
#include <array>
#include <cfenv>
#include <cfloat>
#include <cmath>
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
#include <xmmintrin.h>

extern "C" {
void dgttrf_(const int*, double*, double*, double*, double*, int*, int*);
void dgttrs_(const char*, const int*, const int*, const double*, const double*,
             const double*, const double*, const int*, double*, const int*,
             int*, std::size_t);
}

namespace {
using LD = long double;
constexpr int RHS = 2, MAX_N = 20000, MAX_SOURCE = 16, MAX_M = 8192;
constexpr LD LEPS = std::numeric_limits<LD>::epsilon();
constexpr LD SHORT_G = 64 * LEPS;
const LD LINF = std::numeric_limits<LD>::infinity();

void need(bool ok, const char* text) {
    if (!ok) throw std::runtime_error(text);
}
void finite_ld(LD x) { need(std::isfinite(x), "NONFINITE_LONG_DOUBLE_BOUND"); }
LD up(LD x) {
    finite_ld(x);
    if (x == 0) return 0;
    const LD y = std::nextafterl(x, LINF);
    finite_ld(y);
    return y;
}
LD down(LD x) {
    finite_ld(x);
    if (x == 0) return 0;
    const LD y = std::nextafterl(x, -LINF);
    finite_ld(y);
    return y;
}
LD uadd(LD x, LD y) {
    need(x >= 0 && y >= 0, "NEGATIVE_ERROR_SUM_INPUT");
    return up(x + y);
}
LD umul(LD x, LD y) {
    need(x >= 0 && y >= 0, "NEGATIVE_ERROR_PRODUCT_INPUT");
    if (x == 0 || y == 0) return 0;
    const LD q = x * y;
    // Positive exact products can underflow during a long error recurrence.
    if (q == 0) return std::nextafterl(0.0L, LINF);
    return up(q);
}
LD udiv(LD x, LD y) {
    need(x >= 0 && y > 0, "INVALID_ERROR_DIVISION");
    if (x == 0) return 0;
    const LD q = x / y;
    if (q == 0) return std::nextafterl(0.0L, LINF);
    return up(q);
}
double round_nearest(LD x) {
    finite_ld(x);
    const double y = static_cast<double>(x);
    need(std::isfinite(y), "BINARY64_OUTPUT_OVERFLOW");
    return y;
}
double out_up(LD x) {
    double y = round_nearest(x);
    if (static_cast<LD>(y) < x) y = std::nextafter(y, INFINITY);
    need(std::isfinite(y), "BINARY64_UPPER_OVERFLOW");
    return y;
}
double out_down(LD x) {
    double y = round_nearest(x);
    if (static_cast<LD>(y) > x) y = std::nextafter(y, -INFINITY);
    need(std::isfinite(y), "BINARY64_LOWER_OVERFLOW");
    return y;
}

void environment() {
    static_assert(sizeof(int) == 4, "LP64 LAPACK int required");
    static_assert(sizeof(double) == 8, "binary64 required");
    need(std::numeric_limits<double>::radix == 2 &&
         std::numeric_limits<double>::digits == 53 &&
         std::numeric_limits<double>::is_iec559, "BINARY64_PLATFORM_REQUIRED");
    need(std::numeric_limits<LD>::radix == 2 &&
         std::numeric_limits<LD>::digits == 64 &&
         std::numeric_limits<LD>::max_exponent >= 16384 &&
         std::numeric_limits<LD>::min_exponent <= -16381,
         "X87_EXTENDED_PLATFORM_REQUIRED");
    need(std::fegetround() == FE_TONEAREST, "ROUND_TO_NEAREST_REQUIRED");
    unsigned short cw = 0;
    __asm__ __volatile__("fnstcw %0" : "=m"(cw));
    need((cw & 0x0300u) == 0x0300u && (cw & 0x0c00u) == 0,
         "X87_EXTENDED_NEAREST_REQUIRED");
    const unsigned csr = _mm_getcsr();
    need((csr & ((1u << 15) | (1u << 6) | (3u << 13))) == 0,
         "SSE_NEAREST_GRADUAL_UNDERFLOW_REQUIRED");
}

void sizes(int n, int ns) {
    need(n >= 1 && n <= MAX_N, "UNSUPPORTED_N");
    need(ns >= 1 && ns <= MAX_SOURCE, "UNSUPPORTED_SOURCE_COUNT");
}
void inputs(int n, int ns, const double* d, const double* l, const double* u,
            const double* r, const double* h, const double* w) {
    sizes(n, ns);
    need(d && r && h && w && (n == 1 || (l && u)), "NULL_INPUT");
    for (int i = 0; i < n; ++i) {
        need(std::isfinite(d[i]) && d[i] > 0, "INVALID_DIAGONAL");
        need(std::isfinite(h[i]) && h[i] > 0, "INVALID_WITNESS");
        for (int k = 0; k < RHS; ++k)
            need(std::isfinite(r[k*n+i]) && r[k*n+i] >= 0,
                 "NONNEGATIVE_FINITE_REWARD_REQUIRED");
    }
    for (int i = 0; i < n-1; ++i)
        need(std::isfinite(l[i]) && std::isfinite(u[i]) &&
             l[i] <= 0 && u[i] <= 0, "Z_MATRIX_REQUIRED");
    for (int s = 0; s < ns; ++s)
        for (int i = 0; i < n; ++i)
            need(std::isfinite(w[s*n+i]) && w[s*n+i] >= 0,
                 "NONNEGATIVE_FINITE_SOURCE_REQUIRED");
}

// Generic n-term dot of exact encoded operands, <=2n operations.
// Error <= 4(n+1)*LEPS*sumabs, including rounding in sumabs.
struct Dot { LD value, error; };
template<class X, class Y>
Dot dot(int n, X x, Y y) {
    LD value = 0, sa = 0;
    for (int i = 0; i < n; ++i) {
        const LD p = static_cast<LD>(x(i)) * static_cast<LD>(y(i));
        value += p;
        sa += std::fabs(p);
    }
    finite_ld(value);
    finite_ld(sa);
    const LD margin = 4 * static_cast<LD>(n + 1) * LEPS;
    need(margin < 0.0001L, "DOT_OPERATION_COUNT_UNSUPPORTED");
    return {value, umul(margin, sa)};
}

LD witness_beta(int n, const double* d, const double* l, const double* u,
                const double* h) {
    LD beta = LINF;
    for (int i = 0; i < n; ++i) {
        LD v = static_cast<LD>(d[i]) * h[i];
        LD sa = std::fabs(v);
        if (i > 0) {
            const LD p = static_cast<LD>(l[i-1]) * h[i-1];
            v += p; sa += std::fabs(p);
        }
        if (i+1 < n) {
            const LD p = static_cast<LD>(u[i]) * h[i+1];
            v += p; sa += std::fabs(p);
        }
        const LD lo = down(v - umul(SHORT_G, sa));
        need(lo > 0, "POSITIVE_WITNESS_NOT_CERTIFIED");
        const LD b = down(lo / static_cast<LD>(h[i]));
        need(b > 0, "POSITIVE_BETA_NOT_CERTIFIED");
        beta = std::min(beta, b);
    }
    return beta;
}

std::vector<LD> inverse_witness(int n, const double* h) {
    std::vector<LD> inv(n);
    for (int i = 0; i < n; ++i) inv[i] = udiv(1, static_cast<LD>(h[i]));
    return inv;
}

// rho = b - K*x - gamma*x. If recurrent, b=gamma*previous EXACTLY;
// solver RHS formation and diagonal-addition rounding are thereby included.
LD residual_norm(int n, const double* d, const double* l, const double* u,
                 const double* rhs_or_previous, const double* x,
                 const std::vector<LD>& invh, double gamma, bool recurrent) {
    LD largest = 0;
    for (int i = 0; i < n; ++i) {
        const LD first = recurrent
            ? static_cast<LD>(gamma) * rhs_or_previous[i]
            : static_cast<LD>(rhs_or_previous[i]);
        LD v = first, sa = std::fabs(first);
        LD p = static_cast<LD>(d[i]) * x[i];
        v -= p; sa += std::fabs(p);
        p = static_cast<LD>(gamma) * x[i];
        v -= p; sa += std::fabs(p);
        if (i > 0) {
            p = static_cast<LD>(l[i-1]) * x[i-1];
            v -= p; sa += std::fabs(p);
        }
        if (i+1 < n) {
            p = static_cast<LD>(u[i]) * x[i+1];
            v -= p; sa += std::fabs(p);
        }
        if (sa == 0) continue;  // all exact product terms are zero
        // <=9 short-dot operations. |rho-v| < 6*LEPS*sa.
        // Four positive rounding operations are covered by (1+64*LEPS).
        const LD b = ((std::fabs(v) + SHORT_G * sa) * invh[i])
                      * (1 + SHORT_G);
        need(std::isfinite(b) && b > 0 && std::fpclassify(b) != FP_SUBNORMAL,
             "RESIDUAL_BOUND_RANGE_UNSUPPORTED");
        largest = std::max(largest, b);
    }
    return up(largest);
}

void scalar_interval(LD value, LD error, double& nominal, double& lo,
                     double& hi, double& radius) {
    need(error >= 0, "NEGATIVE_RADIUS");
    nominal = round_nearest(value);
    const LD cast_error = std::fabs(static_cast<LD>(nominal) - value);
    radius = out_up(uadd(error, cast_error));
    const LD lower = down(value - error), upper = up(value + error);
    need(upper >= 0, "NEGATIVE_CERTIFIED_UPPER");
    lo = std::max(0.0, out_down(lower));
    hi = out_up(upper);
    need(lo <= hi, "EMPTY_NONNEGATIVE_INTERVAL");
}

void message(char* out, std::size_t size, const char* s) {
    if (out && size) std::snprintf(out, size, "%s", s);
}
template<class F>
int guarded(char* out, std::size_t size, F f) {
    try { environment(); f(); message(out, size, "OK"); return 0; }
    catch (const std::exception& e) { message(out, size, e.what()); return 1; }
    catch (...) { message(out, size, "UNKNOWN_NATIVE_ERROR"); return 2; }
}
} // namespace

extern "C" int cr_native_info(int* out, char* msg, std::size_t cap) {
    return guarded(msg, cap, [&] {
        need(out, "NULL_INFO_OUTPUT");
        const int data[10] = {1, int(sizeof(double)), int(sizeof(LD)),
            std::numeric_limits<LD>::digits,
            std::numeric_limits<LD>::max_exponent,
            std::numeric_limits<LD>::min_exponent,
            std::fegetround(), FE_TONEAREST, __GNUC__, __GNUC_MINOR__};
        std::copy(data, data+10, out);
    });
}

extern "C" int cr_prepare(
    int n, int ns, const double* d, const double* l, const double* u,
    const double* r, const double* h, const double* weights,
    const double* xinf, double* beta_out, double* cw_out,
    double* nominal, double* lower, double* upper, double* radius,
    double* eta_out, char* msg, std::size_t cap) {
    return guarded(msg, cap, [&] {
        inputs(n, ns, d, l, u, r, h, weights);
        need(xinf && beta_out && cw_out && nominal && lower && upper &&
             radius && eta_out, "NULL_PREPARE_OUTPUT");
        for (int i = 0; i < n*RHS; ++i)
            need(std::isfinite(xinf[i]), "NONFINITE_SAVED_ALL_TIME");
        const LD b = witness_beta(n, d, l, u, h);
        *beta_out = out_down(b);
        need(*beta_out > 0, "BINARY64_BETA_UNDERFLOW");
        const LD beta = static_cast<LD>(*beta_out);
        const auto invh = inverse_witness(n, h);
        LD eta[RHS];
        for (int k = 0; k < RHS; ++k) {
            eta[k] = residual_norm(n, d, l, u, r+k*n, xinf+k*n, invh, 0, false);
            eta_out[k] = out_up(eta[k]);
        }
        for (int s = 0; s < ns; ++s) {
            const double* w = weights+s*n;
            const Dot cw = dot(n, [&](int i){return w[i];},
                                 [&](int i){return h[i];});
            cw_out[s] = out_up(uadd(cw.value, cw.error));
            for (int k = 0; k < RHS; ++k) {
                const Dot p = dot(n, [&](int i){return w[i];},
                                    [&](int i){return xinf[k*n+i];});
                const LD solve_error = umul(static_cast<LD>(cw_out[s]),
                                             udiv(eta[k], beta));
                scalar_interval(p.value, uadd(solve_error, p.error),
                    nominal[s*RHS+k], lower[s*RHS+k], upper[s*RHS+k],
                    radius[s*RHS+k]);
            }
        }
    });
}

extern "C" int cr_clock(
    int n, int ns, const double* d, const double* l, const double* u,
    const double* r, const double* h, const double* weights,
    double beta_lower, const double* cw_upper, int m, double gamma,
    double* nominal, double* lower, double* upper, double* radius,
    double* stats, double* capture_steps, double* capture_epsilon,
    double* capture_radius, double* capture_sum, double* capture_sum_radius,
    char* msg, std::size_t cap) {
    return guarded(msg, cap, [&] {
        inputs(n, ns, d, l, u, r, h, weights);
        need(m >= 1 && m <= MAX_M, "UNSUPPORTED_CLOCK_ORDER");
        need(std::isfinite(gamma) && gamma > 0, "POSITIVE_FINITE_GAMMA_REQUIRED");
        need(std::isfinite(beta_lower) && beta_lower > 0 &&
             cw_upper && nominal && lower && upper && radius && stats,
             "INVALID_CLOCK_ARGUMENT");
        const bool capture = capture_steps != nullptr;
        need(capture ? (m <= 16 && capture_epsilon && capture_radius &&
                        capture_sum && capture_sum_radius)
                     : (!capture_epsilon && !capture_radius &&
                        !capture_sum && !capture_sum_radius),
             "INVALID_CAPTURE_ARGUMENT");
        const LD verified_beta = witness_beta(n, d, l, u, h);
        need(static_cast<LD>(beta_lower) <= verified_beta,
             "UNVERIFIED_BETA_ARGUMENT");
        for (int s = 0; s < ns; ++s) {
            const Dot cw = dot(n, [&](int i){return weights[s*n+i];},
                                 [&](int i){return h[i];});
            need(std::isfinite(cw_upper[s]) && cw_upper[s] >= 0 &&
                 static_cast<LD>(cw_upper[s]) >= uadd(cw.value, cw.error),
                 "UNVERIFIED_CW_ARGUMENT");
        }
        const auto invh = inverse_witness(n, h);
        const LD alpha = std::max(static_cast<LD>(gamma),
            down(static_cast<LD>(beta_lower)+static_cast<LD>(gamma)));
        need(alpha > 0, "NONPOSITIVE_ALPHA");
        std::vector<double> dl(std::max(1,n-1),0), dd(n), du(std::max(1,n-1),0);
        std::vector<double> du2(std::max(1,n-2),0);
        std::vector<int> piv(n);
        LD shift_loss = 0;
        for (int i = 0; i < n; ++i) {
            dd[i] = d[i] + gamma;
            need(std::isfinite(dd[i]), "SHIFTED_DIAGONAL_OVERFLOW");
            const LD exactish = static_cast<LD>(d[i])+static_cast<LD>(gamma);
            const LD e = std::fabs(exactish-static_cast<LD>(dd[i]));
            const LD addition_round = umul(SHORT_G,
                std::fabs(static_cast<LD>(d[i]))+std::fabs(static_cast<LD>(gamma)));
            shift_loss = std::max(shift_loss, uadd(e,addition_round));
        }
        if (n>1) {
            std::copy(l,l+n-1,dl.begin()); std::copy(u,u+n-1,du.begin());
        }
        int info = 0;
        dgttrf_(&n,dl.data(),dd.data(),du.data(),du2.data(),piv.data(),&info);
        need(info == 0, "DGTTRF_FAILED");
        environment();
        std::vector<double> previous(n*RHS,0), current(n*RHS,0);
        std::vector<LD> cumulative(n*RHS,0), sumabs(n*RHS,0);
        LD eps[RHS] = {0,0}, epssum[RHS] = {0,0}, etamax[RHS] = {0,0};
        double minvalue[RHS] = {INFINITY,INFINITY};
        const char trans = 'N';
        const int nrhs = RHS, ldb = n;
        for (int j = 0; j < m; ++j) {
            if (j == 0) std::copy(r,r+n*RHS,current.begin());
            else for (int i = 0; i < n*RHS; ++i)
                current[i] = gamma*previous[i];
            for (int i = 0; i < n*RHS; ++i)
                need(std::isfinite(current[i]), "RHS_FORMATION_OVERFLOW");
            dgttrs_(&trans,&n,&nrhs,dl.data(),dd.data(),du.data(),du2.data(),
                    piv.data(),current.data(),&ldb,&info,std::size_t(1));
            need(info == 0, "DGTTRS_FAILED");
            environment();
            for (int i = 0; i < n*RHS; ++i)
                need(std::isfinite(current[i]), "NONFINITE_LAPACK_SOLUTION");
            for (int k = 0; k < RHS; ++k) {
                const LD eta = residual_norm(n,d,l,u,
                    (j == 0 ? r : previous.data())+k*n,
                    current.data()+k*n,invh,gamma,j != 0);
                etamax[k] = std::max(etamax[k],eta);
                eps[k] = udiv(uadd(umul(static_cast<LD>(gamma),eps[k]),eta),alpha);
                epssum[k] = uadd(epssum[k],eps[k]);
                if (capture) capture_epsilon[j*RHS+k] = out_up(eps[k]);
                for (int i = 0; i < n; ++i) {
                    const int ix = k*n+i;
                    const double x = current[ix];
                    cumulative[ix] += static_cast<LD>(x);
                    sumabs[ix] += std::fabs(static_cast<LD>(x));
                    minvalue[k] = std::min(minvalue[k],x);
                    if (capture) {
                        const std::size_t ci = std::size_t(j)*RHS*n+ix;
                        capture_steps[ci] = x;
                        capture_radius[ci] = out_up(umul(eps[k],static_cast<LD>(h[i])));
                    }
                }
            }
            previous.swap(current);
        }
        const LD sum_margin = 4 * static_cast<LD>(m+1) * LEPS;
        need(sum_margin < 0.0001L, "ACCUMULATION_OPERATION_COUNT_UNSUPPORTED");
        for (int s = 0; s < ns; ++s) {
            const double* w = weights+s*n;
            for (int k = 0; k < RHS; ++k) {
                const Dot a = dot(n,[&](int i){return w[i];},
                    [&](int i){return cumulative[k*n+i];});
                const Dot sa = dot(n,[&](int i){return w[i];},
                    [&](int i){return sumabs[k*n+i];});
                const LD accumulation = umul(sum_margin,uadd(sa.value,sa.error));
                const LD solve_error = umul(static_cast<LD>(cw_upper[s]),epssum[k]);
                const LD err = uadd(uadd(solve_error,accumulation),a.error);
                scalar_interval(a.value,err,nominal[s*RHS+k],lower[s*RHS+k],
                                upper[s*RHS+k],radius[s*RHS+k]);
            }
        }
        if (capture) for (int k = 0; k < RHS; ++k)
            for (int i = 0; i < n; ++i) {
                const int ix = k*n+i;
                const double y = round_nearest(cumulative[ix]);
                capture_sum[ix] = y;
                LD err = uadd(umul(epssum[k],static_cast<LD>(h[i])),
                              umul(sum_margin,sumabs[ix]));
                err = uadd(err,std::fabs(static_cast<LD>(y)-cumulative[ix]));
                capture_sum_radius[ix] = out_up(err);
            }
        for (int k = 0; k < RHS; ++k) {
            stats[k] = out_up(etamax[k]);
            stats[2+k] = out_up(eps[k]);
            stats[4+k] = out_up(epssum[k]);
            stats[6+k] = minvalue[k];
        }
        stats[8] = out_up(shift_loss);
        stats[9] = double(m);
    });
}

