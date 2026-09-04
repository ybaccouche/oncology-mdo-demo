# MDO demo — build

Renders Simone's synthetic MdoPacket fixtures into a single self-contained HTML demo.

```
python3 build.py          # -> ../mdo-demo-v1.html
```

## Layout

```
mdo-demo/
  build.py        readiness rules, late-result variant, trial screening, schema validation
  template.html   UI (contains the /*__MDO_DATA__*/ marker the build fills in)
  data/           Simone's package, unpacked verbatim
    mdo_packets/  normalised MdoPacket fixtures  <- the app renders these
    fhir/         country-specific FHIR R4 source bundles (traceability only)
    schema/       canonical MdoPacket JSON Schema
    documentation/research-standards.md
```

## Swapping in a new dataset

Replace `data/` and re-run `python3 build.py`. The renderer is generic over the
schema, so no UI changes are needed unless the schema itself changes. The build
validates every packet (including the generated late-result variant) against
`data/schema/mdo_packet.schema.json` when `jsonschema` is installed.

## What the build derives

**Readiness score.** The packet carries a binary `readinessState` plus a
`missingData` array. To rank "attention-needed" cases against each other the
build also scores ten evidence items a colorectal board needs: pathology, TNM,
KRAS, NRAS, BRAF, MSI/MMR, ECOG, current CEA, final+current imaging, and
treatment history. Failures that are **not** listed in `packet.missingData` are
tagged `derived` in the UI.

> DE-002 carries `"ecog": null`. It is schema-valid, but it is not listed in
> that packet's `missingData`. The readiness rules catch it — worth feeding back
> to Simone, since ECOG blocks trial screening.

**Late-result variant (IT-003).** The checked-in Italian fixture is the initial
`result-pending` state; the README says the working mock API can simulate CT
arrival. `resolve_late_ct()` reproduces that second state locally: imaging goes
`final` + current with an `arrivedDate`, a `lateResults` entry is added,
`missingData` clears, and `readinessState` flips to `ready-for-review`. The
result is schema-valid. Swap this for a real mock-API call when it is wired up.

**Trial screening.** Not part of the dataset — an illustrative layer, labelled
as such in the UI. Eligibility is evaluated only against molecular markers,
performance status and imaging currency present in the packet, and returns
*cannot evaluate* whenever the driving field is untested or pending.
Interventional studies additionally require measurable disease on final, current
imaging; that is what flips IT-003 from 0 to 2 eligible when the CT lands.

## Guardrail

`packet.guardrails.noTreatmentAdvice` says the packets carry historical
treatment data only and provide no treatment recommendations. The UI honours
this: the **Board briefing** tab surfaces `decisionPoint.question` and splits
evidence into established / unresolved. It never proposes or ranks therapy.

## Open items

- Load the datasets into Fabric (outstanding on Simone's side).
- Replace `resolve_late_ct()` with the real mock API once available.
- Confirm whether `ecog: null` on DE-002 is intentional.
