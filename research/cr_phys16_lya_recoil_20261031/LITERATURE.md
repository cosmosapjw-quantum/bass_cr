# PHYS16 문헌 소유권과 필요한 원전

## 직접 사용하거나 경계 설정에 필요한 원전

1. Kingston, A. E., Fon, W. C. & Burke, P. G. (1976), "The 1s–2s and 1s–2p excitation of atomic hydrogen by electron impact," *Journal of Physics B* **9**, 605–618, DOI [10.1088/0022-3700/9/4/010](https://doi.org/10.1088/0022-3700/9/4/010). 13–300 eV의 close-coupling/uniterized Born 혼합 total & differential 계산. **이번 계산에는 이 논문의 본문 DCS 수치표를 새 원자 입력으로 재사용하지 않았다.** Born model을 14.6–21 eV에서 검증할 다음 직접 후보.
2. Williams, J. F. (1976), "The 2S and 2P state excitation of atomic hydrogen by electron impact," *Journal of Physics B* **9**, 1519–1527, DOI [10.1088/0022-3700/9/9/017](https://doi.org/10.1088/0022-3700/9/9/017). 13.87, 16.46, 19.58 eV 근접 threshold n=2 state differential measurements, 2s/2p prompt/delayed radiation separation. 어떤 angular data가 명시적으로 2p-resolved인지 논문 표를 확인해야 한다.
3. Williams, J. F. & Willis, B. A. (1975), "Electron scattering from atomic hydrogen. I. Differential cross sections for excitation of the n=2 states," *Journal of Physics B* **8**, 1641–1669, DOI [10.1088/0022-3700/8/10/016](https://doi.org/10.1088/0022-3700/8/10/016). 54–680 eV 실측이므로 14.6–21 eV 직접 데이터로 취급하면 안 된다.
4. James, G. K., Slevin, J. A., Shemansky, D. E. et al. (1997), "Optical excitation function of H(1s–2p) produced by electron impact from threshold to 1.8 keV," *Physical Review A* **55**, 1069, DOI [10.1103/PhysRevA.55.1069](https://doi.org/10.1103/PhysRevA.55.1069). 실측 prompt Lyα 총 여기 cross section 및 CCC 비교. 각도분해 DCS 아님. [NASA NTRS PDF](https://ntrs.nasa.gov/api/citations/19980111017/downloads/19980111017.pdf).
5. Stone, P. M., Kim, Y.-K. & Desclaux, J. P. (2002), "Electron-impact cross sections for dipole- and spin-allowed excitations of hydrogen, helium, and lithium," *Journal of Research of NIST* **107**, 327, DOI [10.6028/jres.107.026](https://doi.org/10.6028/jres.107.026). 원 PHYS14 NIST BE scaled cross section. 적분 total이며 low-energy angular shape 입력이 아니다.
6. Wiese, W. L. & Fuhr, J. R. (2009), "Accurate atomic transition probabilities for hydrogen, helium, and lithium," *Journal of Physical and Chemical Reference Data* **38**, 565, DOI [10.1063/1.3077727](https://doi.org/10.1063/1.3077727): `A21=6.2649e8/s`, `f≈0.41641` 재사용, 2p-specific rate와 shell-averaged n=2를 구분.
7. Hummer, D. G. (1962), "Non-coherent scattering: I. The redistribution function with Doppler broadening," *MNRAS* **125**, 21–37, DOI [10.1093/mnras/125.1.21](https://doi.org/10.1093/mnras/125.1.21). R_II foundational derivation; [원본 ADS PDF](https://adsabs.harvard.edu/pdf/1962MNRAS.125...21H).
8. Rybicki, G. B. (2006), "Improved Fokker-Planck equation for resonance-line scattering," *ApJ* **647**, 709, DOI [10.1086/505327](https://doi.org/10.1086/505327). Corrected detailed balance with recoil and stimulated scattering. 이번 simplified one-scatter kernel의 detailed balance는 별도 검증 대상이다.
9. Meiksin, A. A. (2006), "Energy transfer by the scattering of resonant photons," *MNRAS* **370**, 2025, DOI [10.1111/j.1365-2966.2006.10632.x](https://doi.org/10.1111/j.1365-2966.2006.10632.x). Energy transfer and non-stationary relaxation, exact redistribution formalism.
10. Hirata, C. M. & Forbes, J. C. (2009), "Lyman-alpha transfer in primordial hydrogen recombination," *Phys. Rev. D* **80**, 023001, DOI [10.1103/PhysRevD.80.023001](https://doi.org/10.1103/PhysRevD.80.023001). Full time-dependent transfer with resonant scattering, recoil, true emission/absorption and cosmological expansion; NOT directly reproduced.

## 추가 입력 요청 및 접근

- 우선순위 1: Kingston–Fon–Burke 1976의 `dσ_{1s→2p}(E,θ)/dΩ` 수치표 또는 각도별 그래프의 정식 원본(저자 계산 자료/출판사 PDF). E=14.6–21.0 eV 구간에서 최소 3~5 에너지점, θ는 0–180° 전체와 integral/normalization provenance. DOI 랜딩 페이지에서 소속기관 접근, IOP 이용권 또는 저자 문의. 그림 digitization은 단위·정규화·추출 오차를 별도 기록.
- 우선순위 2: Williams 1976의 13.87/16.46/19.58 eV 측정 데이터 원문(특히 n=2와 2p-resolved 혼동 회피), DOI 10.1088/0022-3700/9/9/017. 실측 DCS 교차검증. 중간/고에너지의 Williams–Willis 1975 자료를 near-threshold로 대체하지 않는다.
- 우선순위 3: 전이 density matrix 혹은 polarization/angular correlation for electron-excited H 2p at E≈15–21 eV (Stokes, magnetic sublevels), 이후 도입하면 현재 E1 q-alignment closure를 교정한다.
- 독립 라인 재분배: Hummer1962 RII 코드/공식, Rybicki2006 상세 평형 정식화와 Lyα fine-structure/spin kernels. 특정 데이터 표가 없으면 조건부 모델만 유지한다.

기존 원본 논문의 복사본을 공개 저장소에 무단 재배포하지 않는다. 사용자가 원본 PDF 또는 공식 데이터 URL을 제공할 경우 source SHA, 해당 표/fig와 읽기 조건을 새 provenance로 기록한다.
