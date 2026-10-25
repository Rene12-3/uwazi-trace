# Contributing

Thank you for helping. This project asks for more care than most because its outputs concern real institutions and people.

## Ground rules
1. **Evidence, not accusation.** Every output must show the data, the peer baseline, uncertainty, innocent explanations and a source.
2. **No sensitive inputs.** Never use ethnicity, religion, party, region-as-proxy or personal names as signals. Never infer kinship from surnames.
3. **Synthetic data only** in issues, tests and examples.
4. **Neutral language.** Use "unusual relative to peers" and "review priority". Avoid "suspicious", "corrupt", "scandal".
5. **A false merge of people is worse than a false split.**

## Setup
    pip install -r requirements-dev.txt
    make test && make lint
    streamlit run streamlit_app.py

## Adding an indicator
1. Open an issue using the *Indicator proposal* template.
2. Write the spec in `docs/INDICATORS.md` first, including legitimate explanations and failure modes.
3. Implement it in `src/uwazi/indicators.py`, register it in `INDICATORS`, and add tests, including a planted-pattern test in the synthetic generator.
4. Report precision and recall on the synthetic benchmark, and explain what it does not tell us.
