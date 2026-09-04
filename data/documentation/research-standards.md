# Research: Technical Standards — Exact Versions & Sources

*Executed: 2026-08-27 | Access date for all URLs: 2026-08-27 | Primary sources only*  
*Supersedes version references in ADR-0001 (`docs/adr/0001-mcode-omop.md`) with pinned,
 verified versions.*

---

## Quick-reference table

| Standard | Version / Edition | Status | Primary URL | Verified 2026-08-27 |
|---|---|---|---|---|
| HL7 FHIR R4 | **4.0.1** (Oct 2019) | Normative + STU mix | https://hl7.org/fhir/R4/ | ✔ |
| mCODE STU4 | **4.0.0** (Feb 2025) | STU – current published | https://hl7.org/fhir/us/mcode/STU4/ | ✔ |
| US Core (mCODE STU4 dep.) | **6.1.0** (Jun 2023) | STU – pinned by mCODE | https://hl7.org/fhir/us/core/STU6.1/ | ✔ |
| HL7 Genomics Reporting IG | **2.0.0** STU2 (May 2022) | STU – current pub. at canonical URL ⚠ | https://hl7.org/fhir/uv/genomics-reporting/ | ✔ |
| International Patient Summary | **2.0.1** STU2 | STU – current | https://hl7.org/fhir/uv/ips/ | ✔ |
| Nictiz ZIB 2020 FHIR R4 | `nictiz.fhir.nl.r4.zib2020` — stable ver. ⚠ | FHIR R4 package | https://simplifier.net/packages/nictiz.fhir.nl.r4.zib2020 | ⚠ ver. TBC |
| MII KDS Onkologie | **2024.3.1** (latest stable) | FHIR R4 package | https://simplifier.net/packages/de.medizininformatikinitiative.kerndatensatz.onkologie | ✔ |
| HL7 Italia IT-Core | **0.2.0** Draft (Jul 2026) | Local dev build — not balloted | https://www.hl7.it/fhir/core/ | ✔ |
| Italian oncology FHIR IG | **DOES NOT EXIST** | — | https://www.hl7.it/fhir/ | ✔ explicit |
| SNOMED CT International | **20260701** (Jul 2026) ⚠ | Bi-annual release | https://www.snomed.org/get-snomed | ⚠ release ID TBC |
| LOINC | **2.83** (Aug 2026) | Current | https://loinc.org/news/loinc-version-2-83-release-highlights | ✔ |
| UCUM | **2.2** (Jun 2024) | Current | https://ucum.org/ucum | ✔ |
| ICD-10-WHO | **5th ed. 2016**; 2019 browser | Current for EU | https://icd.who.int/browse10/2019/en | ✔ |
| ICD-O-3 | **ICD-O-3.2** (2019) | Current revision | https://www.who.int/standards/classifications/other-classifications/international-classification-of-diseases-for-oncology | ✔ |
| HGNC | Continuous; monthly releases | Live database | https://www.genenames.org/ | ✔ |
| HGVS Nomenclature | **21.1** (current stable) | Current | https://hgvs-nomenclature.org/stable/ | ✔ |
| UICC TNM | **8th edition** (2017) | Current (9th in prep.) | https://www.uicc.org/resources/tnm | ✔ |

---

## 1. FHIR Foundations

### 1.1 HL7 FHIR R4 — v4.0.1

- **Version:** 4.0.1
- **Published:** 2019-10-30
- **URL (permanent):** https://hl7.org/fhir/R4/
- **System base URI:** `http://hl7.org/fhir/R4`
- **Note:** FHIR R5 (5.0.0) is available at http://hl7.org/fhir/index.html. mCODE STU4, IPS
  STU2, GRIG STU2, and all national IGs in this stack target R4. HL7 guarantees the R4 URL is
  permanently stable.
- **Implementation implication:** AHDS FHIR Service supports R4 (4.0.1) natively via the
  `rg-onco-<env>-data` FHIR endpoint. All FHIR profiles, REST operations, and $convert-data
  templates in this POC target R4.

---

### 1.2 mCODE STU4 — v4.0.0

