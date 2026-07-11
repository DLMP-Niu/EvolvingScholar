# Intern Study Path and Learning Reflection Record
_Reviewed and organized — July 2026_

## Purpose

This log captures the intern's research path for each gene/disease pair, tracking literature review, EMR data findings, and how learning transfers across projects.

Questions for each study:
1. **What am I studying?**
2. **Where do I find information?**
3. **What EMR data do I have?**
4. **Does EMR data confirm what literature says?**
5. **Does EMR data suggest anything new?**
6. **What did I build for the demo/figure?**
7. **What did this teach me for the next project?**

---

# Phase 1 — First Disease Study: TTR / Amyloidosis

## 1. What am I studying?

TTR amyloidosis can present as cardiomyopathy, neuropathy, or a combination of both. The phenotypic spectrum is diverse and complex, making it difficult to establish disease etiology and genotype-phenotype correlations. Using data from the All of Us Research Program, this project aims to retrieve, clean, and aggregate patient-level EMR data — including diagnoses, laboratory results, procedures, and healthcare encounters — to develop a comprehensive phenotype model.

> PI feedback - Using data approach for disease phentype natrual history. 

---

## 2. Where do I find information?

I started with MedlinePlus to build a baseline understanding of TTR and its associated disease. I then moved to PubMed and ScienceDirect for peer-reviewed literature. After feedback that this literature was less clinically focused, I shifted to Consensus to find more current clinical publications.

My search sequence was:
- Start broad: current knowledge base for TTR/amyloidosis
- Narrow to ongoing debates and unresolved clinical questions
- Focus specifically on genotype-phenotype questions relevant to the EMR analysis

> PI feedback - guideline, primary literature, recent medical conference report, case conference. 

---

## 3. What EMR data do I have?

The datasets were provided via Google Cloud and include:
- Appointment records
- Encounter records
- Diagnosis records (ICD codes)
- Lab results
- All deidentified patient demographic information

> PI feedback - review example cohort study to understand data element first vs explore data set. 

---

## 4. Does EMR data confirm what literature says?

Generally, the EMR data aligned with the published literature. The expected TTR amyloidosis phenotypes — cardiac and neuropathic — were both observable in the cohort.

> PI feedback -  Review and guideline information first - expected age of onset ranges, frequency of cardiac vs. neuropathic presentation, proportion of hereditary vs. wild-type cases.

---

## 5. Does EMR data suggest anything new?

Two patterns stood out that warrant further attention:

1. The combination of amyloidosis + cardiac conditions was more frequent in the cohort than amyloidosis + neuropathy.
2. Neuropathy diagnoses tended to occur significantly later than amyloidosis diagnosis (p < 0.05).

> PI feedbak - Caution on statistical claims with cohort size, and especially the interpreation of the observation (cardiac predominance due to patient subgroup, and triage or ascertaining bias).

---

## 6. What did I build for the demo/figure?

Notebook not shared.

---

## 7. What did this teach me for the next project?

Many of the data analysis approaches developed here are transferable to other gene/disease projects. Specifically, the keyword generation strategy for searching diagnoses and the EMR aggregation structure are reusable. The general workflow — literature first, then EMR validation, then exploratory analysis — held up well and can serve as a template.

---
---

# Phase 2 — Second Disease Study: PMP22 / CMT

_The aim of Phase 2 is to explicitly track how experience with TTR/Amyloidosis changed the approach to PMP22/CMT — not just to repeat Phase 1._

1. **What am I studying?**
2. **Where do I find information?**
3. **What EMR data do I have?**
4. **Does EMR data confirm what literature says?**
5. **Does EMR data suggest anything new?**
6. **What did I build for the demo/figure?**
7. **What did this teach me for the next project?**
