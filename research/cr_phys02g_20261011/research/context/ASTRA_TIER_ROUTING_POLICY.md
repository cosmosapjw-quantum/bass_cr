# Astra tier-routing policy

Owner policy, effective 2026-10-10. This is a project harness rule for new
bounded work; it does not reinterpret historical receipts or authorize a wider
scientific claim.

## Roles

| Work class | Owner tier | Required handoff state |
| --- | --- | --- |
| Theory, source/domain research, DAG choice, model/interface choice, acceptance contract, blocker classification | Astra | Frozen bounded contract or typed HOLD |
| Independent numerical/physics/code review, publication and admission decision | Astra independent of implementation | Scoped review finding |
| Contract-preserving implementation, targeted tests, evidence assembly, routine reports/DAG status, one pre-authorized repair execution | Lower tier | Exact contract, inputs, limits, acceptance rows |

The lower tier may make no new physical/model choice. It must return to Astra
before acting if an input identity is absent, a source or fit domain is crossed,
a tolerance/acceptance row must change, an ambiguous channel mapping appears,
the first failure needs more than one pre-authorized repair, or scope would
expand.

## Required execution sequence

1. Astra writes or approves a finite contract: exact inputs, claim ceiling,
   code ownership, solver/call/wall limits, validation rows, and at most one
   targeted repair rule.
2. A lower-tier worker implements only that contract and preserves the first
   failure. It returns source/code/evidence identities and a typed result.
3. Astra reviews independently. `PASS_SCOPED` advances only the named DAG node;
   a typed HOLD blocks descendants, not unrelated READY work.
4. A lower-tier worker may prepare bounded publication artifacts after Astra's
   review; Astra owns the final publication/admission decision. The controller
   then refreshes live refs and selects the next READY node.

## Cost and escalation rule

Do not use Astra for routine code typing, test repetition, report formatting,
or ordinary commit preparation when the contract is closed. Do not compensate
by letting a lower tier infer physics or relax a gate. If implementation reveals
an unknown, stop immediately and escalate one concise evidence-backed question
to Astra. Record the assigned role in the unit's contract or run state.

## Non-exceptions

This policy does not weaken frozen source identity, numerical validity,
independent review, scientific claim boundaries, dirty-worktree preservation,
or non-force publication rules. It is a routing rule, not a model/runtime
identity claim.
