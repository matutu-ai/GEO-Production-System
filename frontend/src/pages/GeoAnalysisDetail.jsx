import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Descriptions,
  List,
  Progress,
  Result,
  Space,
  Spin,
  Table,
  Tabs,
  Tag,
  Typography,
  message,
} from "antd";
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import {
  getGeoStatusMeta,
  isActiveGeoStatus,
  joinText,
} from "../utils";
import GeoArchitectureViewer from "../components/GeoArchitectureViewer";
import GeoExportList from "../components/GeoExportList";

function GeoAnalysisDetail() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exports, setExports] = useState([]);

  const load = useCallback(async () => {
    try {
      const data = await api.geoProject(projectId);
      setProject(data);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!isActiveGeoStatus(project?.status)) return undefined;
    const timer = setInterval(load, 2000);
    return () => clearInterval(timer);
  }, [project?.status, load]);

  useEffect(() => {
    if (project?.status !== "COMPLETED" || !projectId) return undefined;
    let cancelled = false;
    api
      .geoExports(projectId)
      .then((data) => {
        if (!cancelled) setExports(data.files || []);
      })
      .catch((err) => {
        if (!cancelled) message.error(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, project?.status]);

  const analysis = useMemo(() => {
    const raw = project?.analysis_result || {};
    return raw.result || raw;
  }, [project]);

  if (loading) {
    return <Spin size="large" style={{ display: "block", margin: "80px auto" }} />;
  }

  if (error || !project) {
    return (
      <Result
        status="error"
        title="GEO 分析项目加载失败"
        subTitle={error || "项目不存在"}
        extra={
          <Button onClick={() => navigate("/reports/geo-analysis")}>返回列表</Button>
        }
      />
    );
  }

  if (project.status === "FAILED") {
    return (
      <Result
        status="error"
        title="GEO 分析失败"
        subTitle={project.analysis_result?.error || "请检查输入资料后重新创建"}
        extra={
          <Button onClick={() => navigate("/reports/geo-analysis/new")}>
            重新创建分析
          </Button>
        }
      />
    );
  }

  const article = analysis.article || {};
  const entities = analysis.entities?.entities || [];
  const relationships = analysis.entities?.relationships || [];
  const keywordClusters = analysis.keyword_clusters || [];
  const intents = analysis.intents || [];
  const framework = analysis.framework || {};
  const score = analysis.score || {};

  const scoreItems = [
    { key: "entity_coverage", label: "实体覆盖", value: score.entity_coverage },
    { key: "keyword_coverage", label: "关键词覆盖", value: score.keyword_coverage },
    { key: "intent_match", label: "搜索意图匹配", value: score.intent_match },
    { key: "content_structure", label: "内容结构", value: score.content_structure },
    { key: "authority_score", label: "权威信号", value: score.authority_score },
  ];

  const tabs = [
    {
      key: "article",
      label: "文章分析",
      children: (
        <div>
          <Descriptions bordered column={1} size="small" style={{ marginBottom: 16 }}>
            <Descriptions.Item label="标题">
              {article.title || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="来源">
              {article.source || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="摘要">
              {article.summary || "-"}
            </Descriptions.Item>
          </Descriptions>
          <Card title="主题" size="small" style={{ marginBottom: 16 }}>
            <Space wrap>
              {(article.topics || []).map((topic) => (
                <Tag key={topic} color="blue">
                  {topic}
                </Tag>
              ))}
            </Space>
          </Card>
          <Card title="候选关键词" size="small">
            <Space wrap>
              {(article.keywords || []).map((keyword) => (
                <Tag key={keyword}>{keyword}</Tag>
              ))}
            </Space>
          </Card>
        </div>
      ),
    },
    {
      key: "entities",
      label: "实体图谱",
      children: (
        <div>
          <Table
            rowKey="name"
            size="small"
            pagination={false}
            style={{ marginBottom: 16 }}
            dataSource={entities}
            columns={[
              { title: "实体", dataIndex: "name" },
              { title: "类型", dataIndex: "type", width: 130 },
              {
                title: "置信度",
                dataIndex: "confidence",
                width: 220,
                render: (value) => (
                  <Progress percent={Number(value) || 0} size="small" />
                ),
              },
              { title: "提及次数", dataIndex: "mentions", width: 100 },
            ]}
          />
          <Card title="实体关系" size="small">
            <List
              dataSource={relationships}
              renderItem={(item) => (
                <List.Item>
                  <Typography.Text>
                    {item.source} → {item.relation} → {item.target}
                  </Typography.Text>
                </List.Item>
              )}
              locale={{ emptyText: "暂无实体关系" }}
            />
          </Card>
        </div>
      ),
    },
    {
      key: "keywords",
      label: "关键词簇",
      children: (
        <List
          grid={{ gutter: 16, xs: 1, sm: 1, md: 2 }}
          dataSource={keywordClusters}
          renderItem={(cluster) => (
            <List.Item>
              <Card title={cluster.cluster} size="small">
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="核心词">
                    {joinText(cluster.primary)}
                  </Descriptions.Item>
                  <Descriptions.Item label="扩展词">
                    {joinText(cluster.secondary)}
                  </Descriptions.Item>
                  <Descriptions.Item label="语义词">
                    {joinText(cluster.semantic)}
                  </Descriptions.Item>
                </Descriptions>
                <Table
                  rowKey="keyword"
                  size="small"
                  pagination={false}
                  dataSource={cluster.keywords || []}
                  columns={[
                    { title: "关键词", dataIndex: "keyword" },
                    { title: "类型", dataIndex: "type", width: 90 },
                    { title: "意图", dataIndex: "intent", width: 110 },
                    { title: "优先级", dataIndex: "priority", width: 80 },
                  ]}
                />
              </Card>
            </List.Item>
          )}
        />
      ),
    },
    {
      key: "intents",
      label: "搜索意图",
      children: (
        <Table
          rowKey="intent"
          size="small"
          dataSource={intents}
          columns={[
            { title: "意图", dataIndex: "intent" },
            { title: "名称", dataIndex: "label", width: 140 },
            {
              title: "占比",
              dataIndex: "share",
              width: 240,
              render: (value) => <Progress percent={Number(value) || 0} size="small" />,
            },
            {
              title: "关键词",
              dataIndex: "keywords",
              render: (value) => joinText(value),
            },
          ]}
        />
      ),
    },
    {
      key: "framework",
      label: "内容框架",
      children: (
        <div>
          <Card title="页面结构" size="small" style={{ marginBottom: 16 }}>
            <ul className="geo-framework-list">
              {(framework.structure || []).map((item) => (
                <li key={`${item.heading}-${item.level}`}>
                  <Typography.Text strong>{item.heading}</Typography.Text>
                  <Typography.Paragraph type="secondary" style={{ marginBottom: 4 }}>
                    {item.purpose}
                  </Typography.Paragraph>
                </li>
              ))}
            </ul>
          </Card>
          <Card title="FAQ" size="small" style={{ marginBottom: 16 }}>
            <List
              dataSource={framework.faq || []}
              renderItem={(item) => (
                <List.Item>
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Typography.Text strong>{item.question}</Typography.Text>
                    <Typography.Text type="secondary">
                      {item.answer}
                    </Typography.Text>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
          <Card title="优化建议" size="small" style={{ marginBottom: 16 }}>
            <List
              dataSource={framework.recommendations || []}
              renderItem={(item) => (
                <List.Item>
                  <Typography.Text>{item}</Typography.Text>
                </List.Item>
              )}
            />
          </Card>
          <Card title="Schema Markup" size="small">
            <pre className="geo-code-block">
              {framework.schema || framework.schema_markup || "-"}
            </pre>
          </Card>
        </div>
      ),
    },
    {
      key: "svg",
      label: "SVG 架构",
      children: (
        <GeoArchitectureViewer
          src={api.geoDownloadUrl(projectId, "architecture.svg")}
        />
      ),
    },
    {
      key: "exports",
      label: "导出文件",
      children: (
        <Card title="交付文件" size="small">
          <GeoExportList projectId={projectId} files={exports} />
        </Card>
      ),
    },
  ];

  return (
    <div>
      <div className="page-title-row">
        <Space align="center">
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate("/reports/geo-analysis")}
          >
            返回
          </Button>
          <div>
            <Typography.Title level={3} style={{ margin: 0 }}>
              {project.name || "GEO Analysis"}
            </Typography.Title>
            <Typography.Text type="secondary">
              {project.id} · {project.source || "直接输入"}
            </Typography.Text>
          </div>
        </Space>
        <Space>
          <Tag color={getGeoStatusMeta(project.status).color}>
            {getGeoStatusMeta(project.status).label}
          </Tag>
          {isActiveGeoStatus(project.status) && (
            <Progress
              percent={Number(project.progress) || 0}
              size="small"
              style={{ width: 150 }}
            />
          )}
          <Button icon={<ReloadOutlined />} onClick={load}>
            刷新
          </Button>
        </Space>
      </div>

      {isActiveGeoStatus(project.status) && (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          message="GEO 分析任务正在运行，页面会自动刷新。"
        />
      )}

      {project.status === "COMPLETED" && (
        <Card size="small" style={{ marginBottom: 16 }}>
          <Space size="large" align="center">
            <Progress
              type="dashboard"
              percent={Number(score.total) || 0}
              format={(percent) => `${percent || 0} 分`}
            />
            <div>
              <Typography.Title level={4} style={{ marginBottom: 8 }}>
                GEO 综合评分
              </Typography.Title>
              <Typography.Text type="secondary">
                基于实体覆盖、关键词覆盖、搜索意图、内容结构与权威信号
              </Typography.Text>
            </div>
          </Space>
          <div className="geo-score-grid" style={{ marginTop: 16 }}>
            {scoreItems.map((item) => (
              <div key={item.key} className="geo-score-item">
                <Typography.Text type="secondary">{item.label}</Typography.Text>
                <Typography.Title level={3} style={{ margin: "6px 0 0" }}>
                  {Number(item.value) || 0}
                </Typography.Title>
                <Progress
                  percent={Number(item.value) || 0}
                  size="small"
                  showInfo={false}
                />
              </div>
            ))}
          </div>
        </Card>
      )}

      <Tabs defaultActiveKey="article" items={tabs} />
    </div>
  );
}

export default GeoAnalysisDetail;