- **Version:** 4.0.0
- **Published:** 2025-02-16
- **URL (permanent):** https://hl7.org/fhir/us/mcode/STU4/
- **Canonical IG URL:** `http://hl7.org/fhir/us/mcode/ImplementationGuide/hl7.fhir.us.mcode`
- **NPM package:** `hl7.fhir.us.mcode#4.0.0`
- **OID:** `2.16.840.1.113883.4.642.40.15`
- **Trademark:** mCODE® is a trademark of ASCO; developed by MITRE.
- **GitHub:** https://github.com/HL7/fhir-mCODE-ig
- **Structure:** ~40 FHIR R4 profiles in 6 groups: Patient, Disease Characterization, Treatment,
  Genomics, Outcomes, Radiology (via CodeX RT IG extension).
- **Declared dependencies (from STU4 source):**
  - US Core STU6.1 v6.1.0 — `http://hl7.org/fhir/us/core/STU6.1` (see §1.3)
  - Genomics Reporting IG — `http://hl7.org/fhir/uv/genomics-reporting/` → resolves to v2.0.0
    STU2 (see §1.4)

#### European conformance implications

mCODE STU4 is US-Realm (`hl7.fhir.us`). Required European adaptations (tracked in ADR-0001):

| US-centric element | Required adaptation for EU deployment |
|---|---|
| `US Core Patient` base profile | Replace with IPS `Patient-uv-ips` or national profile (ZIB NL, MII DE, IT-Core IT) |
| `US Core Practitioner / Organization` | Replace with IPS or national equivalents |
| `RxNorm` medication coding | Add `ATC` (WHO/WHOCC) binding; map ATC↔RxNorm via OMOP Athena |
| `ICD-10-CM` diagnosis coding path | Use ICD-10-WHO (5th ed.) — structurally compatible |
| US-only value set OIDs | Validate per profile; substitute SNOMED CT / LOINC where available |

---

### 1.3 US Core STU6.1 — v6.1.0 *(mCODE STU4 dependency)*

- **Version:** 6.1.0
- **Published:** 2023-06-19
- **URL:** https://hl7.org/fhir/us/core/STU6.1/
- **Current US Core (for reference only):** v9.0.0 (STU9) at https://hl7.org/fhir/us/core/
- **Implementation implication:** mCODE STU4 profiles derive from US Core 6.1.0. European
  deployments must provide conformant substitutes for every US Core profile mCODE extends.
  IPS STU2 provides internationally-scoped equivalents. A profile-by-profile substitution map
  is required in Sprint 2.

---

### 1.4 HL7 Genomics Reporting IG (GRIG) — v2.0.0 STU2

- **Version:** 2.0.0 (STU2)
- **Published:** 2022-05-09
- **URL (current published canonical):** https://hl7.org/fhir/uv/genomics-reporting/
- **Permanent STU2 URL:** https://hl7.org/fhir/uv/genomics-reporting/STU2/
- **Scope:** International (UV); germline + somatic variants; SNV, indel, CNV, structural
  variants; pharmacogenomics; somatic tumour reporting; HLA typing.
- **Key mCODE-used profiles:** `GenomicsReport`, `GenomicVariant`, `GenomicRegionStudied`,
  `TherapeuticImplication`.
- **⚠ Version uncertainty:** A v3.0.0 (STU3) is accessible at
  https://hl7.org/fhir/uv/genomics-reporting/STU3/ and STU2 profile pages reference v3.0.0 as
  superseding STU2. However, the canonical URL still serves v2.0.0 as "current published
  version" as of 2026-08-27. See §5 gap #1.
- **Implementation implication:** Use v2.0.0 for POC (matches mCODE STU4 dependency). KRAS/
  NRAS/BRAF/MSI/HER2 variants use `GenomicVariant`; IHC markers use `TumorMarkerTest`. HGVS
  v21.1 is the preferred variant notation (see §3.7). Plan upgrade to v3.0.0 once status is
  confirmed.

---

### 1.5 International Patient Summary (IPS) — v2.0.1 STU2

- **Version:** 2.0.1 (STU2)
- **URL (current published):** https://hl7.org/fhir/uv/ips/
- **Based on:** FHIR R4
- **Scope:** International (UV); specialty-agnostic patient summary; EU cross-border exchange
  baseline (MyHealth@EU / EHDS).
- **Implementation implication:** IPS provides the internationally-scoped Patient, Practitioner,
  Condition, etc. profiles that replace US Core dependencies in the European mCODE adaptation.
  Use `Patient-uv-ips` as the European `CancerPatient` base profile.

---

## 2. National European FHIR Profiles

