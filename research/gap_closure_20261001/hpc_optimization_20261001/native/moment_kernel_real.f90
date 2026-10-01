! Real Cartesian s+p kernel. The C ABI keeps interleaved double complex data.
! Each independent matrix entry retains the original ascending quadrature order.
module bass_moment_real_impl
  use, intrinsic :: iso_c_binding, only: c_double, c_size_t, c_int, c_ptr, c_associated, c_f_pointer
  implicit none
  private
  public :: bass_moment_accumulate_real_f90_v1
  integer, parameter :: lane_count=8
  type :: cx
    real(c_double) :: r, i
  end type
contains
  integer(c_int) function bass_moment_accumulate_real_f90_v1(n,nt,np, &
      geo_p,radt_p,radp_p,qt_p,qp_p,vel_p,weights_p,phase_p,R,Zt,Zp,output_p) &
      bind(C,name='bass_moment_accumulate_real_f90_v1') result(rc)
    integer(c_size_t), value :: n,nt,np
    type(c_ptr), value :: geo_p,radt_p,radp_p,qt_p,qp_p,vel_p,weights_p,phase_p,output_p
    real(c_double), value :: R,Zt,Zp
    real(c_double), pointer, contiguous :: geo(:),radt(:),radp(:),qt(:),qp(:),vel(:),weights(:),phase(:),output(:)
    real(c_double), allocatable :: geom(:,:),tcoef(:,:),pcoef(:,:),qdot(:,:)
    real(c_double) :: vt2,vp2,vtp
    integer :: nn,nnt,nnp,nblocks,b,u,i,j,k
    logical :: target_static
    rc=1_c_int
    if (n<1_c_size_t.or.n>4096_c_size_t.or.nt<1_c_size_t.or.nt>128_c_size_t &
        .or.np<1_c_size_t.or.np>128_c_size_t) return
    if (.not.(c_associated(geo_p).and.c_associated(radt_p).and.c_associated(radp_p) &
        .and.c_associated(qt_p).and.c_associated(qp_p).and.c_associated(vel_p) &
        .and.c_associated(weights_p).and.c_associated(phase_p).and.c_associated(output_p))) return
    nn=int(n); nnt=int(nt); nnp=int(np)
    call c_f_pointer(geo_p,geo,[4*nn]); call c_f_pointer(radt_p,radt,[2*nn*nnt])
    call c_f_pointer(radp_p,radp,[2*nn*nnp]); call c_f_pointer(qt_p,qt,[8*nnt])
    call c_f_pointer(qp_p,qp,[8*nnp]); call c_f_pointer(vel_p,vel,[6])
    call c_f_pointer(weights_p,weights,[12*nn]); call c_f_pointer(phase_p,phase,[2*nn])
    call c_f_pointer(output_p,output,[8*nnt*nnp])
    ! The Python boundary also checks this. Never silently discard complex data.
    if (any(qt(2::2)/=0.0_c_double).or.any(qp(2::2)/=0.0_c_double)) then
      rc=2_c_int
      return
    end if
    vt2=(vel(1)*vel(1)+vel(2)*vel(2))+vel(3)*vel(3)
    vp2=(vel(4)*vel(4)+vel(5)*vel(5))+vel(6)*vel(6)
    vtp=(vel(1)*vel(4)+vel(2)*vel(5))+vel(3)*vel(6)
    target_static=all(vel(1:3)==0.0_c_double)
    allocate(geom(5,nn),tcoef(6,nnt),pcoef(6,nnp),qdot(nnp,nnt))
    do u=1,nn
      geom(1,u)=geo(4*u-1)                           ! a
      geom(2,u)=geo(4*u)                             ! rho
      geom(3,u)=geom(1,u)-R                          ! a-R
      geom(4,u)=((geo(4*u-3)*geo(4*u-3)+geo(4*u-2)*geo(4*u-2))-R*R)/2.0_c_double
      geom(5,u)=-Zt/geo(4*u-3)-Zp/geo(4*u-2)
    end do
    do i=1,nnt
      do k=1,4
        tcoef(k,i)=qt(8*(i-1)+2*k-1)
      end do
      tcoef(5,i)=(vel(4)*tcoef(2,i)+vel(5)*tcoef(3,i))+vel(6)*tcoef(4,i)
      tcoef(6,i)=(vel(1)*tcoef(2,i)+vel(2)*tcoef(3,i))+vel(3)*tcoef(4,i)
    end do
    do j=1,nnp
      do k=1,4
        pcoef(k,j)=qp(8*(j-1)+2*k-1)
      end do
      pcoef(5,j)=(vel(4)*pcoef(2,j)+vel(5)*pcoef(3,j))+vel(6)*pcoef(4,j)
      pcoef(6,j)=(vel(1)*pcoef(2,j)+vel(2)*pcoef(3,j))+vel(3)*pcoef(4,j)
      do i=1,nnt
        qdot(j,i)=(tcoef(2,i)*pcoef(2,j)+tcoef(3,i)*pcoef(3,j))+tcoef(4,i)*pcoef(4,j)
      end do
    end do
    nblocks=(nnt*nnp+lane_count-1)/lane_count
    !$omp parallel do schedule(static) default(none) &
    !$omp shared(nblocks,nn,nnt,nnp,geom,radt,radp,tcoef,pcoef,qdot,vel,weights,phase,output,vt2,vp2,vtp,target_static)
    do b=1,nblocks
      call accumulate_block(b,nn,nnt,nnp,geom,radt,radp,tcoef,pcoef,qdot,vel,weights,phase, &
                            output,vt2,vp2,vtp,target_static)
    end do
    !$omp end parallel do
    rc=0_c_int
  end function

  subroutine accumulate_block(block_id,n,nt,np,geom,radt,radp,tcoef,pcoef,qdot,vel,weights,phase, &
                              output,vt2,vp2,vtp,target_static)
    integer, intent(in) :: block_id,n,nt,np
    real(c_double), intent(in) :: geom(5,n),radt(*),radp(*),tcoef(6,nt),pcoef(6,np),qdot(np,nt)
    real(c_double), intent(in) :: vel(6),weights(*),phase(*),vt2,vp2,vtp
    real(c_double), intent(inout) :: output(*)
    logical, intent(in) :: target_static
    integer :: size,first,l,u,k,i,j,pos,ri,rj
    integer :: ti(lane_count),pj(lane_count)
    real(c_double) :: tr(lane_count,6),pr(lane_count,6),qd(lane_count)
    real(c_double) :: acc_r(lane_count,4),acc_i(lane_count,4)
    real(c_double) :: a,rho,apx,xx,V,at,bt,ap,bp,b0,bc,bs,bcc,bss,bcs
    real(c_double) :: lt0,lt1,lt2,txp0,txp1,txp2,lp0,lp1,lp2,pxt0,pxt1,pxt2
    real(c_double) :: vpxt(3),vpxp(3),vtxt(3),vtxp(3)
    type(cx) :: m(6),pw
    ! BEGIN GENERATED DECLARATIONS
    real(c_double) :: w001r,w001i,w002r,w002i,w003r,w003i,w004r,w004i,w005r,w005i
    real(c_double) :: w006r,w006i,w007r,w007i,w008r,w008i,w009r,w009i,w010r,w010i
    real(c_double) :: w011r,w011i,w012r,w012i,w013r,w013i,w014r,w014i,w015r,w015i
    real(c_double) :: w016r,w016i,w017r,w017i,w018r,w018i,w019r,w019i,w020r,w020i
    real(c_double) :: w021r,w021i,w022r,w022i,w023r,w023i,w024r,w024i,w025r,w025i
    real(c_double) :: w026r,w026i,w027r,w027i,w028r,w028i,w029r,w029i,w030r,w030i
    real(c_double) :: w031r,w031i,w032r,w032i,w033r,w033i,w034r,w034i,w035r,w035i
    real(c_double) :: w036r,w036i,w037r,w037i,w038r,w038i,w039r,w039i,w040r,w040i
    real(c_double) :: w041r,w041i,w042r,w042i,w043r,w043i,w044r,w044i,w045r,w045i
    real(c_double) :: w046r,w046i,w047r,w047i,w048r,w048i,w049r,w049i,w050r,w050i
    real(c_double) :: w051r,w051i,w052r,w052i,w053r,w053i,w054r,w054i,w055r,w055i
    real(c_double) :: w056r,w056i,w057r,w057i,w058r,w058i,w059r,w059i,w060r,w060i
    real(c_double) :: w061r,w061i,w062r,w062i,w063r,w063i,w064r,w064i,w065r,w065i
    real(c_double) :: w066r,w066i,w067r,w067i,w068r,w068i,w069r,w069i,w070r,w070i
    real(c_double) :: w071r,w071i,w072r,w072i,w073r,w073i,w074r,w074i,w075r,w075i
    real(c_double) :: w076r,w076i,w077r,w077i,w078r,w078i,w079r,w079i,w080r,w080i
    real(c_double) :: w081r,w081i,w082r,w082i,w083r,w083i,w084r,w084i,w085r,w085i
    real(c_double) :: w086r,w086i,w087r,w087i,w088r,w088i,w089r,w089i,w090r,w090i
    real(c_double) :: w091r,w091i,w092r,w092i,w093r,w093i,w094r,w094i,w095r,w095i
    real(c_double) :: w096r,w096i,w097r,w097i,w098r,w098i,w099r,w099i,w100r,w100i
    real(c_double) :: w101r,w101i,w102r,w102i,w103r,w103i,w104r,w104i,w105r,w105i
    real(c_double) :: w106r,w106i,w107r,w107i,w108r,w108i,w109r,w109i
    ! END GENERATED DECLARATIONS
    first=(block_id-1)*lane_count
    size=min(lane_count,nt*np-first)
    do l=1,size
      i=(first+l-1)/np+1; j=mod(first+l-1,np)+1
      ti(l)=i; pj(l)=j; tr(l,:)=tcoef(:,i); pr(l,:)=pcoef(:,j); qd(l)=qdot(j,i)
      do k=1,4
        pos=2*((k-1)*nt*np+first+l)-1
        acc_r(l,k)=output(pos); acc_i(l,k)=output(pos+1)
      end do
    end do
    do u=1,n
      a=geom(1,u); rho=geom(2,u); apx=geom(3,u); xx=geom(4,u); V=geom(5,u)
      pw=cx(phase(2*u-1),phase(2*u))
      do k=1,6
        m(k)=cx(weights(12*(u-1)+2*k-1),weights(12*(u-1)+2*k))
      end do
      vpxt=[vel(4)*a,vel(5)*rho,vel(6)*rho]; vpxp=[vel(4)*apx,vel(5)*rho,vel(6)*rho]
      vtxt=[vel(1)*a,vel(2)*rho,vel(3)*rho]; vtxp=[vel(1)*apx,vel(2)*rho,vel(3)*rho]
      ! Uniform branch is outside the SIMD loop; no lane changes its u order.
      ! BEGIN GENERATED ARITHMETIC
      if (target_static) then
      !$omp simd &
      !$omp private(i,j,ri,rj,at,bt,ap,bp,b0,bc) &
      !$omp private(bs,bcc,bss,bcs,lt0,lt1,lt2,txp0,txp1,txp2) &
      !$omp private(lp0,lp1,lp2,pxt0,pxt1,pxt2,w001r,w001i,w002r,w002i) &
      !$omp private(w003r,w003i,w004r,w004i,w005r,w005i,w006r,w006i,w007r,w007i) &
      !$omp private(w008r,w008i,w009r,w009i,w010r,w010i,w011r,w011i,w012r,w012i) &
      !$omp private(w013r,w013i,w014r,w014i,w015r,w015i,w016r,w016i,w017r,w017i) &
      !$omp private(w018r,w018i,w019r,w019i,w020r,w020i,w021r,w021i,w022r,w022i) &
      !$omp private(w023r,w023i,w024r,w024i,w025r,w025i,w026r,w026i,w027r,w027i) &
      !$omp private(w028r,w028i,w029r,w029i,w030r,w030i,w031r,w031i,w032r,w032i) &
      !$omp private(w033r,w033i,w034r,w034i,w035r,w035i,w036r,w036i,w037r,w037i) &
      !$omp private(w038r,w038i,w039r,w039i,w040r,w040i,w041r,w041i,w042r,w042i) &
      !$omp private(w043r,w043i,w044r,w044i,w045r,w045i,w046r,w046i,w047r,w047i) &
      !$omp private(w048r,w048i,w049r,w049i,w050r,w050i,w051r,w051i,w052r,w052i) &
      !$omp private(w053r,w053i,w054r,w054i,w055r,w055i,w056r,w056i,w057r,w057i) &
      !$omp private(w058r,w058i,w059r,w059i,w060r,w060i,w061r,w061i,w062r,w062i) &
      !$omp private(w063r,w063i,w064r,w064i,w065r,w065i,w066r,w066i,w067r,w067i) &
      !$omp private(w068r,w068i,w069r,w069i,w070r,w070i,w071r,w071i,w072r,w072i) &
      !$omp private(w073r,w073i,w074r,w074i,w075r,w075i,w076r,w076i,w077r,w077i) &
      !$omp private(w078r,w078i,w079r,w079i,w080r,w080i,w081r,w081i,w082r,w082i) &
      !$omp private(w083r,w083i,w084r,w084i,w085r,w085i,w086r,w086i,w087r,w087i) &
      !$omp private(w088r,w088i,w089r,w089i,w090r,w090i,w091r,w091i,w092r,w092i) &
      !$omp private(w093r,w093i,w094r,w094i,w095r,w095i,w096r,w096i,w097r,w097i) &
      !$omp private(w098r,w098i,w099r,w099i,w100r,w100i,w101r,w101i,w102r,w102i) &
      !$omp private(w103r,w103i,w104r,w104i,w105r,w105i,w106r,w106i,w107r,w107i) &
      !$omp private(w108r,w108i,w109r,w109i)
      do l=1,size
        i=ti(l); j=pj(l)
        lt0=tr(l,1)+a*tr(l,2); lt1=rho*tr(l,3); lt2=rho*tr(l,4)
        txp0=apx*tr(l,2); txp1=rho*tr(l,3); txp2=rho*tr(l,4)
        lp0=pr(l,1)+apx*pr(l,2); lp1=rho*pr(l,3); lp2=rho*pr(l,4)
        pxt0=a*pr(l,2); pxt1=rho*pr(l,3); pxt2=rho*pr(l,4)
        ri=2*((u-1)*nt+i)-1; rj=2*((u-1)*np+j)-1
        at=radt(ri); bt=radt(ri+1); ap=radp(rj); bp=radp(rj+1)
        w001r=m(1)%r*(lt0)
        w001i=m(1)%i*(lt0)
        w002r=m(2)%r*(lt1)
        w002i=m(2)%i*(lt1)
        w003r=w001r+w002r
        w003i=w001i+w002i
        w004r=m(1)%r*(lp0)
        w004i=m(1)%i*(lp0)
        w005r=m(2)%r*(lp1)
        w005i=m(2)%i*(lp1)
        w006r=w004r+w005r
        w006i=w004i+w005i
        w007r=m(1)%r*(lt0)
        w007i=m(1)%i*(lt0)
        w008r=w007r*(lp0)
        w008i=w007i*(lp0)
        w009r=m(2)%r*(lt0*lp1+lt1*lp0)
        w009i=m(2)%i*(lt0*lp1+lt1*lp0)
        w010r=w008r+w009r
        w010i=w008i+w009i
        w011r=m(3)%r*(lt1)
        w011i=m(3)%i*(lt1)
        w012r=w011r*(lp1)
        w012i=w011i*(lp1)
        w013r=w010r+w012r
        w013i=w010i+w012i
        w014r=m(4)%r*(lt2)
        w014i=m(4)%i*(lt2)
        w015r=w014r*(lp2)
        w015i=w014i*(lp2)
        w016r=w013r+w015r
        w016i=w013i+w015i
        w017r=(at*ap)*w016r
        w017i=(at*ap)*w016i
        w018r=((at*ap)*qd(l))*m(1)%r
        w018i=((at*ap)*qd(l))*m(1)%i
        w019r=m(1)%r*(txp0)
        w019i=m(1)%i*(txp0)
        w020r=w019r*(lp0)
        w020i=w019i*(lp0)
        w021r=m(2)%r*(txp0*lp1+txp1*lp0)
        w021i=m(2)%i*(txp0*lp1+txp1*lp0)
        w022r=w020r+w021r
        w022i=w020i+w021i
        w023r=m(3)%r*(txp1)
        w023i=m(3)%i*(txp1)
        w024r=w023r*(lp1)
        w024i=w023i*(lp1)
        w025r=w022r+w024r
        w025i=w022i+w024i
        w026r=m(4)%r*(txp2)
        w026i=m(4)%i*(txp2)
        w027r=w026r*(lp2)
        w027i=w026i*(lp2)
        w028r=w025r+w027r
        w028i=w025i+w027i
        w029r=(at*bp)*w028r
        w029i=(at*bp)*w028i
        w030r=w018r+w029r
        w030i=w018i+w029i
        w031r=m(1)%r*(lt0)
        w031i=m(1)%i*(lt0)
        w032r=w031r*(pxt0)
        w032i=w031i*(pxt0)
        w033r=m(2)%r*(lt0*pxt1+lt1*pxt0)
        w033i=m(2)%i*(lt0*pxt1+lt1*pxt0)
        w034r=w032r+w033r
        w034i=w032i+w033i
        w035r=m(3)%r*(lt1)
        w035i=m(3)%i*(lt1)
        w036r=w035r*(pxt1)
        w036i=w035i*(pxt1)
        w037r=w034r+w036r
        w037i=w034i+w036i
        w038r=m(4)%r*(lt2)
        w038i=m(4)%i*(lt2)
        w039r=w038r*(pxt2)
        w039i=w038i*(pxt2)
        w040r=w037r+w039r
        w040i=w037i+w039i
        w041r=(bt*ap)*w040r
        w041i=(bt*ap)*w040i
        w042r=w030r+w041r
        w042i=w030i+w041i
        w043r=((bt*bp)*xx)*w016r
        w043i=((bt*bp)*xx)*w016i
        w044r=w042r+w043r
        w044i=w042i+w043i
        b0=lt0*lp0; bc=lt0*lp1+lt1*lp0; bs=lt0*lp2+lt2*lp0
        bcc=lt1*lp1; bss=lt2*lp2; bcs=lt1*lp2+lt2*lp1
        w045r=m(2)%r*(b0)
        w045i=m(2)%i*(b0)
        w046r=m(3)%r*(bc)
        w046i=m(3)%i*(bc)
        w047r=w045r+w046r
        w047i=w045i+w046i
        w048r=m(5)%r*(bcc)
        w048i=m(5)%i*(bcc)
        w049r=w047r+w048r
        w049i=w047i+w048i
        w050r=m(6)%r*(bss)
        w050i=m(6)%i*(bss)
        w051r=w049r+w050r
        w051i=w049i+w050i
        w052r=m(4)%r*(bs)
        w052i=m(4)%i*(bs)
        w053r=m(6)%r*(bcs)
        w053i=m(6)%i*(bcs)
        w054r=w052r+w053r
        w054i=w052i+w053i
        w055r=0.0_c_double*(ap)
        w055i=1.0_c_double*(ap)
        w056r=(at*tr(l,5))*w006r
        w056i=(at*tr(l,5))*w006i
        w057r=(vpxt(1))*w016r
        w057i=(vpxt(1))*w016i
        w058r=(vpxt(2))*w051r
        w058i=(vpxt(2))*w051i
        w059r=w057r+w058r
        w059i=w057i+w058i
        w060r=(vpxt(3))*w054r
        w060i=(vpxt(3))*w054i
        w061r=w059r+w060r
        w061i=w059i+w060i
        w062r=(bt)*w061r
        w062i=(bt)*w061i
        w063r=w056r+w062r
        w063i=w056i+w062i
        w064r=w055r*w063r-w055i*w063i
        w064i=w055r*w063i+w055i*w063r
        w065r=w044r+w064r
        w065i=w044i+w064i
        w066r=((-at*ap)*pr(l,5))*w003r
        w066i=((-at*ap)*pr(l,5))*w003i
        w067r=(vpxp(1))*w016r
        w067i=(vpxp(1))*w016i
        w068r=(vpxp(2))*w051r
        w068i=(vpxp(2))*w051i
        w069r=w067r+w068r
        w069i=w067i+w068i
        w070r=(vpxp(3))*w054r
        w070i=(vpxp(3))*w054i
        w071r=w069r+w070r
        w071i=w069i+w070i
        w072r=(at*bp)*w071r
        w072i=(at*bp)*w071i
        w073r=w066r-w072r
        w073i=w066i-w072i
        w074r=(0.5_c_double)*0.0_c_double
        w074i=(0.5_c_double)*1.0_c_double
        w075r=w074r*(vp2)
        w075i=w074i*(vp2)
        w076r=w075r*w017r-w075i*w017i
        w076i=w075r*w017i+w075i*w017r
        w077r=w073r-w076r
        w077i=w073i-w076i
        w078r=(0.5_c_double)*w065r
        w078i=(0.5_c_double)*w065i
        w079r=(V)*w017r
        w079i=(V)*w017i
        w080r=w078r+w079r
        w080i=w078i+w079i
        w081r=pw%r*w017r-pw%i*w017i
        w081i=pw%r*w017i+pw%i*w017r
        acc_r(l,1)=acc_r(l,1)+w081r
        acc_i(l,1)=acc_i(l,1)+w081i
        w082r=pw%r*w080r-pw%i*w080i
        w082i=pw%r*w080i+pw%i*w080r
        acc_r(l,2)=acc_r(l,2)+w082r
        acc_i(l,2)=acc_i(l,2)+w082i
        w083r=pw%r*w077r-pw%i*w077i
        w083i=pw%r*w077i+pw%i*w077r
        acc_r(l,3)=acc_r(l,3)+w083r
        acc_i(l,3)=acc_i(l,3)+w083i
        w084r=pw%r*0.0_c_double-pw%i*0.0_c_double
        w084i=pw%r*0.0_c_double+pw%i*0.0_c_double
        acc_r(l,4)=acc_r(l,4)+w084r
        acc_i(l,4)=acc_i(l,4)+w084i
      end do
      !$omp end simd
      else
      !$omp simd &
      !$omp private(i,j,ri,rj,at,bt,ap,bp,b0,bc) &
      !$omp private(bs,bcc,bss,bcs,lt0,lt1,lt2,txp0,txp1,txp2) &
      !$omp private(lp0,lp1,lp2,pxt0,pxt1,pxt2,w001r,w001i,w002r,w002i) &
      !$omp private(w003r,w003i,w004r,w004i,w005r,w005i,w006r,w006i,w007r,w007i) &
      !$omp private(w008r,w008i,w009r,w009i,w010r,w010i,w011r,w011i,w012r,w012i) &
      !$omp private(w013r,w013i,w014r,w014i,w015r,w015i,w016r,w016i,w017r,w017i) &
      !$omp private(w018r,w018i,w019r,w019i,w020r,w020i,w021r,w021i,w022r,w022i) &
      !$omp private(w023r,w023i,w024r,w024i,w025r,w025i,w026r,w026i,w027r,w027i) &
      !$omp private(w028r,w028i,w029r,w029i,w030r,w030i,w031r,w031i,w032r,w032i) &
      !$omp private(w033r,w033i,w034r,w034i,w035r,w035i,w036r,w036i,w037r,w037i) &
      !$omp private(w038r,w038i,w039r,w039i,w040r,w040i,w041r,w041i,w042r,w042i) &
      !$omp private(w043r,w043i,w044r,w044i,w045r,w045i,w046r,w046i,w047r,w047i) &
      !$omp private(w048r,w048i,w049r,w049i,w050r,w050i,w051r,w051i,w052r,w052i) &
      !$omp private(w053r,w053i,w054r,w054i,w055r,w055i,w056r,w056i,w057r,w057i) &
      !$omp private(w058r,w058i,w059r,w059i,w060r,w060i,w061r,w061i,w062r,w062i) &
      !$omp private(w063r,w063i,w064r,w064i,w065r,w065i,w066r,w066i,w067r,w067i) &
      !$omp private(w068r,w068i,w069r,w069i,w070r,w070i,w071r,w071i,w072r,w072i) &
      !$omp private(w073r,w073i,w074r,w074i,w075r,w075i,w076r,w076i,w077r,w077i) &
      !$omp private(w078r,w078i,w079r,w079i,w080r,w080i,w081r,w081i,w082r,w082i) &
      !$omp private(w083r,w083i,w084r,w084i,w085r,w085i,w086r,w086i,w087r,w087i) &
      !$omp private(w088r,w088i,w089r,w089i,w090r,w090i,w091r,w091i,w092r,w092i) &
      !$omp private(w093r,w093i,w094r,w094i,w095r,w095i,w096r,w096i,w097r,w097i) &
      !$omp private(w098r,w098i,w099r,w099i,w100r,w100i,w101r,w101i,w102r,w102i) &
      !$omp private(w103r,w103i,w104r,w104i,w105r,w105i,w106r,w106i,w107r,w107i) &
      !$omp private(w108r,w108i,w109r,w109i)
      do l=1,size
        i=ti(l); j=pj(l)
        lt0=tr(l,1)+a*tr(l,2); lt1=rho*tr(l,3); lt2=rho*tr(l,4)
        txp0=apx*tr(l,2); txp1=rho*tr(l,3); txp2=rho*tr(l,4)
        lp0=pr(l,1)+apx*pr(l,2); lp1=rho*pr(l,3); lp2=rho*pr(l,4)
        pxt0=a*pr(l,2); pxt1=rho*pr(l,3); pxt2=rho*pr(l,4)
        ri=2*((u-1)*nt+i)-1; rj=2*((u-1)*np+j)-1
        at=radt(ri); bt=radt(ri+1); ap=radp(rj); bp=radp(rj+1)
        w001r=m(1)%r*(lt0)
        w001i=m(1)%i*(lt0)
        w002r=m(2)%r*(lt1)
        w002i=m(2)%i*(lt1)
        w003r=w001r+w002r
        w003i=w001i+w002i
        w004r=m(1)%r*(lp0)
        w004i=m(1)%i*(lp0)
        w005r=m(2)%r*(lp1)
        w005i=m(2)%i*(lp1)
        w006r=w004r+w005r
        w006i=w004i+w005i
        w007r=m(1)%r*(lt0)
        w007i=m(1)%i*(lt0)
        w008r=w007r*(lp0)
        w008i=w007i*(lp0)
        w009r=m(2)%r*(lt0*lp1+lt1*lp0)
        w009i=m(2)%i*(lt0*lp1+lt1*lp0)
        w010r=w008r+w009r
        w010i=w008i+w009i
        w011r=m(3)%r*(lt1)
        w011i=m(3)%i*(lt1)
        w012r=w011r*(lp1)
        w012i=w011i*(lp1)
        w013r=w010r+w012r
        w013i=w010i+w012i
        w014r=m(4)%r*(lt2)
        w014i=m(4)%i*(lt2)
        w015r=w014r*(lp2)
        w015i=w014i*(lp2)
        w016r=w013r+w015r
        w016i=w013i+w015i
        w017r=(at*ap)*w016r
        w017i=(at*ap)*w016i
        w018r=((at*ap)*qd(l))*m(1)%r
        w018i=((at*ap)*qd(l))*m(1)%i
        w019r=m(1)%r*(txp0)
        w019i=m(1)%i*(txp0)
        w020r=w019r*(lp0)
        w020i=w019i*(lp0)
        w021r=m(2)%r*(txp0*lp1+txp1*lp0)
        w021i=m(2)%i*(txp0*lp1+txp1*lp0)
        w022r=w020r+w021r
        w022i=w020i+w021i
        w023r=m(3)%r*(txp1)
        w023i=m(3)%i*(txp1)
        w024r=w023r*(lp1)
        w024i=w023i*(lp1)
        w025r=w022r+w024r
        w025i=w022i+w024i
        w026r=m(4)%r*(txp2)
        w026i=m(4)%i*(txp2)
        w027r=w026r*(lp2)
        w027i=w026i*(lp2)
        w028r=w025r+w027r
        w028i=w025i+w027i
        w029r=(at*bp)*w028r
        w029i=(at*bp)*w028i
        w030r=w018r+w029r
        w030i=w018i+w029i
        w031r=m(1)%r*(lt0)
        w031i=m(1)%i*(lt0)
        w032r=w031r*(pxt0)
        w032i=w031i*(pxt0)
        w033r=m(2)%r*(lt0*pxt1+lt1*pxt0)
        w033i=m(2)%i*(lt0*pxt1+lt1*pxt0)
        w034r=w032r+w033r
        w034i=w032i+w033i
        w035r=m(3)%r*(lt1)
        w035i=m(3)%i*(lt1)
        w036r=w035r*(pxt1)
        w036i=w035i*(pxt1)
        w037r=w034r+w036r
        w037i=w034i+w036i
        w038r=m(4)%r*(lt2)
        w038i=m(4)%i*(lt2)
        w039r=w038r*(pxt2)
        w039i=w038i*(pxt2)
        w040r=w037r+w039r
        w040i=w037i+w039i
        w041r=(bt*ap)*w040r
        w041i=(bt*ap)*w040i
        w042r=w030r+w041r
        w042i=w030i+w041i
        w043r=((bt*bp)*xx)*w016r
        w043i=((bt*bp)*xx)*w016i
        w044r=w042r+w043r
        w044i=w042i+w043i
        b0=lt0*lp0; bc=lt0*lp1+lt1*lp0; bs=lt0*lp2+lt2*lp0
        bcc=lt1*lp1; bss=lt2*lp2; bcs=lt1*lp2+lt2*lp1
        w045r=m(2)%r*(b0)
        w045i=m(2)%i*(b0)
        w046r=m(3)%r*(bc)
        w046i=m(3)%i*(bc)
        w047r=w045r+w046r
        w047i=w045i+w046i
        w048r=m(5)%r*(bcc)
        w048i=m(5)%i*(bcc)
        w049r=w047r+w048r
        w049i=w047i+w048i
        w050r=m(6)%r*(bss)
        w050i=m(6)%i*(bss)
        w051r=w049r+w050r
        w051i=w049i+w050i
        w052r=m(4)%r*(bs)
        w052i=m(4)%i*(bs)
        w053r=m(6)%r*(bcs)
        w053i=m(6)%i*(bcs)
        w054r=w052r+w053r
        w054i=w052i+w053i
        w055r=0.0_c_double*(ap)
        w055i=1.0_c_double*(ap)
        w056r=(at*tr(l,5))*w006r
        w056i=(at*tr(l,5))*w006i
        w057r=(vpxt(1))*w016r
        w057i=(vpxt(1))*w016i
        w058r=(vpxt(2))*w051r
        w058i=(vpxt(2))*w051i
        w059r=w057r+w058r
        w059i=w057i+w058i
        w060r=(vpxt(3))*w054r
        w060i=(vpxt(3))*w054i
        w061r=w059r+w060r
        w061i=w059i+w060i
        w062r=(bt)*w061r
        w062i=(bt)*w061i
        w063r=w056r+w062r
        w063i=w056i+w062i
        w064r=w055r*w063r-w055i*w063i
        w064i=w055r*w063i+w055i*w063r
        w065r=w044r+w064r
        w065i=w044i+w064i
        w066r=0.0_c_double*(at)
        w066i=1.0_c_double*(at)
        w067r=(ap*pr(l,6))*w003r
        w067i=(ap*pr(l,6))*w003i
        w068r=(vtxp(1))*w016r
        w068i=(vtxp(1))*w016i
        w069r=(vtxp(2))*w051r
        w069i=(vtxp(2))*w051i
        w070r=w068r+w069r
        w070i=w068i+w069i
        w071r=(vtxp(3))*w054r
        w071i=(vtxp(3))*w054i
        w072r=w070r+w071r
        w072i=w070i+w071i
        w073r=(bp)*w072r
        w073i=(bp)*w072i
        w074r=w067r+w073r
        w074i=w067i+w073i
        w075r=w066r*w074r-w066i*w074i
        w075i=w066r*w074i+w066i*w074r
        w076r=w065r-w075r
        w076i=w065i-w075i
        w077r=(vtp)*w017r
        w077i=(vtp)*w017i
        w078r=w076r+w077r
        w078i=w076i+w077i
        w079r=((-at*ap)*pr(l,5))*w003r
        w079i=((-at*ap)*pr(l,5))*w003i
        w080r=(vpxp(1))*w016r
        w080i=(vpxp(1))*w016i
        w081r=(vpxp(2))*w051r
        w081i=(vpxp(2))*w051i
        w082r=w080r+w081r
        w082i=w080i+w081i
        w083r=(vpxp(3))*w054r
        w083i=(vpxp(3))*w054i
        w084r=w082r+w083r
        w084i=w082i+w083i
        w085r=(at*bp)*w084r
        w085i=(at*bp)*w084i
        w086r=w079r-w085r
        w086i=w079i-w085i
        w087r=(0.5_c_double)*0.0_c_double
        w087i=(0.5_c_double)*1.0_c_double
        w088r=w087r*(vp2)
        w088i=w087i*(vp2)
        w089r=w088r*w017r-w088i*w017i
        w089i=w088r*w017i+w088i*w017r
        w090r=w086r-w089r
        w090i=w086i-w089i
        w091r=((-at*ap)*tr(l,6))*w006r
        w091i=((-at*ap)*tr(l,6))*w006i
        w092r=(vtxt(1))*w016r
        w092i=(vtxt(1))*w016i
        w093r=(vtxt(2))*w051r
        w093i=(vtxt(2))*w051i
        w094r=w092r+w093r
        w094i=w092i+w093i
        w095r=(vtxt(3))*w054r
        w095i=(vtxt(3))*w054i
        w096r=w094r+w095r
        w096i=w094i+w095i
        w097r=(ap*bt)*w096r
        w097i=(ap*bt)*w096i
        w098r=w091r-w097r
        w098i=w091i-w097i
        w099r=(0.5_c_double)*0.0_c_double
        w099i=(0.5_c_double)*1.0_c_double
        w100r=w099r*(vt2)
        w100i=w099i*(vt2)
        w101r=w100r*w017r-w100i*w017i
        w101i=w100r*w017i+w100i*w017r
        w102r=w098r+w101r
        w102i=w098i+w101i
        w103r=(0.5_c_double)*w078r
        w103i=(0.5_c_double)*w078i
        w104r=(V)*w017r
        w104i=(V)*w017i
        w105r=w103r+w104r
        w105i=w103i+w104i
        w106r=pw%r*w017r-pw%i*w017i
        w106i=pw%r*w017i+pw%i*w017r
        acc_r(l,1)=acc_r(l,1)+w106r
        acc_i(l,1)=acc_i(l,1)+w106i
        w107r=pw%r*w105r-pw%i*w105i
        w107i=pw%r*w105i+pw%i*w105r
        acc_r(l,2)=acc_r(l,2)+w107r
        acc_i(l,2)=acc_i(l,2)+w107i
        w108r=pw%r*w090r-pw%i*w090i
        w108i=pw%r*w090i+pw%i*w090r
        acc_r(l,3)=acc_r(l,3)+w108r
        acc_i(l,3)=acc_i(l,3)+w108i
        w109r=pw%r*w102r-pw%i*w102i
        w109i=pw%r*w102i+pw%i*w102r
        acc_r(l,4)=acc_r(l,4)+w109r
        acc_i(l,4)=acc_i(l,4)+w109i
      end do
      !$omp end simd
      end if
    ! END GENERATED ARITHMETIC
    end do
    do l=1,size
      do k=1,4
        pos=2*((k-1)*nt*np+first+l)-1
        output(pos)=acc_r(l,k); output(pos+1)=acc_i(l,k)
      end do
    end do
  end subroutine
end module
