# CR-PHYS02-DELAY 독립 문헌 감사

작성: 2026-10-10. 역할: 문헌 취득·조건 확인·보조 수치 검산. 후보 설계 또는 최종 승격 판정은 수행하지 않았다.

## 확인한 실행 문맥

`harness/START_HERE.md`, `PROJECT_INSTRUCTIONS.md`, `docs/MODEL_ROUTING.md`, `state/RESEARCH_STATE.md`, `policies/EVIDENCE_AND_CITATION.md`, `prompts/phases/03_claim_source_audit.md`, `remote_cr_inventory/AGENTS.md`, `phys01_contract.json`, `phys01_handoff.json`을 읽었다. 하네스 state는 실행 전 템플릿이며 과거 연구 결과로 사용하지 않았다. 호스트 선언은 GPT-6 Astra이고 모델을 변경하지 않았다.

## 1. Furlanetto–Stoever: 실제 읽은 근거

- 원문: https://arxiv.org/pdf/0910.4410v1
- 서지: https://arxiv.org/abs/0910.4410v1
- 출판 DOI: https://doi.org/10.1111/j.1365-2966.2010.16401.x
- 실제 열람: arXiv v1 PDF pp. 2–5의 §§2–6.3, p. 10의 표/보간 코드 안내·참고문헌. PDF pp. 4–5는 이미지로 수식 확인. 출판 사이트는 본문 접근이 article-minimal로 전환되어 식 전체의 출판본 일치까지 검증하지 못했다.

**문헌 지지 요약 — literature-supported / supports·limits.** §2는 정적 매질에서 전자·광자의 최종 에너지 분배를 계산하며 10.2 eV 이하 잔량을 열로 처리한다. §6.1은 순간 침적 가정을 명시하고, 매질 이온화 상태가 빠르게 변하면 부적절할 수 있다고 경고한다. 식 (8)·(9)는 Coulomb/수소 이온화 손실의 규모 추정이며 전체 cascade 시간 분포가 아니다. §6.3은 반응률의 밀도 선형성 때문에 최종 분율이 거의 밀도 독립임을 설명한다. 시간 자체는 이 성질을 공유하지 않는다. §3·4의 1 keV는 CCC→Bethe 단면적 전환점이다. §6.3의 채택 식 (12)는 gas temperature를 입력하지 않는다. 따라서 프로젝트의 T=100 K를 FS10 MC의 확인된 입력으로 귀속시킬 수 없다. 식 (12)의 명시적 plasma-frequency 형태는 약 13.7 eV 이상 조건을 가지며, 이하 사용은 footnote 5에서 근사라고 밝힌다.

### 확인한 식과 SI 계산형

FS10 식 (5), Gaussian units:

\[
\frac{dE}{dt}=-\frac{4\pi e^4 n_e\ln\Lambda}{m_e v}.
\]

\(k_C=e^2/(4\pi\epsilon_0)\), \(E\) in J, \(n_e\) in m\(^{-3}\), \(v=\sqrt{2E/m_e}\)로 두면 동일한 SI 표현은

\[
b_C(E)\equiv-\dot E=\frac{4\pi k_C^2 n_e\ln\Lambda}{m_e v},\qquad [b_C]={\rm J\,s^{-1}}.
\]

FS10 식 (12)의 첫 표현을 SI로 변환하면

\[
\ln\Lambda_q=\ln\frac{2E}{\hbar\omega_p},\qquad
\omega_p=\sqrt{\frac{n_e e^2}{\epsilon_0m_e}}.
\]

식 (8), (9):

\[
t_{\rm loss,e}\sim5\times10^3x_i^{-1}
\left(\frac{E}{\mathrm{keV}}\right)^{3/2}
\left(\frac{1+z}{10}\right)^{-3}\mathrm{yr},
\]

\[
t_{\rm loss,H}\sim5\times10^5x_H^{-1}
\left(\frac{E}{\mathrm{keV}}\right)^{3/2}
\left(\frac{1+z}{10}\right)^{-3}\mathrm{yr},\qquad x_H=1-x_i.
\]

H 식은 Bethe 단면적과 interaction당 약 13.6 eV 손실을 사용하고 logarithmic factor를 1 keV에서 평가한 규모 추정이다. 13.6 eV 근방으로 외삽하여 유한 손실시간을 얻는 용도로는 부적합하다. 국소 손실시간 \(E/b_C\), 전자 한 개의 CSDA 정지시간 \(\int dE/b_C\), 분기 cascade의 채널별 지연시간은 구별해야 한다.

### 원문 식의 내부 불일치 — derived / limits