### 2.1 Netherlands — Nictiz ZIB 2020 FHIR R4

- **Package ID:** `nictiz.fhir.nl.r4.zib2020`
- **Registry URL:** https://simplifier.net/packages/nictiz.fhir.nl.r4.zib2020
- **Maintainer:** Nictiz (Dutch national IT Institute for Healthcare), https://www.nictiz.nl/
- **Canonical namespace:** `http://nictiz.nl/fhir/`
- **Exact stable version:** ⚠ Not confirmed (Simplifier served only the canonicals declaration
  page; beta packages visible). See §5 gap #2.
- **Coverage:** Generic clinical building blocks (Zorginformatiebouwstenen / ZIBs) — patient,
  medication, procedures, diagnoses. **No dedicated Dutch oncology FHIR IG exists.**
- **Implementation implication:** ChipSoft HiX outputs ZIB-compliant FHIR R4. A ZIB → mCODE
  concept map is required at the FHIR adapter layer (`ZIB.TumourType` →
  `mcode-PrimaryCancerCondition`). Document in `curation/usagi/`. Nictiz has no published
  ZIB-to-mCODE map as of 2026-08-27.

---

### 2.2 Germany — MII Kerndatensatz Onkologie

- **Package ID:** `de.medizininformatikinitiative.kerndatensatz.onkologie`
- **Registry URL:** https://simplifier.net/packages/de.medizininformatikinitiative.kerndatensatz.onkologie
- **Stable version to use:** **2024.3.1**
- **Beta version (do not use):** 2025.0.0 — explicitly described on Simplifier as
  "unterjährige Beta-Version" with breaking changes to radiotherapy profiling and SNOMED code
  updates.
- **Canonical:** `https://www.medizininformatik-initiative.de/fhir/ext/modul-onko/`
- **Maintainer:** Medizininformatik-Initiative (MII), https://www.medizininformatik-initiative.de/
- **GitHub org:** https://github.com/medizininformatik-initiative
- **Terminology stack:** FHIR R4 + SNOMED CT + ICD-10-GM + ICD-O-3.2 + LOINC + UCUM
- **Coverage:** Tumour diagnosis, TNM staging, therapy (surgery, systemic, radiotherapy),
  follow-up, pathology; aligned with German ADT/GEKID cancer registry requirements.
- **Implementation implication:** German university hospital DIZ sites output MII KDS Onkologie
  natively (36+ institutions). Conform to `2024.3.1` for validation. MII KDS → mCODE mapping
  is tractable (shared ICD-O-3 and TNM 8 basis). Document concept map in `curation/usagi/`.
  Monitor Simplifier for stable `2025.x.y` release.

---

### 2.3 Italy — HL7 Italia IT-Core

- **Version:** 0.2.0 (Draft)
- **Build date:** 2026-07-30
- **URL:** https://www.hl7.it/fhir/core/
- **Canonical IG URL:** `http://hl7.it/fhir/itcore/ImplementationGuide/hl7.fhir.it.core`
- **Package:** `hl7.fhir.it.core` (R4 and R4B builds available)
- **Maintainer:** HL7 Italia, https://www.hl7.it/
- **Status:** ⚠ This is a **local development build**, not a formally balloted HL7 publication.
  Profiles defined: PatientItCore, PractitionerItCore, AddressItCore, PractitionerRoleItCore,
  CoverageItCore, OrganizationItCore, MedicationItCore, ProcedureItCore.
- **Implementation implication:** Use v0.2.0 as the best-available Italian FHIR base profile for
  Italian site Patient/Practitioner profiles in the mCODE European adapter. Monitor for formal
  ballot publication. Contact HL7 Italia (mario.sicuranza@icar.cnr.it or
  leonardo.alcaro@gmail.com) to confirm ballot timeline.

---

### 2.4 Italy — Oncology-Specific FHIR IG

> **EXPLICIT FINDING: No official published Italian oncology-specific FHIR IG exists as of
> 2026-08-27.**

Verified by inspection of https://www.hl7.it/fhir/ (HL7 Italia's complete published and
CI-build IG list), accessed 2026-08-27.

**Published IGs at HL7 Italia:** Laboratory Report, Taccuino Personale dell'assistito,
Televisita, Teleconsulto, Teleassistenza, Telemonitoraggio, IT-Core.  
**CI-Build IGs:** Terminology, Dossier Farmaceutico, CDA-to-FHIR Maps.  
**Oncology IG: absent from both lists.**

