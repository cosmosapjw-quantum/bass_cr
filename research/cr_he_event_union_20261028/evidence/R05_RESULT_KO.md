# R5 — 유한 원자 측도의 완결된 직접 증명

단위 CR_PHYS02_HE_EVENT_UNION_V1. 전체 유도는 [THEORY_KO.md](../theory/THEORY_KO.md)에 있다. 중앙 관찰22a99cb9b1691274e74c122d54521be4f2f51ba5의 **28/88**, 88 nodes/17 edges를 유지하며 이 단계의 집계 효과는 0이다.

## 증명 파일의 identity와 복원

해당 파일은 리셋 전에 실제 유도·독립 검토됐던 수학 내용을 대화에서 복원한 새 문서다. 손실된 파일과 byte-identical하다고 주장하지 않는다. 이번 게시 경로의 파일은 현재 복원본을 byte-identical하게 복사했다.

- 파일: theory/THEORY_KO.md
- 크기: 12,705 bytes
- 새 SHA256: 05002690eb9b08ef5297f88496ade941c3b363031a54adbdf31114e181b56918
- 복사 대응: ../intake/RECOVERY_COPY_RECEIPT.json

## 증명의 의존 관계

| 순서 | 명시한 전제 | 직접 얻은 결과 |
|---|---|---|
| 1 | 유한 electron atoms, nonnegative single S와 symmetric double D | μ=S+2π₁D 및 single/outside-partner/within-double 분해 |
| 2 | Disjoint birth-energy partitions | ν_U=Σνᵢ−C, δ_U=Σδᵢ−C, source species correction(+C,0,−C) |
| 3 | 고정 atomwise marginal nᵢ, N=Σnᵢ, M=maxnᵢ | Leg count의2C≤N과 largest-block complement의C≤N−M |
| 4 | All-single witness | 하한C=0 달성 |
| 5 | 질량 원에서 measure-preserving half-shift | 모든 질량 경우에서 상한min(N/2,N−M) 달성 |
| 6 | 같은 marginal의 convex mixture | [0,C_max]의 모든 값 달성 |
| 7 | 명시적 same-state n_b와 recipient binding convention | Native species 및 chemical bookkeeping correction |
| 8 | qⱼ(t)=tAⱼ와 proper [0,10¹⁰]s | 같은 coefficient-level witness를 F[a,b]=(b²−a²)/2로 scaling한 유한 history 일관성 |

Half-shift 증명은 N=0, largest block이 N/2 이하인 경우, 초과인 경우를 모두 포함한다. 이론의 계산 복잡도 주장은 sparse event records의 O(K) 개수로 제한한다. 정렬을 포함한 구현 시간까지 근거 없이 O(K)라고 하지 않는다.

## Source와 반환의 소유권

Source normalization은 기존 Aⱼ에 이미 포함됐으며 다시 곱하지 않는다. Proper exposure는 실제 구간의 적분이며 conditional mean time을 exposure로 쓰지 않는다. Cumulative prefix끼리는 겹치므로 더하지 않고 disjoint time bins만 합친다. Birth-energy partition과 observation-time bins를 섞지 않는다.

Selected electron marginal과 kinetic return은 그대로이고 source-ion event count만 union에 맞게 보정한다. RR, cutoff, Coulomb, retained photon port는 기존 소유권대로 한 번만 남는다. Chemical correction을 w_ext 또는 heating으로 보내지 않는다.

## 결론의 정확한 범위

이 정리는 유한 원자 nonnegative measure family의 sharp mathematical envelope다. Actual exclusive He event kernel, outside partner distribution, residual excitation, proton donor debit, physical EOS/T와 full-source physical native25를 결정하지 않는다. Missing actual input은 null이다. 일반 연속 측도 이론, 실제 산란 FDCS의 physical sharpness 또는 전체 문헌의 no-go까지 확장하지 않는다.

이 단계의 증거는 직접 유도와 scope가 맞는 기존 수학 검토의 재사용이다. 새로운 symbolic evaluator, science runtime 또는 numerical PASS를 이 문서 작성으로 선언하지 않는다. 독립 static 관찰과 후속 runtime의 구분은 R06_RESULT_KO.md에 있다.
