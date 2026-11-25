
use serde::Serialize;

/// Categorías utilizadas para presentar los tokens en la interfaz.
///
/// La clasificación es independiente de los tipos internos de Ruff.
/// Esto permite mantener estable el contrato de IPC.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum TokenCategory {
    Keyword,
    SoftKeyword,
    Identifier,
    Number,
    String,
    FString,
    TString,
    Comment,
    Operator,
    Delimiter,
    Newline,
    Indent,
    Dedent,
    Eof,
    Unknown,
}

/// Representa un token producido por el analizador de Python.
///
/// `kind` conserva el nombre específico utilizado por Ruff.
/// `category` proporciona una clasificación general para la interfaz.
///
/// Los rangos utilizan offsets de bytes UTF-8 y son semiabiertos:
/// [start, end).
#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Token {
    pub kind: String,
    pub category: TokenCategory,
    pub lexeme: String,
    pub start: usize,
    pub end: usize,
}

impl Token {
    /// Crea una representación serializable del token.
    #[must_use]
    pub fn new(
        kind: impl Into<String>,
        category: TokenCategory,
        lexeme: impl Into<String>,
        start: usize,
        end: usize,
    ) -> Self {
        Self {
            kind: kind.into(),
            category,
            lexeme: lexeme.into(),
            start,
            end,
        }
    }
}

/// Representa un error detectado durante el análisis.
///
/// Se conservan los rangos para localizar el problema
/// en Monaco sin depender del texto del mensaje.
#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Diagnostic {
    pub message: String,
    pub start: usize,
    pub end: usize,
}

/// Resultado completo del análisis léxico.
///
/// Los errores de sintaxis no impiden entregar los tokens
/// que el parser haya recuperado.
#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct TokenizationResult {
    pub tokens: Vec<Token>,
    pub diagnostics: Vec<Diagnostic>,
}
