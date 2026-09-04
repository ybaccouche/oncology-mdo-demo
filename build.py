#!/usr/bin/env python3
"""
Build the single-file MDO demo from Simone's synthetic MdoPacket fixtures.

    python3 build.py

Reads   : data/mdo_packets/*.json   (canonical MdoPacket fixtures)
          data/schema/mdo_packet.schema.json
Writes  : ../mdo-demo-v1.html       (self-contained, no network calls)

When a new dataset drops, replace data/ and re-run. Nothing else changes.
"""

import json
import pathlib
import re
import sys
import copy
from datetime import date

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "mdo_packets"
SCHEMA = ROOT / "data" / "schema" / "mdo_packet.schema.json"
TEMPLATE = ROOT / "template.html"
OUT = ROOT / "mdo-demo-v1.html"

# Display order on the worklist is derived (least ready first), but this fixes
# the canonical case order and the short labels used in the UI.
LABELS = {
    "synthetic-mcrc-NL-001": {"short": "NL-001", "flag": "\U0001F1F3\U0001F1F1", "country": "Netherlands"},
    "synthetic-mcrc-DE-002": {"short": "DE-002", "flag": "\U0001F1E9\U0001F1EA", "country": "Germany"},
    "synthetic-mcrc-IT-003": {"short": "IT-003", "flag": "\U0001F1EE\U0001F1F9", "country": "Italy"},
}

# --------------------------------------------------------------------------
# Readiness rules.
#
# The MdoPacket carries a binary readinessState plus a missingData array. For
# the worklist we also derive a completeness score from the evidence a
# colorectal board actually needs, so that "attention-needed" cases can be
# ranked against each other. Each rule returns (passed, detail).
# --------------------------------------------------------------------------

REQUIRED = [
    ("Pathology report", lambda p: (
        bool(p.get("pathology", {}).get("reportDate")),
        "%s, %s (%s)" % (
            p["pathology"].get("histology", "?"),
            p["pathology"].get("site", "?"),
            p["pathology"].get("reportDate", "?"),
        ) if p.get("pathology") else "Absent",
    )),
    ("Clinical stage (TNM)", lambda p: (
        bool(p.get("stage", {}).get("tnm", {}).get("combined")),
        "%s %s, stage group %s" % (
            p["stage"]["system"], p["stage"]["tnm"]["combined"], p["stage"]["stageGroup"],
        ) if p.get("stage") else "Absent",
    )),
    ("KRAS", lambda p: _marker(p, "kras")),
    ("NRAS", lambda p: _marker(p, "nras")),
    ("BRAF", lambda p: _marker(p, "braf")),
    ("MSI / MMR", lambda p: _marker(p, "msi")),
    ("ECOG performance status", lambda p: (
        p.get("ecog") is not None,
        ("ECOG %s (%s)" % (p["ecog"]["score"], p["ecog"]["date"]))
        if p.get("ecog") else "Not recorded in the packet — ecog is null",
    )),
    ("CEA, current", lambda p: (
        bool(p.get("labs", {}).get("cea", {}).get("isCurrent")),
        "%s %s (%s)%s" % (
            p["labs"]["cea"]["value"], p["labs"]["cea"]["unit"], p["labs"]["cea"]["date"],
            "" if p["labs"]["cea"]["isCurrent"] else " — not current",
        ) if p.get("labs", {}).get("cea") else "Absent",
    )),
    ("Imaging, final and current", lambda p: _imaging(p)),
    ("Treatment history", lambda p: (
        len(p.get("treatmentTimeline", [])) > 0,
        "%d line(s) recorded" % len(p.get("treatmentTimeline", [])),
    )),
]

OK_MARKER = {"detected", "not-detected"}


def _marker(p, key):
    m = p.get("molecularProfile", {}).get(key)
    if not m:
        return False, "Absent"
    st = m.get("status")
    detail = m.get("interpretation") or st
    return st in OK_MARKER, "%s (%s)" % (detail, m.get("date", "?"))


def _imaging(p):
    imgs = p.get("imaging") or []
    if not imgs:
        return False, "Absent"
    cur = [i for i in imgs if i.get("status") == "final" and i.get("isCurrent")]
    if cur:
        i = cur[0]
        return True, "%s %s — %s" % (i["type"], i["date"], i["summary"])
    i = imgs[0]
    return False, "%s %s — %s (%s)" % (i["type"], i["date"], i["summary"], i.get("status"))


