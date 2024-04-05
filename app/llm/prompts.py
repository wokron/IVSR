from langchain_core.prompts import PromptTemplate


STATIC_PROMPT_TEMPLATE = """\
Write a summary of the following json content:
------------
{text}
------------
SUMMARY:\
"""
STATIC_PROMPT = PromptTemplate.from_template(STATIC_PROMPT_TEMPLATE)


STATIC_REFINE_PROMPT_TEMPLATE = """\
Your job is to produce a final summary.
We have provided an existing summary up to a certain point:
------------
{existing_answer}
------------
We have the opportunity to refine the existing summary (only if needed) with some more context below.
------------
{text}
------------
Given the new context, refine the original summary (and do not mention the original summary again).
If the context isn't useful, return the original summary.
FINAL SUMMARY:\
"""
STATIC_REFINE_PROMPT = PromptTemplate.from_template(STATIC_REFINE_PROMPT_TEMPLATE)


ML_PROMPT_TEMPLATE = """\
The following content is the result of XmalPlus, an Android malware classifier.
Your job is to write a concise summary of the following json content:
------------
{ml_text}
------------
where:
- `apk_name` is the apk analyzed by XmalPlus.
- `malware_score` means the possibility that the application is malware. The value range is 0-1.
- `key_features` are the key features that define the application as a malware.
- `associate_features`: are other features associated with the key feature.
CONCISE SUMMARY:\
"""
ML_PROMPT = PromptTemplate.from_template(ML_PROMPT_TEMPLATE)


REPORT_PROMPT_TEMPLATE = """\
Your job is to produce a analysis report based on the following content:
------------
{static_summary}

{ml_summary}
------------
The analysis report should be in markdown format, and include as much information as possible.
The report should have these sections:
1. introduction (keep it simple)
2. reports of different parts of analysis (three to five parts here, exclude conclusion and recommendations)
3. conclusion
4. recommendations

For example, the format of your report could by like this:
SECURITY ANALYSIS REPORT
==============================

Introduction
------------
The following analysis...

Part1: XXX
----------
The apk requests ..., include
1. ...
2. ...

Conclusion
----------
...

Recommendations
---------------
...

(ATTENTION PLEASE, since this report is formal, you shouldn't answer me with something like "Sure, I can answer your question". You should only answer me with the content of your report.)
ANALYSIS REPORT:\
"""
REPORT_PROMPT = PromptTemplate.from_template(REPORT_PROMPT_TEMPLATE)
