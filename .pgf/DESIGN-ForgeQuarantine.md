# DESIGN-ForgeQuarantine

```text
ForgeQuarantine // additive-manufacturing PQC exposure ledger (done) @v:0.1
    SourceBoundary // preserve SA standalone provenance (done)
    InputAdapters // parse component, crypto, and service-life data (done)
    ExposureCompiler // score physical crypto exposure (done)
        CryptoRisk // classify algorithm exposure (done)
        PhysicalQualification // factor criticality and qualification evidence (done)
        ServiceLifeOverlap // compute quantum-horizon overlap and deadline (done)
        EvidenceGaps // surface missing qualification, crypto, and life evidence (done)
    Reports // emit JSON and Markdown (done)
    Verification // tests, CLI smoke, SVG parse, ledger wrapper (needs-verify)
```

```python
def AI_compile_forge_quarantine(component_manifest, crypto_dependencies, service_life) -> ExposureReport:
    """
    Tie cryptographic dependency exposure to physical printed components.
    Return exposure class, quarantine priority, migration deadline,
    evidence gaps, and SA standalone boundary metadata.
    """
    parsed = parse(component_manifest, crypto_dependencies, service_life)
    exposure = AI_assess_crypto_physical_service_life(parsed)
    return rank(exposure, by=["exposure_score", "component_id", "dependency_id"])
```

## Acceptance Criteria

- CLI writes sample inputs.
- CLI writes full JSON and Markdown report.
- Report includes `cross_model_certified=false`.
- Highest risk sample path is a flight-critical ECDSA/no-update component overlapping the quantum horizon.
- Tests pass with stdlib runtime plus pytest.

