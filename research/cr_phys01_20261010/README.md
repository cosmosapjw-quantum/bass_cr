# CR-PHYS01: conditional charged-particle provider

Read REPORT_KO.md and review/INDEPENDENT_REVIEW.json. Actual source, secondary
cascade response and native REI binding are implemented. Full causal IGM
history remains HOLD. See HANDOFF.json and DAG.json for parallel next units.

The combined Python provider imports the CRIPTIC-derived GPLv3 Rudd module;
src/GPL-3.0.txt and src/RUDD_NOTICE.md apply to that program. The acquired
21cmFAST table distribution retains its MIT notice. Existing repository lanes
and their licensing are not relabelled. The separate REI Rust receiver consumes
source-pinned numeric output and does not copy the GPL collision implementation.
