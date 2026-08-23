# Future agentic layer

## Entry gate

Agents are added only after the mathematical core demonstrates stable, useful candidates against baselines on real data.

## Roles

| Agent | Input | Output |
|---|---|---|
| Investigation Agent | candidate and evidence | bounded investigation plan |
| Evidence Agent | approved questions | traceable evidence references |
| Hypothesis Agent | detected structure | explicit testable hypotheses |
| Critic Agent | hypothesis and evidence | counterexamples and alternatives |
| Forecast Explanation Agent | quantitative forecast | readable explanation without probability changes |

## Protocol

Every agent interaction must preserve:

hypothesis → evidence for → evidence against → testable prediction → rejection criterion.

## Authority boundary

Agents cannot:

- overwrite a numerical score or calibrated probability;
- remove failed predictions;
- promote a candidate to a discovery;
- make a regulated final decision;
- bypass access control, audit, or human review.

Agent agreement is not verification. Final status is determined by quantitative evidence, registered validation rules, and authorized human review.

## Future production concerns

A future implementation must include orchestration state, least-privilege tool access, prompt and model versioning, evidence provenance, audit trails, observability, fault tolerance, cost controls, and human escalation.

