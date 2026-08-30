"""Tests for document ingestion and knowledge extraction pipeline."""

from __future__ import annotations

from pathlib import Path

from agents.company_agent import CompanyAgent
from agents.knowledge_agent.agent import KnowledgeExtractAgent
from app.document_engine.document_pipeline import DocumentPipeline

INPUT_DIR = Path(__file__).resolve().parents[1] / "input"


def test_document_pipeline_parses_and_chunks() -> None:
    result = DocumentPipeline().process(str(INPUT_DIR / "demo_customer.docx"))

    assert result["document"]["format"] == "docx"
    assert "邦胜工业设备有限公司" in result["document"]["content"]
    assert result["chunks"]
    assert all(chunk["chunk_id"] for chunk in result["chunks"])
    assert result["knowledge"]["company"] == ["邦胜工业设备有限公司"]
    assert "自动开箱机" in result["knowledge"]["products"]


def test_knowledge_agent_accepts_pipeline_output() -> None:
    pipeline_result = DocumentPipeline().process(str(INPUT_DIR / "demo_customer.pdf"))
    agent_result = KnowledgeExtractAgent().run(
        {
            "document": pipeline_result,
            "customer_profile": {},
            "raw_information": pipeline_result["document"]["content"],
        }
    )

    assert agent_result["status"] == "success"
    assert agent_result["task"] == "knowledge_extraction"
    assert agent_result["next_action"] == "company_analysis"
    assert agent_result["confidence"] >= 60
    assert agent_result["result"]["company"]["company_name"] == "邦胜工业设备有限公司"
    assert agent_result["result"]["products"]
    assert agent_result["result"]["market"]["ai_questions"]


def test_company_agent_accepts_natural_language_profile() -> None:
    content = """祁阳县维特家瓷砖仓储中心企业介绍
一、企业简介
本中心是本地瓷砖仓储直销服务商，为业主、装修公司、工程方提供瓷砖产品。
四、产品体系
1. 大角鹿超耐磨大理石瓷砖（室内全空间系列）
2. 广陶别墅外墙砖（外立面全系列）
五、全流程服务体系
1. 售前咨询与选品服务
"""
    knowledge_result = KnowledgeExtractAgent().run(
        {
            "document": {"document": {"content": content}},
            "customer_profile": {},
            "raw_information": "",
        }
    )
    company_result = CompanyAgent().run(
        {
            "name": "祁阳县维特家瓷砖仓储中心",
            "website": "",
            "industry": "",
            "products": [],
            "knowledge_extract": knowledge_result,
        }
    )

    assert company_result["status"] == "success"
    assert company_result["result"]["company_name"] == "祁阳县维特家瓷砖仓储中心"
    assert company_result["result"]["industry"] == "建筑装饰装修"
    assert "大角鹿超耐磨大理石瓷砖" in company_result["result"]["products"]
    assert "广陶别墅外墙砖" in company_result["result"]["products"]