No evidence found of a pending Italian national oncology FHIR IG in any primary source.

**Implementation implication:** For Italian site(s), use IT-Core v0.2.0 for patient and
organisation profiling; use mCODE STU4 for oncology data. Italian cancer registry (AIRTUM)
uses ICD-O-3.2, which is natively supported by mCODE's ICD-O-3 encoding path. If Italian
hospital partners hold a regional IG, obtain it directly from the site before Sprint 2 site
onboarding.

---

## 3. Terminology and Coding Systems

### 3.1 SNOMED CT International Edition

- **Release schedule:** Bi-annual — January (YYYYMMM01) and July (YYYY0701)
- **Expected latest release as of 2026-08-27:** `20260701` (July 2026)
  ⚠ release identifier not directly verified; SNOMED browser redirect failed during this
  session. See §5 gap #3.
- **Access URL:** https://www.snomed.org/get-snomed
- **Production browser:** https://snomedbrowser.org/
- **Licensing:** Free for healthcare organisations in SNOMED International member countries.
  POC countries: NL (Nictiz NRC), DE (BfArM NRC), IT (Agenas NRC) — all full members. No
  per-seat licensing costs.
- **FHIR system URI:** `http://snomed.info/sct`
- **Implementation implication:** Primary coding system for cancer conditions, body sites,
  histology, procedures, and TNM stage values in mCODE profiles. National extensions available
  for NL, DE, IT for local concepts. Pin Athena vocabulary SNOMED download to July 2026 release
  once confirmed.

---

### 3.2 LOINC — v2.83

- **Version:** 2.83 (released 2026-08-19)
- **Owner:** Regenstrief Institute, Inc.
- **Download URL:** https://loinc.org/downloads (free, registration required)
- **License:** https://loinc.org/kb/license — free to use; cannot be used to create a
  competing standard.
- **FHIR system URI:** `http://loinc.org`
- **Implementation implication:** Required for genomics observation codes in GRIG profiles, vital
  signs, and clinical observations in FHIR R4. AHDS FHIR Service and OMOP Athena both include
  LOINC vocabulary. Pin to v2.83 in Usagi mapping tables. Run
  `GET [fhirurl]/CodeSystem?url=http://loinc.org` on the provisioned AHDS endpoint to confirm
  service-side LOINC version.

---

### 3.3 UCUM — v2.2

- **Version:** 2.2
- **Date:** 2024-06-17
- **Owner:** Regenstrief Institute, Inc. and the UCUM Organization
- **URL:** https://ucum.org/ucum
- **GitHub:** https://github.com/ucum-org/ucum
- **Copyright:** © 1998–2024 Regenstrief Institute, Inc. and the UCUM Organization
- **FHIR system URI:** `http://unitsofmeasure.org`
- **Licensing:** Free to use.
- **Implementation implication:** Required for all FHIR `Quantity` data types (tumour size, CEA
  levels, lab values). FHIR R4 mandates UCUM for quantities. Use v2.2 unit atoms in all FHIR
  resource instances and OMOP MEASUREMENT.unit_concept_id mapping.

---

### 3.4 ICD-10-WHO — 5th Edition (2016)

- **Edition:** 5th (2016); WHO online browser reflects 2019 update
- **URL:** https://icd.who.int/browse10/2019/en
- **Owner / Maintainer:** World Health Organization
- **FHIR system URIs:** `http://hl7.org/fhir/sid/icd-10` (generic WHO);
  `http://fhir.de/CodeSystem/bfarm/icd-10-gm` (German ICD-10-GM adaptation)
- **Note:** Distinct from ICD-10-CM (US clinical modification). German sites use ICD-10-GM.
  mCODE's ICD-10-CM encoding path is structurally format-compatible with ICD-10-WHO.
- **Implementation implication:** Use ICD-10-WHO codes for primary diagnosis (`Condition.code`)
  in European mCODE deployments (per ADR-0001). Include ICD-10-GM system URI in the German site
  FHIR CapabilityStatement. ICD-11 is the WHO successor, but ICD-10 remains the operative
  standard for European hospital coding through the POC period.

---

### 3.5 ICD-O-3 — ICD-O-3.2 (2019)

- **Current revision:** ICD-O-3.2 (released 2019); prior revisions: ICD-O-3.1 (2013), ICD-O-3
  (2000)