def readiness(p):
    checks = []
    for name, fn in REQUIRED:
        ok, detail = fn(p)
        checks.append({"name": name, "ok": ok, "detail": detail})
    passed = sum(1 for c in checks if c["ok"])
    return {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "score": round(100 * passed / len(checks)),
    }


# --------------------------------------------------------------------------
# Late-result variant for the Italian case.
#
# The checked-in IT-003 fixture is the initial `result-pending` state. Simone's
# README says the working mock API can simulate CT arrival and regenerate the
# ready-for-review view; this reproduces that second state locally so the demo
# can show the transition without the API.
# --------------------------------------------------------------------------

CT_SUMMARY = (
    "Progressive peritoneal disease with new omental nodularity and a small volume of "
    "ascites. Hepatic parenchyma unremarkable. No thoracic metastases. "
    "Overall response category: progressive disease."
)


def resolve_late_ct(p):
    r = copy.deepcopy(p)
    img = r["imaging"][0]
    citation = img["sourceCitation"]
    img.update({
        "status": "final",
        "isCurrent": True,
        "arrivedDate": "2026-08-28",
        "summary": CT_SUMMARY,
    })
    r["lateResults"] = [{
        "item": img["type"],
        "orderedDate": "2026-08-01",
        "arrivedDate": "2026-08-28",
        "arrivalTimestamp": "2026-08-28T09:14:00Z",
        "summary": CT_SUMMARY,
        "sourceCitation": citation,
    }]
    r["missingData"] = []
    r["readinessState"] = {
        "status": "ready-for-review",
        "reason": "CT chest/abdomen/pelvis resulted 2026-08-28; restaging complete",
        "sourceCitations": [citation],
        "derivedFrom": [citation["resourceId"]],
    }
    r["decisionPoint"] = dict(r["decisionPoint"], type="restaging")
    return r


# --------------------------------------------------------------------------
# Illustrative trial layer.
#
# NOT part of the 2026-08-27 dataset. Eligibility is evaluated only against
# molecular markers and performance status that are present in the packet, and
# is reported as "cannot evaluate" whenever the driving marker is untested or
# pending. No treatment is recommended.
# --------------------------------------------------------------------------

TRIALS = [
    {
        "id": "NCT-SYN-2210",
        "title": "BRAF V600E-directed combination in previously treated mCRC",
        "phase": "Phase II",
        "sites": "Munich, Utrecht",
        "marker": "braf",
        "wants": "detected",
        "criteria": "BRAF variant detected; ECOG 0-2; \u22651 prior systemic line; measurable disease on current imaging.",
    },
    {
        "id": "NCT-SYN-3390",
        "title": "Checkpoint inhibition in mismatch-repair deficient colorectal cancer",
        "phase": "Phase III",
        "sites": "Multi-site EU",
        "marker": "msi",
        "wants": "detected",
        "criteria": "MSI-H / dMMR confirmed; ECOG 0-2; measurable disease on current imaging.",
    },
    {
        "id": "NCT-SYN-4471",
        "title": "KRAS-selective inhibitor added to standard doublet chemotherapy",
        "phase": "Phase I/II",
        "sites": "Utrecht, Amsterdam",
        "marker": "kras",
        "wants": "detected",
        "criteria": "KRAS variant detected; ECOG 0-1; measurable disease on current imaging.",
    },
    {
        "id": "NCT-SYN-7714",
        "title": "All-RAS/BRAF wild-type mCRC observational cohort",
        "phase": "Observational",
        "sites": "Netherlands",
        "marker": "allwt",
        "wants": "detected",
        "criteria": "No KRAS, NRAS or BRAF variant detected; any ECOG.",
    },
]


