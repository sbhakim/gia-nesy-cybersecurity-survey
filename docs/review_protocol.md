# Review Protocol and Traceability Notes

This document records the selection protocol used for the accompanying survey. It is intended to make the corpus updateable and its classification inspectable; it is not a claim that the original searches can be replayed record-for-record from proprietary database exports.

## Scope

- **Publication window:** January 2019 through July 2026.
- **Topic:** cybersecurity studies with identifiable neural and symbolic components, plus a limited set of contextual baselines.
- **Final catalog:** 108 publications: 22 Type A, 59 Type B, and 27 Type C entries.

## Search sources and concept blocks

The review searched IEEE Xplore, ACM Digital Library, SpringerLink, ScienceDirect, arXiv, Scopus, Web of Science, and specialist venues including NeSy, NeuS, S&P, IEEE EuroS&P, CCS, USENIX Security, NDSS, NeurIPS, ICML, AAAI, IJCAI, ICLR, KDD, and ISWC. Google Scholar was used only for supplementary citation backfilling.

Searches combined a neural-symbolic block with a cybersecurity-domain block and, where useful, a focused technical block:

```text
("neuro-symbolic" OR neurosymbolic OR "neural-symbolic" OR
 "hybrid AI" OR "knowledge-guided learning")
AND
(cybersecurity OR "network security" OR "intrusion detection" OR
 malware OR "vulnerability analysis")
```

Focused searches additionally used terms such as `knowledge graph`, `explainable AI`, `symbolic reasoning`, `logic tensor networks`, `causal reasoning in cybersecurity`, and `MITRE ATT&CK`. Query syntax was adapted to each source.

## Selection and quality assessment

| Stage | Records | Procedure |
|---|---:|---|
| Records identified | 353 | Potential neural-symbolic cybersecurity applications retrieved from the specified sources |
| After deduplication | 251 | 102 records removed using DOI and title-year matching |
| Eligibility screening | 194 | Titles, abstracts, and full texts screened against the stated criteria |
| Final classification | 108 | Reporting completeness, technical detail, cybersecurity relevance, and taxonomy suitability assessed |

A focused supplementary citation-backfill search identified Pingle et al.'s 2019 RelExt study. Full-text reassessment under the same criteria classified it as Type B because UCO/STIX schema constraints shape neural relation extraction and the predicted relations populate a cybersecurity knowledge graph.

Included studies are peer-reviewed or established preprints that apply identifiable neural and symbolic components to cybersecurity and provide sufficient technical detail for classification. Excluded studies are general AI/ML papers, systems without cross-paradigm interaction, and position papers or abstracts lacking an empirical or architectural contribution. Pure neural or symbolic systems relevant for comparison are retained only as Type C contextual baselines.

Two independent reviewers double-coded 20% of records (`n=49`), obtaining Cohen's kappa of 0.89 for inclusion decisions and 0.85 for quality assessments. Disagreements were resolved through structured discussion and expert consultation.

## Classification rule

- **Type A — Deep NeSy:** joint optimization or deeply interleaved neural-symbolic training.
- **Type B — Structured neural-symbolic systems:** meaningful interaction between identifiable neural and symbolic components, without asserting that every entry meets strict end-to-end integration criteria.
- **Type C — Contextual baselines:** pure neural or statistical systems retained for comparative context; these are not NeSy exemplars.

Each final decision can be inspected in [`data/paper_catalog.csv`](../data/paper_catalog.csv) through its stable ID, tier, subtype, neural component, symbolic component, domain, and venue type. The catalog is the authoritative final-study set; intermediate proprietary-index results and individual exclusion logs are not redistributed.
