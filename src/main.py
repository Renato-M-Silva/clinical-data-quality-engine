def main():
    # 1. Ingestão
    data = ingest_all_sources()

    # 2. Validação
    validation_results = run_validation(data)

    # 3. Anomalias
    anomalies = detect_anomalies(data)

    # 4. Reconciliação
    reconciliation = run_reconciliation(data)

    # 5. Scoring
    dqi_outputs = compute_dqi(data, validation_results, anomalies, reconciliation)

    # 6. Export
    export_for_dashboard(dqi_outputs, validation_results, anomalies, reconciliation)