def match_trials(p):
    mp = p.get("molecularProfile", {})
    ecog = p.get("ecog")
    imgs = p.get("imaging") or []
    # Interventional trials require measurable/evaluable disease documented on
    # current imaging. Observational cohorts do not.
    imaging_current = any(i.get("status") == "final" and i.get("isCurrent") for i in imgs)
    out = []

    for t in TRIALS:
        if t["marker"] == "allwt":
            sts = [mp.get(k, {}).get("status") for k in ("kras", "nras", "braf")]
            if any(s not in OK_MARKER for s in sts):
                verdict, why = "blocked", "Cannot evaluate — one or more of KRAS/NRAS/BRAF is not resulted."
            elif all(s == "not-detected" for s in sts):
                verdict, why = "eligible", "All-RAS and BRAF wild-type confirmed in the packet."
            else:
                verdict, why = "inelig", "Excluded — a RAS or BRAF variant is detected."
        else:
            st = mp.get(t["marker"], {}).get("status")
            if st not in OK_MARKER:
                verdict = "blocked"
                why = "Cannot evaluate — %s status is '%s' in the packet." % (t["marker"].upper(), st)
            elif st == t["wants"]:
                verdict, why = "eligible", "%s %s in the packet." % (t["marker"].upper(), st)
            else:
                verdict, why = "inelig", "Excluded — %s is %s." % (t["marker"].upper(), st)

        # performance-status, imaging and measurability gates, only where they bite
        if verdict == "eligible":
            interventional = t["phase"] != "Observational"
            if ecog is None:
                verdict, why = "blocked", "Cannot evaluate — ECOG performance status is not recorded."
            elif interventional and not imaging_current:
                verdict, why = ("blocked",
                                "Cannot evaluate measurable disease — no final, current imaging in the packet.")
            elif t["id"] == "NCT-SYN-4471" and ecog["score"] > 1:
                verdict, why = "inelig", "Excluded — trial requires ECOG 0-1, packet records ECOG %d." % ecog["score"]

        out.append(dict(t, verdict=verdict, why=why))
    return out


# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Synthetic historic cohort.
#
# NOT part of the 2026-08-27 dataset. An illustrative "patients like this one"
# layer, labelled as such in the UI. Generated deterministically from the same
# seed the fixtures use so the demo is reproducible. Decisions and outcomes are
# biased by molecular profile, performance status and metastatic burden so the
# distributions say something rather than being noise — including a deliberate
# between-hospital difference in how M1a liver-limited disease is handled,
# which is the variation clinicians raised in the 13 Aug working session.
# --------------------------------------------------------------------------

COHORT_SIZE = 320

COHORT_HOSPITALS = [
    ("Hospital-NL-1", "Netherlands"),
    ("Hospital-NL-2", "Netherlands"),
    ("Hospital-DE-1", "Germany"),
    ("Hospital-IT-1", "Italy"),
    ("Hospital-SE-1", "Sweden"),
    ("Hospital-BE-1", "Belgium"),
]

# (ras, braf, msi) -> relative frequency
MOL_MIX = [
    (("wt", "wt", "MSS"), 32),
    (("mut", "wt", "MSS"), 38),
    (("wt", "mut", "MSS"), 8),
    (("wt", "wt", "MSI-H"), 6),
    (("wt", "mut", "MSI-H"), 5),
    (("mut", "wt", "MSI-H"), 4),
    (("mut", "mut", "MSS"), 2),
]

SITES_RIGHT = ["caecum", "ascending colon", "transverse colon"]
SITES_LEFT = ["descending colon", "sigmoid colon", "rectosigmoid junction", "rectum"]

DECISIONS = [
    "Systemic therapy - doublet",
    "Systemic therapy - triplet",
    "Targeted combination",
    "Checkpoint inhibitor",
    "Metastasectomy / surgery",
    "Local ablation",
    "Enrolled in trial",
    "Additional diagnostics first",
    "Best supportive care",
]

OUTCOMES = ["Complete response", "Partial response", "Stable disease", "Progressive disease", "Not evaluable"]


def _pick(rnd, weighted):
    total = sum(w for _, w in weighted)
    x = rnd.uniform(0, total)
    acc = 0
    for item, w in weighted:
        acc += w
        if x <= acc:
            return item
    return weighted[-1][0]


def _decision_weights(mol, ecog, m_cat, hospital):
    ras, braf, msi = mol
    w = {d: 1 for d in DECISIONS}
    w["Systemic therapy - doublet"] = 22
    w["Systemic therapy - triplet"] = 8
    w["Additional diagnostics first"] = 4
    w["Local ablation"] = 3
    w["Enrolled in trial"] = 4

    if msi == "MSI-H":
        w["Checkpoint inhibitor"] = 30
        w["Systemic therapy - doublet"] = 8
    if braf == "mut":
        w["Targeted combination"] = 22
        w["Systemic therapy - triplet"] = 12
    if ecog >= 2:
        w["Best supportive care"] = 12
        w["Systemic therapy - triplet"] = 2
        w["Metastasectomy / surgery"] = 1
    if m_cat == "M1a":
        w["Metastasectomy / surgery"] = 18 if ecog <= 1 else 3
        w["Local ablation"] = 8
    if m_cat == "M1c":
        w["Metastasectomy / surgery"] = 1
        w["Best supportive care"] = w.get("Best supportive care", 1) + 4

    # Between-hospital variation for resectable-looking M1a disease.
    if m_cat == "M1a" and ecog <= 1:
        if hospital in ("Hospital-NL-1", "Hospital-BE-1"):
            w["Metastasectomy / surgery"] = int(w["Metastasectomy / surgery"] * 2.0)
        elif hospital in ("Hospital-DE-1", "Hospital-IT-1"):
            w["Metastasectomy / surgery"] = max(2, int(w["Metastasectomy / surgery"] * 0.4))
            w["Systemic therapy - doublet"] += 10
    if hospital == "Hospital-SE-1":
        w["Enrolled in trial"] += 12

    return [(k, v) for k, v in w.items()]


