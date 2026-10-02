! R4AB immutable-panel endpoint-factored real radial moments.
! Strict FP64 and serial Kahan sums per entry. No OpenMP floating reduction.
module r4ab_radial
  use iso_c_binding
  use, intrinsic :: ieee_arithmetic
  implicit none
contains
  subroutine fixed_radial(nm,ne,nq,edges,ep,bubble,s,weight,out,status) bind(C,name='r4ab_fixed_radial')
    integer(c_int),value :: nm,ne,nq
    real(c_double),intent(in) :: edges(ne+1),ep(nm,ne+1),bubble(nm,ne,3),s(nq),weight(nq)
    real(c_double),intent(out) :: out(nm,nm,5)
    integer(c_int),intent(out) :: status
    real(c_double) :: acc(5),comp(5),term(5),u(nm),du(nm),r,h,x,qq,dq,uv,y,t
    integer :: a,b,e,j,k,i
    status=1;out=0
    if(nm<1.or.nm>32.or.ne<1.or.nq<5.or.nq>64)return
    if(any(.not.ieee_is_finite(edges)).or.any(.not.ieee_is_finite(ep)).or.any(.not.ieee_is_finite(bubble)))return
    if(any(.not.ieee_is_finite(s)).or.any(.not.ieee_is_finite(weight)))return
    if(edges(1)/=0.or.any(edges(2:)<=edges(:ne)).or.any(s<=0).or.any(s>=1).or.any(weight<=0))return
    if(any(ep(:,1)/=0).or.any(ep(:,ne+1)/=0))return
    do b=1,nm
      do a=1,nm
        acc=0;comp=0
        do e=1,ne
          h=edges(e+1)-edges(e)
          do j=1,nq
            x=s(j);r=edges(e)+h*x
            do i=1,nm
              qq=(bubble(i,e,3)*x+bubble(i,e,2))*x+bubble(i,e,1)
              dq=(2*bubble(i,e,3))*x+bubble(i,e,2)
              u(i)=(1-x)*ep(i,e)+x*ep(i,e+1)+(x*(1-x))*qq
              du(i)=((ep(i,e+1)-ep(i,e))+(1-2*x)*qq+(x*(1-x))*dq)/h
            end do
            uv=u(a)*u(b)
            term(1)=(h*weight(j))*uv
            term(2)=(h*weight(j))*(u(a)*du(b))
            term(3)=(h*weight(j))*(du(a)*du(b))
            term(4)=(h*weight(j))*(uv/r)
            term(5)=(h*weight(j))*(uv/(r*r))
            do k=1,5
              y=term(k)-comp(k);t=acc(k)+y;comp(k)=(t-acc(k))-y;acc(k)=t
            end do
          end do
        end do
        out(a,b,:)=acc
      end do
    end do
    status=0
    if(any(.not.ieee_is_finite(out)))status=2
  end subroutine
end module
