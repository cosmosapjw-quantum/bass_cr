# CR PHYS06 | 물리적 광자 재순환의 종별 전하 장부

기준: Draft PR130 (HEAD da701cc06d207fde55b73d4cb0f9aca22a9d86b7), 원본 SOURCE SHA256 89fd528ede24929cb29b51b1edf55f27ad1ea1f7c0a61f976884ebe657e48cb3. 100K, fixed n_HI=138.6 m^-3, n_HeI=11.427127659574467 m^-3, PR125 실제 6400 photon energy atoms × 4 time bins, PR127 Verner (1996) σ.

각 source i와 target a에 대해 A_ia(T) = sum_{j,k} w_ijk [n_a sigma_a(E_ik)/sum_b n_b sigma_b(E_ik)] * [1-exp(-c (sum_b n_b sigma_b(E_ik)) (T-s_j))].

Source birth time s_j은 원래 구간 [l_j,r_j]에서 미지. 최종 T=1e10 s에서는 A_ia가 birth time에 단조 감소하므로 earliest/largest와 latest/smallest 선택으로 네 matrix entry의 sharp **common-witness** bounds를 얻는다.

화학적 장부:
Delta n_HI=R_H-A_H,HI-A_He,HI;
Delta n_HeI=R_He-A_He,HeI;
Delta n_e=-(R_H+R_He)+sum_ia A_ia=-N_gamma,surviving.
He-origin RR photon이 H를 이온화하는 경우 순 전자수 변화 0, 순 H↔He 이온 재배치가 일어난다. H photon은 HeI photoionization threshold에 미달하여 A_H,HeI=0.

에너지: absorbed photon E=target ionization I_a+initial photoelectron excess (E-I_a). 이것을 plasma heat/thermal deposition으로 해석하지 않는다.

출력: results/FINAL_PHOTON_RECYCLING_MATRIX.csv, results/PHYSICAL_RESULT.json, reproduce_matrix.py. 로컬 전체 source-inclusive archive에는 368 energy response rows, 27 globally consistent 9-time witness rows, 원본 complete ZIP, 15+15 tests 및 MP80 128 controls가 포함됨. 원격 Git에 binary 전체 아카이브 업로드는 성공하지 않았으며 file-bridge 오류를 따로 기록함.

Literature: Verner et al. ApJ 465,487 (1996), DOI 10.1086/177435; Switzer & Hirata PRD 77,083006 (2008), DOI 10.1103/PhysRevD.77.083006. Cross-species process is known; this is source-qualified scoped data, not a universal novelty claim or case A/B coefficient.

CENTRAL_DAG=28/88 (+0), EXTENSION_DAG=0/3 (+0), auxiliary=1/1 REVIEW_HOLD. Independent author R06/C09 NOT_RUN; actual exclusive He kernel, K, evolving density, cosmic transfer, native25, L4, production HOLD. Parent and main unchanged; Draft only, auto_next=false.
