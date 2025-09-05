# CONSORT-AI Extension

> Scope: The CONSORT-AI extension provides additional reporting guidelines for clinical trials evaluating interventions involving artificial intelligence (AI). It should be used alongside the CONSORT 2010 statement to ensure comprehensive reporting of AI-specific aspects.
>
> Reference: https://www.nature.com/articles/s41591-020-1034-x

## Instructions
- Use task list items for checklist boxes; these become interactive checkboxes in PDF.
- Use a span with class `.textfield` for free‑text fields.
- Complete these items IN ADDITION to all applicable CONSORT 2010 items.
- Report all 14 CONSORT-AI extension items.

## CONSORT-AI Extension Items

### Title and Abstract

- [ ] **CONSORT-AI 1a:** In the title, identification of the study as a clinical trial of an AI intervention
- [ ] **CONSORT-AI 1b:** In the abstract, identification of the AI intervention

### Introduction

- [ ] **CONSORT-AI 2a:** For the AI intervention, description of the intended use, the intended users, and the stage of development

### Methods - Participants

- [ ] **CONSORT-AI 4a(i):** For the AI intervention, provide a clear description of the input data, including how the input data relates to the participant
- [ ] **CONSORT-AI 4a(ii):** For the AI intervention, description of the output provided by the AI intervention

### Methods - Interventions

- [ ] **CONSORT-AI 5(i):** For the AI intervention, specify the version of the AI intervention and describe its integration into the clinical workflow
- [ ] **CONSORT-AI 5(ii):** For the AI intervention, provide a description of the development environment and the deployment environment
- [ ] **CONSORT-AI 5(iii):** For the AI intervention, provide sufficient detail about the AI intervention so that someone could feasibly reproduce the AI intervention

### Methods - Outcomes

- [ ] **CONSORT-AI 6b:** For the AI intervention, describe any interoperability, user experience considerations, or human-AI interaction issues that could affect trial outcomes

### Methods - Statistical Analysis

- [ ] **CONSORT-AI 12a:** Describe the statistical methods used to evaluate the AI intervention during the trial, including any model retraining or updates

### Results - Participant Flow

- [ ] **CONSORT-AI 13b:** For the AI intervention, provide details of any participants excluded because of inabilities of the AI intervention to provide an output

### Results - Baseline Data

- [ ] **CONSORT-AI 15:** For the AI intervention, describe the baseline demographic characteristics of the datasets used to train and validate the AI intervention

### Results - Outcomes and Estimation

- [ ] **CONSORT-AI 17a:** For the AI intervention, provide effect size estimates and confidence intervals for AI-relevant outcomes

### Discussion - Harms

- [ ] **CONSORT-AI 19:** Report details of any adverse events related to the AI intervention and any consequences of failures of the AI intervention to provide an output

## Additional AI-Specific Considerations

### Input Data Characteristics
[Describe input data types, quality requirements, and preprocessing]{.textfield name=ai_input_data width=12cm}

### AI Model Information
[Document model architecture, training data, validation approach]{.textfield name=ai_model_info width=12cm}

### Human-AI Interaction
[Describe how users interact with the AI system and any usability considerations]{.textfield name=human_ai_interaction width=12cm}

### Performance Monitoring
[Report on AI performance during the trial, including any retraining or updates]{.textfield name=ai_performance width=12cm}

### Deployment Context
[Describe the clinical environment where AI was deployed vs development environment]{.textfield name=deployment_context width=12cm}

## Provenance
- Source: Nature Medicine. 2020;26:1364–1374. doi:10.1038/s41591-020-1034-x
- Version: 2020
- License: CC-BY-4.0
- Note: Use this extension alongside CONSORT 2010 main checklist
