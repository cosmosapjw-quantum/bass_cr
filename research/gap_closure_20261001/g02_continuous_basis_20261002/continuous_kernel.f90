! R4X diagnostic-only FP64 endpoint-factored evaluator. Independent points only.
subroutine continuous_eval(n, ne, cells, s, h, endpoint, bubble, threads, u, du, observed) bind(C)
  use iso_c_binding
  use omp_lib
  implicit none
  integer(c_int), value :: n, ne, threads
  integer(c_int), intent(in) :: cells(n)
  real(c_double), intent(in) :: s(n), h(n), endpoint(ne+1), bubble(3,ne)
  real(c_double), intent(out) :: u(n), du(n)
  integer(c_int), intent(out) :: observed
  integer :: i, e
  real(c_double) :: x, q, dq, left, right, q0, q1, q2
  observed=0
  !$omp parallel num_threads(threads) private(i,e,x,q,dq,left,right,q0,q1,q2)
  !$omp single
  observed=omp_get_num_threads()
  !$omp end single
  !$omp do simd schedule(static)
  do i=1,n
    e=cells(i)+1
    x=s(i)
    left=endpoint(e)
    right=endpoint(e+1)
    q0=bubble(1,e)
    q1=bubble(2,e)
    q2=bubble(3,e)
    q=(q2*x+q1)*x+q0
    dq=(2.0_c_double*q2)*x+q1
    u(i)=(1.0_c_double-x)*left+x*right+(x*(1.0_c_double-x))*q
    du(i)=((right-left)+(1.0_c_double-2.0_c_double*x)*q+(x*(1.0_c_double-x))*dq)/h(i)
  end do
  !$omp end do simd
  !$omp end parallel
end subroutine continuous_eval
