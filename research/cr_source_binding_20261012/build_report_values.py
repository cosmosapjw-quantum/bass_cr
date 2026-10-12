#!/usr/bin/env python3
"""Render report macros from the saved results without changing science data."""
from pathlib import Path
from decimal import Decimal
import json

r = Path(__file__).parent
d = json.loads((r / "results/SOURCE_BOUND_RESPONSE.json").read_text())
a, g, e = d["rows"][0], d["gas_calorimeter"], d["cumulative_energy_envelope"]
j = a["cutoff_thermal_join"]
values = {
 "HeatPower": a["heat_power_J_m3_s"], "HeatCumu": a["cumulative_heat_J_m3"],
 "SourcePower": d["source"]["q_star_J_m3_s"], "InjectedEnergy": d["source"]["selected_injected_energy_J_m3"],
 "PromptPowerError": a["prompt_power_absolute_error_J_m3_s"], "PromptCumuError": a["prompt_cumulative_absolute_error_J_m3"],
 "HeatCapacity": g["C_V_J_m3_K"], "CalorimetricDeltaT": a["calorimetric_delta_T_K"],
 "CalorimetricRate": a["calorimetric_heat_rate_K_s"], "ThermalJoinRate": j["local_Tdot_frozen_coeff_K_s"],
 "ThermalJoinDeltaT": j["linearized_delta_T_frozen_coeff_K"], "CapacityChange": j["heat_capacity_fractional_change"],
 "AllEnergy": e["all_secondary_injected_energy_J_m3"], "OutsideEnergy": e["omitted_birth_energy_J_m3"],
 "JoinOutsideUpper": e["cutoff_join_plus_all_omitted_delta_T_upper_K"],
 "AllSecondaryUpper": e["all_secondary_delta_T_upper_K"],
 "AllSecondaryRelative": e["all_secondary_upper_to_reference_thermal_energy_fraction"],
 "MaxRecordDifference": d["maximum_relative_readback_difference"],
}
def sci(v):
    m, power = f"{Decimal(v):.8E}".split("E")
    return r"\ensuremath{" + m + r"\times10^{" + str(int(power)) + "}}"
text = [r"\newcommand{\%s}{%s}" % (k, sci(v)) for k, v in values.items()]
for k, v in {"CheckCount": str(len(d["checks"])), "PromptPowerRatio": f'{Decimal(a["prompt_power_over_causal"]):.4f}', "PromptCumuRatio": f'{Decimal(a["prompt_cumulative_over_causal"]):.4f}'}.items():
    text.append(r"\newcommand{\%s}{%s}" % (k, v))
(r / "latex/result_macros.tex").write_text("\n".join(text) + "\n")
review = r / "review/DECISION.json"
if review.exists():
    dec = json.loads(review.read_text())
    status = str(dec.get("status", dec.get("decision", "SEE_REVIEW_DECISION"))).replace("_", r"\_")
    reference = dec["reference_execution"]
    reference_summary = str(reference["checks_passed"]) + r"개 PASS, " + str(reference["checks_failed"]) + r"개 실패, 종료 코드 " + str(reference["exit_code"])
    paragraph = r"독립 검토자의 최종 판정은 \texttt{" + status + r"}이다. 후보 구현을 호출하지 않은 별도 기준 계산은 " + reference_summary + r"를 기록했다. 실제 입력·코드·결과의 읽기 범위, 독립 실행 및 적용 조건은 \path{review/DECISION.json}과 \path{review/REVIEW_KO.md}에 보존한다. 승격 대상은 실제 source에 결속한 고정 배경 응답, 명시한 cutoff 열적 편입 및 누적 에너지 예산이다. 전체 REI 채택과 cutoff 물리의 정밀도는 이 판정의 범위 밖이다."
else:
    paragraph = r"현재 고정한 과학 후보는 독립 판정 중이다. 최종 산출물에는 실제 독립 판정과 수행한 검증 기록을 반영한다."
(r / "latex/review_status.tex").write_text(paragraph + "\n")
print(json.dumps({"status": "REPORT_MACROS_WRITTEN", "science_result_changed": False, "independent_decision_available": review.exists()}))
