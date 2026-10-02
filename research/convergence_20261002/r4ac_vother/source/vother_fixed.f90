! Independent local-coordinate, split fixed-panel Coulomb radial moments.
! Each output entry has its own fixed summation order. No reduction/projection.
module r4ac_vother
 use iso_c_binding
 use, intrinsic :: ieee_arithmetic
 implicit none
contains
 subroutine r4ac_radial(nm,ne,nq,edges,endpoints,bubbles,rr,x,w,out,ierr) bind(C,name='r4ac_radial')
  integer(c_int),value::nm,ne,nq
  real(c_double),intent(in)::edges(ne+1),endpoints(nm,ne+1),bubbles(nm,ne,3),x(nq),w(nq)
  real(c_double),value::rr
  real(c_double),intent(out)::out(nm,nm,3)
  integer(c_int),intent(out)::ierr
  integer::ia,ib,ell,e,part,k
  real(c_double)::a,h,cut,lo,hi,s,r,ua,ub,fac,term,acc,comp,y,t
  out=0.0_c_double
  ierr=1
  if(nm<1.or.ne<1.or.nq<5.or.nq>64) return
  if(.not.ieee_is_finite(rr).or.rr<=0.0_c_double) return
  do ia=1,nm
   do ib=1,nm
    do ell=0,2
     acc=0.0_c_double
     comp=0.0_c_double
     do e=1,ne
      a=edges(e);h=edges(e+1)-a
      if(h<=0.0_c_double.or..not.ieee_is_finite(h))return
      cut=max(0.0_c_double,min(1.0_c_double,(rr-a)/h))
      do part=1,2
       if(part==1)then
        lo=0.0_c_double;hi=cut
       else
        lo=cut;hi=1.0_c_double
       endif
       if(hi<=lo)cycle
       do k=1,nq
        s=lo+0.5_c_double*(hi-lo)*(x(k)+1.0_c_double)
        r=a+h*s
        ua=(1.0_c_double-s)*endpoints(ia,e)+s*endpoints(ia,e+1) &
          +s*(1.0_c_double-s)*(bubbles(ia,e,1)+s*(bubbles(ia,e,2)+s*bubbles(ia,e,3)))
        ub=(1.0_c_double-s)*endpoints(ib,e)+s*endpoints(ib,e+1) &
          +s*(1.0_c_double-s)*(bubbles(ib,e,1)+s*(bubbles(ib,e,2)+s*bubbles(ib,e,3)))
        if(part==1)then
         fac=(r/rr)**ell/rr
        else
         fac=(rr/r)**ell/r
        endif
        term=(0.5_c_double*h*(hi-lo)*w(k))*ua*ub*fac
        y=term-comp;t=acc+y;comp=(t-acc)-y;acc=t
       enddo
      enddo
     enddo
     out(ia,ib,ell+1)=acc
    enddo
   enddo
  enddo
  if(.not.all(ieee_is_finite(out)))return
  ierr=0
 end subroutine
end module
