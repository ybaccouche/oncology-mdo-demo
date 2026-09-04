# Oncology MDO synthetic datasets

SYNTHETIC TEST DATA ONLY - NOT REAL PATIENT DATA

This package contains three fictional metastatic colorectal cancer datasets:

- `synthetic-mcrc-NL-001`: complete Dutch reference case.
- `synthetic-mcrc-DE-002`: German missing-data case.
- `synthetic-mcrc-IT-003`: Italian late-CT-result case in its initial pending state.

## Contents

- `fhir/`: country-specific FHIR R4 source bundles.
- `mdo_packets/`: normalized MdoPacket JSON fixtures.
- `schema/`: canonical MdoPacket JSON Schema.
- `documentation/research-standards.md`: standards versions, direct owner URLs, and known uncertainties.

Generation seed: `42`

Fixture reference date: `2026-08-27`

Profile label: `mCODE-aligned European demo profile`

The datasets contain historical synthetic treatment data only. They provide no treatment recommendations and must not be used for clinical care.

The Italian checked-in fixture represents the initial `result-pending` state. The working mock API can simulate CT arrival and regenerate the normalized ready-for-review view.
