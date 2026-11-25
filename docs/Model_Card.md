# Model card · Sovereign Engine

## Model and intended use

Logistic regression, binary supervised classification of pairs of Python source-code blocks. Positive class: similar according to dataset labels. This is a review aid, not an authorship, plagiarism, semantic-equivalence or security-verification tool. Do not use the score as the sole basis for disciplinary action.

## Dataset and training

3,000 balanced pairs from `training/poolc_prepared.zip`: 2,100 training, 450 validation, 450 test. Source groups and hashes are checked for disjointness across splits. Python 3.13.5, scikit-learn 1.8.0, seed 42; logistic regression max_iter=1000. Threshold search 0.05–0.95 in increments of 0.01; ties favor proximity to 0.5. Selection: smallest estimated supervised model within 0.02 validation F1 of the best. Test partition was used in historical project evaluation; external validation is required.

## Feature contract

| Index | Feature | Interpretation |
| ---: | --- | --- |
| 0 | token_cosine | Normalized unigram frequency cosine |
| 1 | bigram_cosine | Normalized adjacent token frequency cosine |
| 2 | trigram_cosine | Normalized three-token frequency cosine |
| 3 | token_jaccard | Unique normalized token overlap |
| 4 | bigram_jaccard | Unique normalized bigram overlap |
| 5 | raw_bigram_cosine | Bigram frequencies retaining identifier names |
| 6 | line_cosine | Frequency cosine of normalized token-line sequences |
| 7 | indent_cosine | Frequency cosine of indentation widths |
| 8 | byte_difference | Absolute UTF-8 byte-length difference / max length |
| 9 | token_difference | Absolute token-count difference / max count |
| 10 | line_difference | Absolute nonempty token-line count difference / max count |

Cosine returns zero when either frequency vector is empty. Jaccard returns one when both sets are empty. Relative difference denominator is at least one. Keywords/operators are retained; identifiers, numeric and string literals are normalized. Raw identifier names are retained in an auxiliary representation; comments are skipped. This lexer is not a parser.

## Model parameters and decision

`p = sigmoid(b + dot(w, x))`, threshold 0.35. 11 f64 weights plus one intercept are 96 bytes; threshold adds 8 bytes. All numeric values are compiled into `engine/src/model.rs`. The output probability is not calibrated. The lexical score is a separate average of token Jaccard and available unigram/bigram/trigram cosines.

## Evaluation

| Metric | Value |
| --- | ---: |
| Validation F1 | 83.56% |
| Test accuracy | 79.56% |
| Test precision | 74.36% |
| Test recall | 90.22% |
| Test F1 | 81.53% |
| Test ROC-AUC | 90.11% |
| True negative / false positive | 155 / 70 |
| False negative / true positive | 22 / 203 |

Native Rust parity passed on 450 pairs in the macOS benchmark. The accuracy target of 80% was missed by 0.44 percentage points. The historical original forest F1 was 82.93%, a 1.40 pp difference. No calibration, external corpus generalization, adversarial robustness, or performance across all Python grammar has been established.

Dataset SHA-256: `66da6e71710a6eac7e9c92c1f3586500752c4e7c59660cf6e69fb88fe5582c25`. See `results/metrics.json` for exact values and alternative candidates.