- **Owner:** WHO / IARC (International Agency for Research on Cancer)
- **WHO page:** https://www.who.int/standards/classifications/other-classifications/international-classification-of-diseases-for-oncology
- **CSV download:** http://www.iacr.com.fr/index.php?Itemid=577 (IACR distribution)
- **FHIR system URI (morphology):** `urn:oid:2.16.840.1.113883.6.43.1`; topography uses ICD-10
  C-codes
- **Structure:** Topography (C-codes, e.g. C18.0 = cecum) + Morphology (M-HHHH/B format, e.g.
  M-8140/3 = adenocarcinoma NOS, malignant) + 1-digit histologic grade.
- **Licensing:** Free. Distributed by WHO / IACR.
- **Implementation implication:** Primary coding for European cancer registries (DCRA NL,
  AIRTUM IT, ADT/GEKID DE). mCODE STU4 explicitly supports ICD-O-3 via `PrimaryCancerCondition`
  (base SNOMED neoplasm concept `363346000` in `Condition.code` + full ICD-O-3 morphology in
  `HistologyMorphologyBehavior` extension). OMOP Athena includes ICD-O-3 vocabulary with SNOMED
  CT mappings. Verify Athena coverage includes ICD-O-3.2 update codes (post-2019).

---

### 3.6 HGNC

- **Release model:** Continuously updated; monthly archive snapshots (deleted after 365 days)
  and permanent quarterly archives.
- **~43,000 approved symbols** (~19,000 protein-coding genes + pseudogenes, ncRNAs, other
  loci). Each assigned a permanent stable `HGNC ID`.
- **Owner:** EMBL-EBI / University of Cambridge; funded by NHGRI (US NIH)
- **URL:** https://www.genenames.org/
- **Archive / bulk download:** https://www.genenames.org/download/archive/
- **License:** No restrictions on access or use. Data freely available.
- **FHIR system URI:** `http://www.genenames.org`
- **MDT-relevant gene HGNC IDs:** KRAS (HGNC:6407), NRAS (HGNC:7989), BRAF (HGNC:1097), ERBB2
  / HER2 (HGNC:3430), MLH1 (HGNC:7127), MSH2 (HGNC:7325)
- **Implementation implication:** Use HGNC gene symbols and HGNC IDs in
  `GenomicVariant.component:gene-studied` (GRIG) and in OMOP MEASUREMENT for gene-level
  results. HGNC IDs are stable even when gene symbols are updated. Include HGNC ID as
  `measurement_source_value` in OMOP for unambiguous gene identification across time.

---

### 3.7 HGVS Nomenclature — v21.1

- **Current version:** 21.1
- **URL:** https://hgvs-nomenclature.org/stable/
- **Versioning note:** Semantic versioning adopted January 2024 (v21.0.0+). Major version is NOT
  year-based. Prior versions were date-based (e.g., 20.05 = May 2020).
- **Administrator:** HGVS Variant Nomenclature Committee (HVNC) under HUGO
- **Key citation:** Hart RK et al., *HGVS Nomenclature 2024.* Genome Med **16**, 149 (2024).
  doi:10.1186/s13073-024-01421-5
- **FHIR usage:** No single FHIR system URI for HGVS; expressions are bound to specific
  reference sequences (e.g., `https://www.ncbi.nlm.nih.gov/refseq/` for RefSeq-based
  expressions).
- **Implementation implication:** HGVS is the preferred variant description in GRIG
  `GenomicVariant.component[dna-chg].valueCodeableConcept`. Example: BRAF V600E =
  `NM_004333.6:c.1799T>A`. Store full HGVS string as `measurement_source_value` in OMOP;
  map only clinically actionable variants to OMOP standard concept IDs (KRAS exon 2/3/4, NRAS
  exon 2/3/4, BRAF V600E, MSI status, HER2 amplification). State HGVS version in all genomics
  data contracts.

---

### 3.8 UICC TNM Classification — 8th Edition (2017)

- **Edition:** 8th (2017)
- **Publisher:** Union for International Cancer Control (UICC)
- **URL:** https://www.uicc.org/resources/tnm
- **FAQ document (2025):** https://www.uicc.org/sites/default/files/2025-02/faq-tnm-helpdesk-2025.pdf
- **ISBN:** 978-1-119-26357-9 (Wiley-Blackwell, 2017); editors Brierley, Gospodarowicz, Wittekind
- **Equivalence note:** AJCC 8th edition is internationally equivalent to UICC TNM 8 for CRC
  staging. mCODE STU4 encodes staging as AJCC 8, which is directly applicable for UICC TNM 8
  reporting in European contexts.
