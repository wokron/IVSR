from functools import lru_cache
from typing import Any
from langchain_community.llms.baidu_qianfan_endpoint import QianfanLLMEndpoint
from langchain.chains.summarize import load_summarize_chain
from langchain_core.runnables import RunnablePick, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveJsonSplitter
from app.config import get_settings

from app.llm.prompts import (
    ML_PROMPT,
    REPORT_PROMPT,
    STATIC_PROMPT,
    STATIC_REFINE_PROMPT,
)


@lru_cache
def create_chain():
    settings = get_settings()

    llm = QianfanLLMEndpoint(
        model="Llama-2-13b-chat",
        qianfan_ak=settings.qianfan_ak,
        qianfan_sk=settings.qianfan_sk,
    )

    static_summary_chain = load_summarize_chain(
        llm,
        chain_type="refine",
        question_prompt=STATIC_PROMPT,
        refine_prompt=STATIC_REFINE_PROMPT,
        input_key="static_docs",
    ) | RunnablePick("output_text")

    ml_summary_chain = ML_PROMPT | llm | StrOutputParser()

    report_chain = (
        {"static_summary": static_summary_chain, "ml_summary": ml_summary_chain}
        | REPORT_PROMPT
        | llm
        | StrOutputParser()
    )

    return report_chain


async def llm_generate_report(
    chain: RunnableSerializable[Any, str],
    static_content: dict,
    ml_text: str,
):
    static_docs = RecursiveJsonSplitter().create_documents(
        texts=[static_content], convert_lists=True
    )

    result = await chain.ainvoke({"static_docs": static_docs, "ml_text": ml_text})
    return result