arXiv v1 식 (12)는 \(\ln(2E/\hbar\omega_p)\equiv\ln(4E/\zeta_e)\)라 쓴 다음 \(\zeta_e=7.40\times10^{-11}(n_e/\mathrm{cm}^{-3})\,\mathrm{eV}\)를 제시한다. 그러나 앞의 명시적 식으로부터

\[
\zeta_e=2\hbar\omega_p\propto\sqrt{n_e}
\]

이어야 하므로 두 표현은 일치하지 않는다. 올바른 대수적 환산계수는 약 \(7.43\times10^{-11}\sqrt{n_e/\mathrm{cm}^{-3}}\,\mathrm{eV}\)다. 이번 보조 검산은 첫 plasma-frequency 표현만 사용했다. 이는 공개된 MC가 실제 어떤 코드를 실행했는지를 입증하거나 기존 FS10 table을 수정할 근거가 아니다. 식 (11)도 인쇄된 `ln Λ = sqrt(...)`에 전사상 문제가 있어 계산 근거로 채택하지 않았다.

## 2. Khrapak: 저에너지 classical stopping 근거와 한계

- 원문: https://arxiv.org/pdf/2006.00128v1
- 서지: https://arxiv.org/abs/2006.00128v1
- 출판: Phys. Rev. E **101**, 061202 (2020), https://doi.org/10.1103/PhysRevE.101.061202
- 실제 열람: v1 PDF pp. 1–3, 특히 식 (4)–(6), 식 (11), 가정 설명. 원문 발견은 root가 제공했고, 이 감사자는 별도로 열람하였다.

**문헌 지지 요약 — literature-supported / supports·limits.** 이 논문은 immobile neutralizing background 안의 ideal electron gas에서 classical, superthermal test electron의 stopping을 구한다. 식 (6)은 neutral-collision frequency \(\nu<\omega_p\), 넓은 파수 간격, 큰 Coulomb logarithm을 전제한다. 감속이 induced force 자체에 주는 효과는 제외한다. 전자–이온 momentum transfer와 완전한 thermalization operator도 계산하지 않는다. 식 (11)의 binary momentum-force 추정 계수는 \(8\pi\)이고 식 (6)의 stopping 계수는 \(4\pi\)이므로 다른 양을 섞어 계수를 바꾸면 안 된다.

Gaussian 식 (6):

\[
F_{\rm st}=\frac{4\pi e^4n_e}{m_ev^2}
\ln\left(\frac{v}{\omega_p\rho_0}\right),\qquad
\rho_0=\frac{e^2}{\mu v^2},\quad \mu=m_e/2.
\]

SI에서는 \(\rho_0=k_C/E\), 따라서

\[
\ln\Lambda_{\rm cl}=\ln\left(\frac{vE}{k_C\omega_p}\right),\qquad
b_{\rm cl}(E)=vF_{\rm st}=
\frac{4\pi k_C^2n_e}{m_ev}\ln\Lambda_{\rm cl}.
\]

이 식은 선택한 classical leading-log stopping closure의 근거가 될 수 있다. 다만 T=100 K에서 \(E_{\rm cut}=0.1\,\mathrm{eV}\)는 \(E/k_BT\simeq11.6\)이며 완전한 열화 상태가 아니다. 또한 \(k_C/(\hbar v)=\sqrt{\mathrm{Ry}/E}\)는 10 eV에서 약 1.17뿐이다. 따라서 10 eV를 포함하는 전 구간에 강한 classical asymptotic scale separation이 있다고 주장할 수 없다. 이 두 점은 직접 계산한 적용 조건 점검이며 논문이 제공한 수치 오차 보장이 아니다. 경계 아래의 잔류 에너지는 별도 ledger로 남겨야 한다.

**계수의 별도 운동학 검산 — derived.** 정지한 동종 target electron과의 탄성 산란에서 center-of-mass 산란각을 \(\chi\)라 하면 incident electron의 손실은 \(\Delta p_\parallel=(m_ev/2)(1-\cos\chi)\), \(\Delta E=(m_ev^2/4)(1-\cos\chi)\)이다. 따라서 이 binary momentum-transfer 양에 대해서는 \(\Delta E=(v/2)\Delta p_\parallel\)다. 그러므로 식 (11)의 \(8\pi\) momentum-transfer 추정에서 에너지율로 바꿀 때 \(v/2\)를 곱하면 \(4\pi\)가 되어 식 (6)의 \(vF_{\rm st}\) 및 FS10 식 (5)의 계수와 일치한다. 이 관찰은 논문의 서로 다른 양을 구별하는 직접 검산이며 전체 Fokker–Planck operator의 검증은 아니다.

## 3. Inelastic collision 데이터의 primary source 경로

