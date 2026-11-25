
use crate::lexer::tokenize;
use crate::token::TokenizationResult;

/// Analiza código fuente Python y devuelve sus tokens.
///
/// Este comando es el punto de entrada desde Tauri IPC.
/// No ejecuta, compila ni evalúa el código recibido.
///
/// El trabajo se realiza en un hilo bloqueante para evitar
/// interrumpir el procesamiento asíncrono de la aplicación.
#[tauri::command]
pub async fn analyze_python(
    source: String,
) -> Result<TokenizationResult, String> {
    tauri::async_runtime::spawn_blocking(move || {
        tokenize(&source)
    })
        .await
        .map_err(|_| {
            "No se pudo completar el análisis del código.".to_owned()
        })?
        .map_err(|error| error.message)
}