def _outcome_weights(mol, ecog, decision):
    ras, braf, msi = mol
    w = {"Complete response": 2, "Partial response": 22, "Stable disease": 30,
         "Progressive disease": 26, "Not evaluable": 6}
    if msi == "MSI-H" and decision == "Checkpoint inhibitor":
        w["Complete response"] = 12
        w["Partial response"] = 34
        w["Progressive disease"] = 12
    if braf == "mut" and decision != "Targeted combination":
        w["Progressive disease"] += 14
        w["Partial response"] -= 8
    if decision == "Metastasectomy / surgery":
        w["Complete response"] += 10
        w["Progressive disease"] -= 8
    if decision == "Best supportive care":
        w = {"Complete response": 0, "Partial response": 1, "Stable disease": 8,
             "Progressive disease": 30, "Not evaluable": 14}
    if ecog >= 2:
        w["Progressive disease"] += 10
    return [(k, max(1, v)) for k, v in w.items()]


def make_cohort():
    import random
    rnd = random.Random(42)
    # Balanced hospital assignment so between-hospital comparisons have
    # comparable denominators.
    assign = [COHORT_HOSPITALS[i % len(COHORT_HOSPITALS)] for i in range(COHORT_SIZE)]
    rnd.shuffle(assign)
    rows = []
    for i in range(COHORT_SIZE):
        hospital, country = assign[i]
        mol = _pick(rnd, MOL_MIX)
        side = _pick(rnd, [("right", 38), ("left", 62)])
        site = rnd.choice(SITES_RIGHT if side == "right" else SITES_LEFT)
        m_cat = _pick(rnd, [("M1a", 44), ("M1b", 38), ("M1c", 18)])
        ecog = _pick(rnd, [(0, 30), (1, 46), (2, 20), (3, 4)])
        age_band = _pick(rnd, [("40-49", 6), ("50-59", 20), ("60-69", 32), ("70-74", 18), ("75-84", 20), ("85+", 4)])
        prior = _pick(rnd, [(0, 42), (1, 33), (2, 18), (3, 7)])
        decision = _pick(rnd, _decision_weights(mol, ecog, m_cat, hospital))
        outcome = _pick(rnd, _outcome_weights(mol, ecog, decision))
        base = {"Complete response": 26, "Partial response": 14, "Stable disease": 9,
                "Progressive disease": 4, "Not evaluable": 5}[outcome]
        ttnt = max(1, int(rnd.gauss(base, base * 0.35)))
        rows.append({
            "id": "SYN-COH-%03d" % (i + 1),
            "hospital": hospital,
            "country": country,
            "site": site,
            "side": side,
            "ras": mol[0], "braf": mol[1], "msi": mol[2],
            "mCategory": m_cat,
            "ecog": ecog,
            "ageBand": age_band,
            "priorLines": prior,
            "decision": decision,
            "outcome": outcome,
            "monthsToNextTreatment": ttnt,
            "year": rnd.choice([2023, 2024, 2025, 2026]),
        })
    return rows


# --------------------------------------------------------------------------

def cohort_attrs(p):
    """Attributes of the index patient, in the cohort's vocabulary.
    Anything the packet cannot answer is reported as None so the UI can say so."""
    mp = p.get("molecularProfile", {})

    def st(key):
        m = mp.get(key) or {}
        return m.get("status")

    kras, nras, braf, msi = st("kras"), st("nras"), st("braf"), st("msi")
    if kras in OK_MARKER and nras in OK_MARKER:
        ras = "mut" if (kras == "detected" or nras == "detected") else "wt"
    else:
        ras = None
    braf_v = ("mut" if braf == "detected" else "wt") if braf in OK_MARKER else None
    msi_v = ("MSI-H" if msi == "detected" else "MSS") if msi in OK_MARKER else None

    site = (p["diagnosis"]["primary"].get("site") or "").lower()
    side = "right" if any(k in site for k in ("caec", "cec", "ascend", "transverse", "hepatic flex")) else \
           "left" if any(k in site for k in ("descend", "sigmoid", "rectosigmoid", "rectum", "splenic flex")) else None

    return {
        "ras": ras, "braf": braf_v, "msi": msi_v,
        "side": side,
        "mCategory": p.get("stage", {}).get("tnm", {}).get("m"),
        "ecog": p["ecog"]["score"] if p.get("ecog") else None,
        "ageBand": p.get("header", {}).get("ageBand"),
        "priorLines": len(p.get("treatmentTimeline", [])),
    }


