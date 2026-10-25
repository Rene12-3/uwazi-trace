# Ethics, neutrality and legal considerations

*This document is a framework for decisions, not legal advice. Have a Kenyan lawyer review it before real data is used.*

## Principles
1. **Evidence first.** Show data, baseline, uncertainty, innocent explanations, source and audit trail. Never a verdict.
2. **No scores for people.** The system produces review priorities for transactions and patterns. It does not rank politicians, officials or individuals.
3. **Humans decide.** The tool prompts questions. A qualified person investigates, and the decision is logged.
4. **Right of reply.** Nothing is published about a named entity without a logged opportunity to respond.
5. **Say what we cannot see.** Coverage and blind spots are shown first. "No alert" never means "clean".
6. **Neutral by construction.** The same rules apply to national government and every county.

## What the system will never use
Ethnicity, religion, party, region-as-proxy, or personal names as inputs. No kinship inference from surnames. Names carry no information about wrongdoing, and such inference is inaccurate, discriminatory and defamatory.
Only documented relationships from authoritative sources may ever be added, and person-level entity resolution requires at least two independent corroborating attributes. A false merge is worse than a false split.

## Neutrality safeguards
- Entities that publish more produce more flags. Raw alert counts are never compared across entities; exposure is shown instead.
- Quarterly published fairness audit of flag rates by county size, region and category.
- Pre-registered indicator definitions and a public changelog. Weights are set by expert elicitation, not fitted to prosecutions.
- An independent advisory board (professional bodies, civil society, academia, legal) and a funder-independence disclosure.
- A pre-election protocol: a freeze or advisory-board review on new entity-level public releases in sensitive windows.
- Neutral language: "unusual relative to peers", "review priority". Never "suspicious", "corrupt" or "scandal".

## Kenyan legal landscape to review (verify current text and status)
| Area | Why it matters |
|---|---|
| Constitution, Article 35 and the **Access to Information Act, 2016** | Basis for formal requests to institutions for award data and bills of quantities. Log every request |
| **Data Protection Act, 2019** | Directors and owners are personal data. Needs a lawful basis, purpose limitation, minimisation, a data protection impact assessment, and possible registration with the data commissioner. Journalism and research exemptions are conditional. Breach notification duties are short |
| **Computer Misuse and Cybercrimes Act, 2018** | Do not circumvent access controls or scrape behind logins. Respect robots.txt and terms of use |
| **Defamation (civil)** | Companies can sue too. Use neutral language and right of reply |
| **Public Procurement and Asset Disposal Act, 2015** and Regulations | Source of thresholds, methods and windows. Versioned rule tables are required because rules differ by entity type, category and year |
| **Public Finance Management Act, 2012** | Budget and reporting context |
| Evidence Act (electronic records) | Chain of custody for evidence packs |
| Copyright and terms of use | Archive for analysis; republish only what you may |

## Prohibited in this project
Leaked or confidential documents, tax data, non-public asset declarations, and anything obtained by circumventing access controls. Whistleblower material needs a separate, hardened workflow and legal protection, and is out of scope here.

## Publication policy (when real data is used)
Two thresholds: a higher bar for public releases than for verified reviewers. A legal checklist before publication, a logged right-of-reply, and a documented correction and takedown process with defined timelines.
