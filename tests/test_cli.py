import json

from forgequarantine.cli import main


def test_cli_sample_and_run_json(tmp_path):
    components = tmp_path / "component_manifest.json"
    dependencies = tmp_path / "crypto_dependencies.json"
    service = tmp_path / "service_life.json"
    out = tmp_path / "report.json"

    assert main(["sample", "-c", str(components), "-d", str(dependencies), "-s", str(service)]) == 0
    assert main(["run", "-c", str(components), "-d", str(dependencies), "-s", str(service), "--full", "-o", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))

    assert data["boundary"]["cross_model_certified"] is False
    assert data["records"][0]["exposure_class"] == "service_life_crypto_quarantine"


def test_cli_markdown(tmp_path):
    components = tmp_path / "component_manifest.json"
    dependencies = tmp_path / "crypto_dependencies.json"
    service = tmp_path / "service_life.json"
    out = tmp_path / "report.md"

    main(["sample", "-c", str(components), "-d", str(dependencies), "-s", str(service)])
    assert main(["run", "-c", str(components), "-d", str(dependencies), "-s", str(service), "--markdown", "-o", str(out)]) == 0

    assert "ForgeQuarantine Report" in out.read_text(encoding="utf-8")

