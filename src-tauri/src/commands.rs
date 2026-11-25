#[derive(serde::Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ResultDto {
    similarity: f64,
    confidence: f64,
    predicted_similar: bool,
    threshold: f64,
    elapsed_ms: f64,
    model: &'static str,
}
#[tauri::command]
pub async fn compare_python(
    original: String,
    comparison: String,
) -> Result<ResultDto, String> {
    if original.len() > sovereign_engine::MAX_BYTES
        || comparison.len() > sovereign_engine::MAX_BYTES
    {
        return Err("Máximo 64 KiB por entrada".into());
    }
    tauri::async_runtime::spawn_blocking(move || {
        let r = sovereign_engine::compare(&original, &comparison)?;
        Ok(ResultDto {
            similarity: r.similarity,
            confidence: r.confidence,
            predicted_similar: r.predicted_similar,
            threshold: sovereign_engine::THRESHOLD,
            elapsed_ms: r.total_us as f64 / 1000.,
            model: sovereign_engine::NAME,
        })
    })
        .await
        .map_err(|e| e.to_string())?
}

/// Señal de preparación, exclusivamente para el benchmark local opt-in.
#[tauri::command]
pub fn benchmark_ready(variant: String) -> Result<(), String> {
    if let Some(path) = std::env::var_os("AIVORA_BENCH_READY") {
        if variant != "monaco" && variant != "textarea" {
            return Err("Invalid variant".into());
        }
        std::fs::write(path, variant).map_err(|e| e.to_string())?;
    }
    Ok(())
}