def build_case(p, variant=None):
    pid = p["patientId"]
    lab = LABELS[pid]
    return {
        "key": lab["short"] + ("+ct" if variant else ""),
        "short": lab["short"],
        "flag": lab["flag"],
        "country": lab["country"],
        "packet": p,
        "readiness": readiness(p),
        "trials": match_trials(p),
        "attrs": cohort_attrs(p),
    }


def validate(packets, resolved):
    """Validate every packet against the canonical schema, if jsonschema is available."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  (jsonschema not installed — skipping schema validation)")
        return
    v = Draft202012Validator(json.loads(SCHEMA.read_text()))
    targets = list(packets.items()) + [("synthetic-mcrc-IT-003 (late-result variant)", resolved)]
    bad = 0
    for name, p in targets:
        errs = sorted(v.iter_errors(p), key=lambda e: list(e.path))
        if errs:
            bad += 1
            print("  SCHEMA FAIL %s" % name)
            for e in errs[:5]:
                print("      %s: %s" % ("/".join(str(x) for x in e.path) or "<root>", e.message))
    if bad:
        sys.exit("%d packet(s) failed schema validation" % bad)
    print("  schema: %d/%d packets valid" % (len(targets), len(targets)))


def main():
    packets = {}
    for f in sorted(DATA.glob("*.json")):
        p = json.loads(f.read_text())
        packets[p["patientId"]] = p

    missing = set(LABELS) - set(packets)
    if missing:
        sys.exit("Missing expected packets: %s" % ", ".join(sorted(missing)))

    cases = [build_case(packets[pid]) for pid in LABELS]
    it = packets["synthetic-mcrc-IT-003"]
    resolved_packet = resolve_late_ct(it)
    resolved = build_case(resolved_packet, variant=True)

    schema = json.loads(SCHEMA.read_text())

    bundle = {
        "cases": cases,
        "resolvedIT": resolved,
        "cohort": make_cohort(),
        "meta": {
            "builtOn": date.today().isoformat(),
            "referenceDate": cases[0]["packet"]["fixtureMetadata"]["referenceDate"],
            "seed": cases[0]["packet"]["fixtureMetadata"]["generationSeed"],
            "profileLabel": cases[0]["packet"]["profileLabel"],
            "schemaTitle": schema.get("title"),
            "schemaRequired": schema.get("required", []),
            "cohortSize": COHORT_SIZE,
            "cohortHospitals": [h for h, _ in COHORT_HOSPITALS],
        },
    }

    payload = json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
    # keep the payload safe inside a <script> block
    payload = payload.replace("</", "<\\/")

    html = TEMPLATE.read_text()
    if "/*__MDO_DATA__*/" not in html:
        sys.exit("template.html is missing the /*__MDO_DATA__*/ marker")
    html = html.replace("/*__MDO_DATA__*/", "const MDO = " + payload + ";")

    OUT.write_text(html, encoding="utf-8")

    print("Built %s (%.0f KB)" % (OUT.name, OUT.stat().st_size / 1024))
    validate(packets, resolved_packet)
    for c in cases:
        r = c["readiness"]
        elig = sum(1 for t in c["trials"] if t["verdict"] == "eligible")
        print("  %-7s %-18s readiness %3d%% (%d/%d)  missingData=%d  trials eligible=%d"
              % (c["short"], c["packet"]["readinessState"]["status"], r["score"],
                 r["passed"], r["total"], len(c["packet"]["missingData"]), elig))
    r = resolved["readiness"]
    print("  %-7s %-18s readiness %3d%% (%d/%d)  missingData=%d  trials eligible=%d"
          % ("IT-003*", resolved["packet"]["readinessState"]["status"], r["score"],
             r["passed"], r["total"], len(resolved["packet"]["missingData"]),
             sum(1 for t in resolved["trials"] if t["verdict"] == "eligible")))


if __name__ == "__main__":
    main()
