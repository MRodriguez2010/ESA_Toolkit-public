# Employee Sentiment Analysis Toolkit

An intake workbook lets an analyst review counts before passing them to a reporting pipeline. This public adaptation includes a desktop file picker, a reproducible fictional workbook and a CLI for batch validation. Input fields are company, quarter, topic, favorable answers and total answers.

```sh
python -m pip install -r requirements.txt
python toolkit.py create intake.xlsx
python toolkit.py validate intake.xlsx
python toolkit.py export intake.xlsx verified.csv
```

To use the desktop flow, run `python toolkit.py desktop` with Tk installed. Validation checks the header, required labels, integer counts, count bounds and duplicate keys before writing the CSV. The fixture contains no individual responses. [Related repositories](https://github.com/search?q=user%3AMRodriguez2010+topic%3Aemployee-sentiment-analysis&type=repositories)