### CCC 공식 DB — literature-supported / contextual

https://atom.curtin.edu.au/CCC-WWW/

실제 열람: 공식 landing page 전체. FS10이 사용했다고 명시한 원천이지만 현재 H I, He I, He II archive는 각각 2026년 갱신 데이터라고 표시된다. 현재 파일을 취득해도 FS10 계산 당시 bytes를 복구한 것은 아니다. ZIP 내부의 table, 단위, 수치값은 이번 감사에서 취득·검증하지 않았다. 연결된 H 원 논문 DOI는 https://doi.org/10.1103/PhysRevA.46.6995 이고 초록까지만 읽었다.

### NIST electron-impact DB — literature-supported / contextual

- 설명: https://physics.nist.gov/PhysRefData/Ionization/intro.html
- 정확한 수식: https://physics.nist.gov/PhysRefData/Ionization/Eqs/latex.html
- H: https://physics.nist.gov/cgi-bin/Ionization/atom.php?element=H
- He: https://physics.nist.gov/cgi-bin/Ionization/atom.php?element=He
- 원 model reference: Kim & Rudd, PRA **50**, 3954–3967 (1994), https://doi.org/10.1103/PhysRevA.50.3954

실제 열람: 공식 설명문과 LaTeX 식 (1)–(6), H·He species page. H/He threshold는 각각 13.5984/24.5874 eV다. BEB total 및 BED singly differential cross section의 정의·단위 변환을 제공한다. Total data endpoints는 HTTP 500으로 실패하여 실제 table 수치나 orbital parameter를 취득하지 않았다. NIST 모델은 CCC 데이터와 구별해야 한다. 이 원천을 사용한 새로운 collision clock은 별도 source admission이 필요하다.

## 4. 시간율 정의와 현재 근거의 정확한 범위

**정의/직접 유도.** Cold target에서 단면적 \(\sigma_s(E)\)의 event rate는

\[
\nu_s(E)=n_s v(E)\sigma_s(E),\qquad
t_{\rm event}=\left(\sum_s\nu_s\right)^{-1}.
\]

\([n_s]={\rm m^{-3}}\), \([v]={\rm m\,s^{-1}}\), \([\sigma_s]={\rm m^2}\)이면 \([\nu_s]={\rm s^{-1}}\)다. 이온화에서 incident electron의 에너지 감소에는 binding energy와 ejected kinetic energy가 둘 다 들어간다. ejected kinetic energy는 다른 전자에 남으므로 그 자체를 열로 세면 이중 계산이다. Event clock과 channel energy deposition은 별개 양이다.

Terminal yield만으로 얻는 것은 시간 적분이다. 매질 밀도를 바꾸면 rate clock이 달라지지만 terminal branching ratios는 거의 같을 수 있다. 그러므로 density-insensitive terminal yield에서 지연시간을 역으로 복원할 수 없다. Exponential lag의 도입은 별도 가정이며 FS10 표 자체의 측정 또는 유도가 아니다.

`coulomb_timescale_diagnostic.json`은 root가 지정한 \(n_e=1.5154\,\mathrm{m^{-3}}\)에 FS10 식 (5)·(12)를 SI로 적용한 **Coulomb-only 국소 규모 검산**이다. 100 eV / 1 keV / 4 keV에서 \(E/b_C\)는 약 \(7.51\times10^4\), \(2.23\times10^6\), \(1.72\times10^7\) yr다. 식 (8)의 거친 prefactor와 일치하는 정밀 결과로 주장하지 않는다. Inelastic loss를 포함한 총 손실시간이나 source-weighted cascade delay는 여기서 계산하지 않았다.

## 5. 접근 실패를 보존한 원천

- Schunk & Hays (1971), DOI https://doi.org/10.1016/0032-0633(71)90071-7 : publisher HTML/PDF HTTP 403. U Michigan 원문 https://deepblue.lib.umich.edu/bitstream/2027.42/33734/1/0000248.pdf 접근 불가. 본문을 읽었다고 주장하지 않는다.
- 저에너지 후속 note의 원문 https://deepblue.lib.umich.edu/bitstream/2027.42/33736/1/0000251.pdf 역시 접근 불가.
- Varney et al. (2012), https://doi.org/10.1029/2011JA017280 : §3의 thermal-electron collision discussion은 열람하였다. 이온층용 empirical Swartz formula의 저밀도 IGM 적용범위는 검증하지 않아 이번 채택 근거에 넣지 않았다.

이 노트는 source-specific 모델의 조건을 명료화한다. 실제 Qe 가중 유한시간 계산과 그 독립 판정은 root의 별도 산출물이다.
