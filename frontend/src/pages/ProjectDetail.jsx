import { useCallback, useEffect, useState } from "react";
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
} from "antd";
import {
  ArrowLeftOutlined,
  FileTextOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { api } from "../api";
import { getStatusMeta, isActiveStatus, unwrap, joinText } from "../utils";

function ProjectDetail() {
  const { taskId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [shouldPoll, setShouldPoll] = useState(false);

  const load = useCallback(async () => {
    try {
      const detail = await api.project(taskId);
      setProject(detail);
      setShouldPoll(isActiveStatus(detail.status));
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!shouldPoll) {
      return undefined;
    }
    const timer = setInterval(load, 2000);
    return () => clearInterval(timer);
  }, [shouldPoll, load]);

  if (loading) {
    return <Spin size="large" style={{ display: "block", margin: "80px auto" }} />;
  }

  if (error || !project) {
    return (
      <Result
        status="error"
        title="项目加载失败"
        subTitle={error || "项目不存在"}
        extra={<Button href="/">返回 Dashboard</Button>}
      />
    );
  }

  const analysis = project.analysis || {};
  const company = unwrap(analysis.company_profile);
  const business = unwrap(analysis.business_analysis);
  const keywords = unwrap(analysis.keywords).keywords || [];
  const personas = unwrap(analysis.personas).personas || [];
  const content = unwrap(analysis.content_plan);
  const strategy = unwrap(analysis.strategy_plan);
  const monitor = unwrap(analysis.monitor_report);
  const geoScore = unwrap(analysis.geo_score);

  const keywordColumns = [
    { title: "关键词", dataIndex: "keyword" },
    { title: "类型", dataIndex: "type", width: 100 },
    { title: "意图", dataIndex: "intent", width: 110 },
    { title: "优先级", dataIndex: "priority", width: 90 },
    { title: "业务线", dataIndex: "business_line", width: 180 },
    { title: "客户类型", dataIndex: "customer_type", width: 130 },
    { title: "搜索阶段", dataIndex: "search_stage", width: 110 },
  ];

  const contentColumns = [
    { title: "日期", dataIndex: "日期", width: 90 },
    { title: "内容主题", dataIndex: "内容主题" },
    { title: "目标关键词", dataIndex: "目标关键词", width: 180 },
    { title: "目标用户", dataIndex: "目标用户", width: 140 },
    { title: "发布建议", dataIndex: "发布建议", width: 260 },
  ];

  const tabs = [
    {
      key: "company",
      label: "企业分析",
      children: (
        <Descriptions bordered column={1} size="small">
          <Descriptions.Item label="企业定位">
            {company.company_positioning || "-"}
          </Descriptions.Item>
          <Descriptions.Item label="行业">{company.industry || "-"}</Descriptions.Item>
          <Descriptions.Item label="产品">
            {joinText(company.products)}
          </Descriptions.Item>
          <Descriptions.Item label="服务">
            {joinText(company.services)}
          </Descriptions.Item>
          <Descriptions.Item label="目标客户">
            {joinText(company.target_customers)}
          </Descriptions.Item>
          <Descriptions.Item label="竞争优势">
            {joinText(company.advantages)}
          </Descriptions.Item>
          <Descriptions.Item label="客户痛点">
            {joinText(company.customer_pain_points)}
          </Descriptions.Item>
          <Descriptions.Item label="可信证据">
            {joinText(company.evidence)}
          </Descriptions.Item>
        </Descriptions>
      ),
    },
    {
      key: "business",
      label: "业务分析",
      children: (
        <List
          grid={{ gutter: 16, xs: 1, sm: 1, md: 2 }}
          dataSource={business.business_lines || []}
          renderItem={(line) => (
            <List.Item>
              <Card title={line.business_name} size="small">
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="产品">
                    {joinText(line.products)}
                  </Descriptions.Item>
                  <Descriptions.Item label="目标客户">
                    {joinText(line.target_customers)}
                  </Descriptions.Item>
                  <Descriptions.Item label="客户问题">
                    {joinText(line.customer_problems)}
                  </Descriptions.Item>
                  <Descriptions.Item label="购买意图">
                    {joinText(line.buying_intent)}
                  </Descriptions.Item>
                  <Descriptions.Item label="关键词方向">
                    {joinText(line.keywords_direction)}
                  </Descriptions.Item>
                  <Descriptions.Item label="内容方向">
                    {joinText(line.content_direction)}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </List.Item>
          )}
        />
      ),
    },
    {
      key: "keywords",
      label: "关键词",
      children: (
        <Table
          rowKey={(record) => `${record.type}-${record.keyword}`}
          columns={keywordColumns}
          dataSource={keywords}
          size="small"
          pagination={{ pageSize: 12 }}
          locale={{ emptyText: "暂无关键词数据" }}
        />
      ),
    },
    {
      key: "personas",
      label: "用户画像",
      children: (
        <List
          grid={{ gutter: 16, xs: 1, sm: 1, md: 2 }}
          dataSource={personas}
          renderItem={(persona) => (
            <List.Item>
              <Card title={persona.role} size="small">
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="关注点">
                    {joinText(persona.focus)}
                  </Descriptions.Item>
                  <Descriptions.Item label="痛点">
                    {joinText(persona.pain_points)}
                  </Descriptions.Item>
                  <Descriptions.Item label="搜索行为">
                    {joinText(persona.search_behavior)}
                  </Descriptions.Item>
                  <Descriptions.Item label="决策因素">
                    {joinText(persona.decision_factors)}
                  </Descriptions.Item>
                  <Descriptions.Item label="内容需求">
                    {joinText(persona.content_needs)}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </List.Item>
          )}
        />
      ),
    },
    {
      key: "content",
      label: "内容计划",
      children: (
        <div>
          <Card title="内容方向" size="small" style={{ marginBottom: 16 }}>
            <Table
              rowKey={(record) => record.content_topic}
              size="small"
              pagination={false}
              dataSource={content.content_directions || []}
              columns={[
                { title: "方向", dataIndex: "direction", width: 120 },
                { title: "主题", dataIndex: "content_topic" },
                { title: "关键词", dataIndex: "target_keyword", width: 200 },
                { title: "用户", dataIndex: "target_user", width: 140 },
                { title: "发布建议", dataIndex: "publish_suggestion", width: 260 },
              ]}
            />
          </Card>
          <Card title="30 天内容计划" size="small">
            <Table
              rowKey={(record) => record["日期"]}
              size="small"
              dataSource={content.plan || []}
              columns={contentColumns}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </div>
      ),
    },
    {
      key: "strategy",
      label: "策略",
      children: (
        <div>
          <Card size="small" style={{ marginBottom: 16 }}>
            <Typography.Paragraph>
              {strategy.summary || "暂无策略摘要"}
            </Typography.Paragraph>
          </Card>
          <List
            dataSource={strategy.priority_actions || []}
            renderItem={(action) => (
              <List.Item>
                <Card size="small" style={{ width: "100%" }}>
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Space>
                      <Tag color={action.priority === "P1" ? "red" : "blue"}>
                        {action.priority}
                      </Tag>
                      <Typography.Text strong>{action.action}</Typography.Text>
                    </Space>
                    <Typography.Text type="secondary">
                      原因：{action.reason}
                    </Typography.Text>
                    <Typography.Text type="secondary">
                      关键词：{joinText(action.related_keywords)}
                    </Typography.Text>
                    <Typography.Text type="secondary">
                      目标用户：{joinText(action.target_users)}
                    </Typography.Text>
                    <Typography.Text type="secondary">
                      内容：{action.content_needed}
                    </Typography.Text>
                  </Space>
                </Card>
              </List.Item>
            )}
          />
        </div>
      ),
    },
    {
      key: "score",
      label: "GEO评分",
      children: (
        <div>
          <Card size="small" style={{ marginBottom: 16 }}>
            <Space size="large" align="center">
              <Progress
                type="dashboard"
                percent={geoScore.score || 0}
                format={(percent) => `${percent || 0} 分`}
              />
              <div>
                <Typography.Title level={4} style={{ marginBottom: 8 }}>
                  {geoScore.level || "暂无评分"}
                </Typography.Title>
                <Typography.Text type="secondary">
                  评分维度：企业信息、关键词、内容、用户画像、AI推荐基础
                </Typography.Text>
              </div>
            </Space>
          </Card>
          <Card title="评分维度" size="small" style={{ marginBottom: 16 }}>
            <Table
              rowKey="dimension"
              size="small"
              pagination={false}
              dataSource={Object.entries(geoScore.dimensions || {}).map(
                ([dimension, value]) => ({
                  dimension,
                  value,
                })
              )}
              columns={[
                { title: "维度", dataIndex: "dimension" },
                {
                  title: "得分",
                  dataIndex: "value",
                  width: 260,
                  render: (value) => (
                    <Progress percent={Number(value) || 0} size="small" />
                  ),
                },
              ]}
            />
          </Card>
          <Card title="优化建议" size="small">
            <List
              dataSource={geoScore.recommendations || []}
              renderItem={(item) => (
                <List.Item>
                  <Typography.Text>{item}</Typography.Text>
                </List.Item>
              )}
            />
          </Card>
        </div>
      ),
    },
    {
      key: "monitor",
      label: "效果监控",
      children: (
        <div>
          <Card size="small" style={{ marginBottom: 16 }}>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="关键词数量">
                {monitor.keyword_count ?? "-"}
              </Descriptions.Item>
              <Descriptions.Item label="内容数量">
                {monitor.content_count ?? "-"}
              </Descriptions.Item>
              <Descriptions.Item label="用户画像数量">
                {monitor.persona_count ?? "-"}
              </Descriptions.Item>
              <Descriptions.Item label="策略动作数量">
                {monitor.priority_action_count ?? "-"}
              </Descriptions.Item>
            </Descriptions>
          </Card>
          <Card title="优化建议" size="small" style={{ marginBottom: 16 }}>
            <List
              dataSource={monitor.optimization_suggestions || []}
              renderItem={(item) => (
                <List.Item>
                  <Typography.Text>{item}</Typography.Text>
                </List.Item>
              )}
            />
          </Card>
          <Card title="下一步行动" size="small">
            <List
              dataSource={monitor.next_actions || []}
              renderItem={(item) => (
                <List.Item>
                  <Typography.Text>{item}</Typography.Text>
                </List.Item>
              )}
            />
          </Card>
        </div>
      ),
    },
  ];

  return (
    <div>
      <div className="page-title-row">
        <Space align="center">
          <Button icon={<ArrowLeftOutlined />} href="/">
            返回
          </Button>
          <div>
            <Typography.Title level={3} style={{ margin: 0 }}>
              {project.customer_name || "未命名项目"}
            </Typography.Title>
            <Typography.Text type="secondary">
              {project.industry || "未填写行业"} · {project.task_id}
            </Typography.Text>
          </div>
        </Space>
        <Space>
          <Tag color={getStatusMeta(project.status).color}>
            {getStatusMeta(project.status).label}
          </Tag>
          <Button icon={<ReloadOutlined />} onClick={load}>
            刷新
          </Button>
          <Button
            type="primary"
            icon={<FileTextOutlined />}
            href={`/projects/${taskId}/report`}
          >
            查看报告
          </Button>
        </Space>
      </div>

      {isActiveStatus(project.status) && (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          message={`项目状态：${getStatusMeta(project.status).label}，页面会自动刷新。`}
        />
      )}
      {project.status === "FAILED" && (
        <Alert
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          message="项目分析失败"
          description={project.error_message || project.message}
        />
      )}

      <Tabs defaultActiveKey="company" items={tabs} />
    </div>
  );
}

export default ProjectDetail;
