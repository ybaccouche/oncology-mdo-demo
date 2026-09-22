# MDO demo — build

Renders Simone's synthetic MdoPacket fixtures into a single self-contained HTML demo.

```
python3 build.py          # -> mdo-demo-v1.html
```

`mdo-demo-v1.html` is **committed on purpose**. It is a single file with no
external dependencies, so reviewers who don't run Python can open or preview it
directly. Re-run the build and commit the result whenever you change the
template or the data.

## Sharing

**Non-technical reviewers** — send them `mdo-demo-v1.html`. It is fully
self-contained: no external scripts, styles, fonts or images, no network calls,
no browser storage. That means it also renders correctly in OneDrive/SharePoint
in-browser preview, so a share link works without downloading.

**Anyone adapting it** — this repo. Everything needed to rebuild is here.

## Layout

```
mdo-demo/
  build.py           readiness rules, late-result variant, trials, cohort, schema validation
  template.html      UI (contains the /*__MDO_DATA__*/ marker the build fills in)
  mdo-demo-v1.html   build output — the shareable artefact
  data/              Simone's package, unpacked verbatim
    mdo_packets/     normalised MdoPacket fixtures  <- the app renders these
    fhir/            country-specific FHIR R4 source bundles (traceability only)
    schema/          canonical MdoPacket JSON Schema
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
> to Simone, since ECOG blocks both trial screening and cohort matching.

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

**Cohort.** Also not part of the dataset. 320 synthetic historic cases across six
hospitals, generated deterministically from seed 42. Decisions and outcomes are
biased by molecular profile, performance status and metastatic burden, including
a deliberate between-hospital difference in how M1a liver-limited disease is
handled — the variation clinicians raised on 13 Aug. The UI degrades honestly:
criteria the packet cannot answer are disabled and called out, and subgroups
under 15 cases are labelled too small to interpret.

## Voice copilot prototype

Use **Voice copilot** in the header to run Simone's voice-and-screen experiment.
The prototype keeps one case in context and supports:

- the opening question about review status and outcome;
- follow-ups about missing information and the radiology contribution;
- a two-voice radiologist / chief-of-staff exchange;
- automatic navigation to the supporting dashboard view;
- a microphone path where browser speech recognition is available;
- prompt buttons and typed input as a reliable fallback; and
- per-session attempt, screen-response and speech-start measurements.

All answers are deterministic and assembled from the selected synthetic packet.
The copilot explicitly distinguishes automated preparation from a recorded human
board decision and does not execute clinical or scheduling actions.

**Demo recommendation.** Run the prompt buttons or typed questions live because
they are deterministic and move the dashboard immediately. Treat browser
microphone recognition as optional: permissions, network policy and room noise
can make it unreliable. Keep a short screen recording as the fallback. Use the
specialist voice exchange only once to explain role separation; the single
chief-of-staff voice is faster and clearer for the rest of the demo.

## Guardrail

`packet.guardrails.noTreatmentAdvice` says the packets carry historical
treatment data only and provide no treatment recommendations. The UI honours
this: the **Board briefing** tab surfaces `decisionPoint.question` and splits
evidence into established / unresolved, the **cohort** layer is explicitly
descriptive rather than advisory, and the **patient summary** carries no
recommendation or prognosis and is marked as needing clinician approval. Nothing
in the UI proposes or ranks therapy.

## Data

All fixtures are synthetic and carry
`SYNTHETIC TEST DATA ONLY - NOT REAL PATIENT DATA`. No real patient information
is present anywhere in this repo.

## Open items

- Load the datasets into Fabric (outstanding on Simone's side).
- Replace `resolve_late_ct()` with the real mock API once available.
- Confirm whether `ecog: null` on DE-002 is intentional.
- Federation view — the three national FHIR flavours are the strongest
  differentiator in the data and are not yet visible on screen.
- Replace deterministic voice responses with Marcel's specialist-agent outputs
  after their input/output contract is agreed.
