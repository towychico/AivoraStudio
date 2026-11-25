
use ruff_python_ast::token::TokenKind;
use ruff_python_parser::{
    parse_unchecked,
    Mode,
    ParseOptions,
};
use ruff_text_size::Ranged;

use crate::token::{
    Diagnostic,
    Token,
    TokenCategory,
    TokenizationResult,
};

/// Tamaño máximo aceptado para una solicitud de análisis.
///
const MAX_SOURCE_BYTES: usize = 1024 * 1024;

/// Error de entrada que impide iniciar el análisis.
#[derive(Debug, Clone, serde::Serialize)]
pub struct LexerError {
    pub message: String,
}

/// Clasifica los tipos de tokens proporcionados por Ruff.
///
/// No implementa reglas léxicas: únicamente adapta las categorías
/// internas del parser a las categorías utilizadas por la interfaz.
fn classify_token(kind: TokenKind) -> TokenCategory {
    use TokenCategory as Category;

    if kind.is_soft_keyword() {
        return Category::SoftKeyword;
    }

    if kind.is_keyword() {
        return Category::Keyword;
    }

    match kind {
        TokenKind::Identifier => Category::Identifier,

        TokenKind::Int
        | TokenKind::Float
        | TokenKind::Complex => Category::Number,

        TokenKind::String => Category::String,

        TokenKind::FStringStart
        | TokenKind::FStringMiddle
        | TokenKind::FStringEnd => Category::FString,

        TokenKind::TStringStart
        | TokenKind::TStringMiddle
        | TokenKind::TStringEnd => Category::TString,

        TokenKind::Comment => Category::Comment,

        TokenKind::Newline
        | TokenKind::NonLogicalNewline => Category::Newline,

        TokenKind::Indent => Category::Indent,
        TokenKind::Dedent => Category::Dedent,
        TokenKind::EndOfFile => Category::Eof,

        TokenKind::Lpar
        | TokenKind::Rpar
        | TokenKind::Lsqb
        | TokenKind::Rsqb
        | TokenKind::Lbrace
        | TokenKind::Rbrace
        | TokenKind::Colon
        | TokenKind::Comma
        | TokenKind::Semi
        | TokenKind::Dot => Category::Delimiter,

        TokenKind::Unknown => Category::Unknown,

        _ if kind.is_operator() => Category::Operator,

        _ => Category::Unknown,
    }
}

/// Analiza código fuente Python mediante el frontend de Ruff.
///
/// Ruff se encarga del reconocimiento de tokens, la indentación,
/// las cadenas interpoladas y las reglas propias de Python.
///
/// Se utiliza `parse_unchecked` para conservar el resultado
/// del análisis incluso cuando existen errores sintácticos.
///
/// Importante: los tokens proceden del parser con recuperación
/// de errores. En código inválido no se garantiza recuperar
/// absolutamente todos los tokens del archivo.
pub fn tokenize(
    source: &str,
) -> Result<TokenizationResult, LexerError> {
    if source.len() > MAX_SOURCE_BYTES {
        return Err(LexerError {
            message: format!(
                "El código supera el límite de {} bytes",
                MAX_SOURCE_BYTES
            ),
        });
    }

    let parsed = parse_unchecked(
        source,
        ParseOptions::from(Mode::Module),
    );

    let tokens = parsed
        .tokens()
        .iter()
        .map(|raw| {
            let range = raw.range();

            let start = range.start().to_usize();
            let end = range.end().to_usize();

            let kind = raw.kind();

            let lexeme = source
                .get(start..end)
                .unwrap_or_default()
                .to_owned();

            Token::new(
                format!("{kind:?}"),
                classify_token(kind),
                lexeme,
                start,
                end,
            )
        })
        .collect();

    let diagnostics = parsed
        .errors()
        .iter()
        .map(|error| Diagnostic {
            message: error.error.to_string(),
            start: error.location.start().to_usize(),
            end: error.location.end().to_usize(),
        })
        .collect();

    Ok(TokenizationResult {
        tokens,
        diagnostics,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reconoce_variables_y_operadores() {
        let result = tokenize("x = 10 + 20\n").unwrap();

        assert!(result.diagnostics.is_empty());

        assert!(result.tokens.iter().any(|token| {
            token.category == TokenCategory::Identifier
                && token.lexeme == "x"
        }));

        assert!(result.tokens.iter().any(|token| {
            token.category == TokenCategory::Number
                && token.lexeme == "10"
        }));

        assert!(result.tokens.iter().any(|token| {
            token.category == TokenCategory::Operator
                && token.lexeme == "+"
        }));
    }

    #[test]
    fn reconoce_bloques_indentation() {
        let source = "if True:\n    print(10)\n";

        let result = tokenize(source).unwrap();

        assert!(result.diagnostics.is_empty());

        assert!(result.tokens.iter().any(|token| {
            token.category == TokenCategory::Indent
        }));

        assert!(result.tokens.iter().any(|token| {
            token.category == TokenCategory::Dedent
        }));
    }

    #[test]
    fn reconoce_identificadores_unicode() {
        let source = "café = 10\n";

        let result = tokenize(source).unwrap();

        assert!(result.diagnostics.is_empty());

        assert!(result.tokens.iter().any(|token| {
            token.category == TokenCategory::Identifier
                && token.lexeme == "café"
                && token.start == 0
                && token.end == 5
        }));
    }

    #[test]
    fn reconoce_f_strings() {
        let source = "nombre = 'Ana'\nprint(f'Hola {nombre}')\n";

        let result = tokenize(source).unwrap();

        assert!(result.diagnostics.is_empty());

        assert!(result.tokens.iter().any(|token| {
            token.category == TokenCategory::FString
        }));
    }

    #[test]
    fn reporta_errores_de_sintaxis() {
        let source = "if True\n    pass\n";

        let result = tokenize(source).unwrap();

        assert!(!result.diagnostics.is_empty());
    }

    #[test]
    fn rechaza_archivos_excesivamente_grandes() {
        let source = "x".repeat(MAX_SOURCE_BYTES + 1);

        assert!(tokenize(&source).is_err());
    }
}
