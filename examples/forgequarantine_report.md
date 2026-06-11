# ForgeQuarantine Report: FQ-AM-2026-06

- Records: `3`
- Urgent: `1`
- Ledger head: `adc6c85e62f710f648ec691e5ce6e8ea625fe7e00b894e342719b0d5576c5221`
- Cross-model certified: `false`
- Source round: `SA-EVX-20260611-001`

## Exposure Ledger

### CMP-AX9 / CRY-AX9-BOOT

- Part: `AM-TVC-AX9`
- Platform: `orbital transfer vehicle`
- Algorithm: `ECDSA` (`quantum_broken`)
- Exposure class: `service_life_crypto_quarantine`
- Quarantine priority: `urgent`
- Migration deadline year: `2028`
- Score: `0.805`
- Entry hash: `e0b2b2e57b6645cfe9a4f5352503b3dfa9346adcbd166afed25e6acd20bf3f29`
- Rationale:
  - ECDSA is classified as quantum_broken
  - flight_critical component on orbital transfer vehicle
  - firmware update path is no_update
  - service life runs through 2042

### CMP-MR2 / CRY-MR2-LINK

- Part: `AM-MOUNT-MR2`
- Platform: `defense radar pod`
- Algorithm: `RSA` (`quantum_broken`)
- Exposure class: `service_life_crypto_quarantine`
- Quarantine priority: `high`
- Migration deadline year: `2030`
- Score: `0.683`
- Entry hash: `540ec53992ae1e6c6dbd3c9d6381c6b08fc062fb0f95e2ba474bd5c44eede22f`
- Rationale:
  - RSA is classified as quantum_broken
  - mission_critical component on defense radar pod
  - firmware update path is depot_update
  - service life runs through 2036

### CMP-LAB / CRY-LAB-DATA

- Part: `AM-LAB-BRACKET`
- Platform: `ground test rig`
- Algorithm: `AES-256` (`symmetric_resilient`)
- Exposure class: `managed_exposure`
- Quarantine priority: `archive`
- Migration deadline year: `2029`
- Score: `0.246`
- Entry hash: `adc6c85e62f710f648ec691e5ce6e8ea625fe7e00b894e342719b0d5576c5221`
- Evidence gaps:
  - missing component qualification evidence
  - missing crypto dependency evidence
  - missing service-life evidence
- Rationale:
  - AES-256 is classified as symmetric_resilient
  - standard component on ground test rig
  - firmware update path is field_update
  - service life runs through 2029
  - 3 evidence gap(s) increase quarantine pressure