- **FHIR coding:** TNM values coded as SNOMED CT concepts in mCODE (e.g., clinical T3 =
  SNOMED `1228882005`); `staging.type.coding` identifies AJCC/UICC 8th edition system.
- **Note:** UICC TNM 9th edition is in preparation; no release date confirmed as of 2026-08-27.
  ⚠ See §5 gap #6.
- **Implementation implication:** Use UICC TNM 8 for all staging in the POC. Capture both
  clinical (cTNM) and pathological (pTNM) staging via `TNMClinicalStageGroup` /
  `TNMPathologicalStageGroup` mCODE profiles. Verify OMOP Athena concept ID coverage for all
  TNM 8 T/N/M subcategory values (staging domain concepts available but completeness not
  confirmed).

---

## 4. Cross-standard conformance summary

| Layer | Standard(s) | Package / pin |
|---|---|---|
| FHIR transport | FHIR R4 | `hl7.fhir.r4.core#4.0.1` |
| Oncology profiles | mCODE STU4 | `hl7.fhir.us.mcode#4.0.0` |
| Patient base (EU) | IPS STU2 | `hl7.fhir.uv.ips#2.0.1` |
| NL site patient / clinical | ZIB 2020 | `nictiz.fhir.nl.r4.zib2020#<TBC>` |
| DE site oncology | MII KDS Onkologie | `de.medizininformatikinitiative.kerndatensatz.onkologie#2024.3.1` |
| IT site base | IT-Core | `hl7.fhir.it.core#0.2.0` (draft) |
| Genomics | GRIG | `hl7.fhir.uv.genomics-reporting#2.0.0` |
| Conditions / body site / procedures | SNOMED CT | International Edition 20260701 (TBC) |
| Lab / observation codes | LOINC | v2.83 |
| Units of measure | UCUM | v2.2 |
| Cancer diagnosis (topology + morphology) | ICD-O-3.2 | CSV via IACR 2019 |
| Tumour staging | UICC TNM 8 | Encoded via SNOMED CT in mCODE |
| Gene nomenclature | HGNC | Monthly (current) |
| Variant notation | HGVS | v21.1 |

---

## 5. Gaps and uncertainties requiring human validation

| # | Item | Detail | Action required |
|---|---|---|---|
| 1 | **GRIG v3.0.0 published status** | Canonical URL serves v2.0.0 as "current published version." STU2 profile pages reference v3.0.0 at `/STU3/` as superseding. Status ambiguous as of 2026-08-27. | Check https://hl7.org/fhir/uv/genomics-reporting/history.html or HL7 Confluence. If STU3 is formally published, update dependency pin. |
| 2 | **Nictiz ZIB 2020 exact stable package version** | Simplifier served only canonicals page; beta packages visible but stable version not confirmed from primary source. | Navigate to https://simplifier.net/packages/nictiz.fhir.nl.r4.zib2020 (logged in) or contact Nictiz (https://www.nictiz.nl/). Pin exact version in FHIR validator config. |
| 3 | **SNOMED CT July 2026 release confirmation** | Bi-annual schedule implies `20260701` release; SNOMED browser redirect failed during this research session. | Verify at https://snomedbrowser.org/ or https://www.snomed.org/get-snomed. Confirm release identifier `20260701`. Update Athena vocabulary download. |
| 4 | **MII KDS Onkologie 2025.0.0 stable release** | `2025.0.0` is a mid-year beta with breaking changes. Use `2024.3.1` until a stable `2025.x.y` is published. | Monitor https://simplifier.net/packages/de.medizininformatikinitiative.kerndatensatz.onkologie. Do not upgrade without reviewing release notes for radiotherapy profile changes. |
| 5 | **HL7 Italia IT-Core ballot timeline** | v0.2.0 is a local dev build / draft. No formal HL7 ballot publication found. | Contact HL7 Italia (mario.sicuranza@icar.cnr.it; leonardo.alcaro@gmail.com) for ballot schedule. Use v0.2.0 as best-available until formally published. |
| 6 | **UICC TNM 9th edition** | 9th edition in preparation; no publication date announced as of 2026-08-27. | Monitor https://www.uicc.org/resources/tnm. No action for POC (use 8th edition); flag for pilot phase architecture review. |
| 7 | **Italian oncology FHIR IG** | Confirmed absent from HL7 Italia published and CI-build IG list (2026-08-27). | Accept as non-existent. Directly query Italian hospital POC partners and AIRTUM for any informal or regional FHIR artefacts. |
| 8 | **LOINC version in AHDS FHIR Service** | Service-side LOINC version not confirmed. LOINC current is v2.83. | Run `GET [fhirurl]/CodeSystem?url=http://loinc.org` on provisioned AHDS endpoint and compare `version` field to `2.83`. |

---

## 6. Citation index

| # | Claim | Source URL | Accessed |
|---|---|---|---|
| C01 | FHIR R4 = v4.0.1, Oct 2019 | https://hl7.org/fhir/R4/ | 2026-08-27 |
| C02 | mCODE STU4 v4.0.0, active 2025-02-16, canonical URL | https://hl7.org/fhir/us/mcode/STU4/ | 2026-08-27 |
| C03 | mCODE STU4 declares US Core STU6.1 dependency | https://hl7.org/fhir/us/mcode/STU4/index.html | 2026-08-27 |
| C04 | US Core v6.1.0, published 2023-06-19; v9.0.0 is current | https://hl7.org/fhir/us/core/STU6.1/ | 2026-08-27 |
| C05 | GRIG v2.0.0 STU2 "current published version", 2022-05-09 | https://hl7.org/fhir/uv/genomics-reporting/StructureDefinition-genomics-report.html | 2026-08-27 |
| C06 | GRIG STU2 profile pages reference v3.0.0 as superseding | https://hl7.org/fhir/uv/genomics-reporting/STU2/StructureDefinition-genomics-report.html | 2026-08-27 |
| C07 | IPS v2.0.1 STU2, current published | https://hl7.org/fhir/uv/ips/ | 2026-08-27 |
| C08 | Nictiz ZIB 2020 package canonical namespace | https://simplifier.net/packages/nictiz.fhir.nl.r4.zib2020 | 2026-08-27 |
| C09 | MII KDS Onkologie canonical; versions 2024.3.1 and 2025.0.0 beta | https://simplifier.net/packages/de.medizininformatikinitiative.kerndatensatz.onkologie | 2026-08-27 |
| C10 | MII KDS 2025.0.0 = "unterjährige Beta-Version" with breaking changes | https://simplifier.net/search?term=de.medizininformatikinitiative.kerndatensatz.onkologie | 2026-08-27 |
| C11 | HL7 Italia IT-Core v0.2.0 draft local dev build, 2026-07-30 | https://www.hl7.it/fhir/core/ | 2026-08-27 |
| C12 | HL7 Italia published IG list — no oncology IG | https://www.hl7.it/fhir/ | 2026-08-27 |
| C13 | SNOMED CT access and member licensing | https://www.snomed.org/get-snomed | 2026-08-27 |
| C14 | LOINC v2.83 release (Aug 2026) | https://loinc.org/news/loinc-version-2-83-release-highlights | 2026-08-27 |
| C15 | UCUM v2.2, 2024-06-17 | https://ucum.org/ucum | 2026-08-27 |
| C16 | ICD-10-WHO browser (5th ed., 2019 online update) | https://icd.who.int/browse10/2019/en | 2026-08-27 |
| C17 | ICD-O-3.2 (2019) current revision; structure and download | https://www.who.int/standards/classifications/other-classifications/international-classification-of-diseases-for-oncology | 2026-08-27 |
| C18 | HGNC ~43,000 symbols, NHGRI-funded, no use restrictions | https://www.genenames.org/about/ | 2026-08-27 |
| C19 | HGNC monthly archive and bulk download | https://www.genenames.org/download/archive/ | 2026-08-27 |
| C20 | HGVS v21.1 current; semantic versioning from Jan 2024 | https://hgvs-nomenclature.org/stable/versions/ | 2026-08-27 |
| C21 | HGVS 2024 paper | doi:10.1186/s13073-024-01421-5 | 2026-08-27 |
| C22 | UICC TNM — resource page and FAQ 2025 | https://www.uicc.org/resources/tnm | 2026-08-27 |
