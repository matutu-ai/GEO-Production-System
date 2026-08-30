import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Descriptions,
  List,
  Result,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
} from "antd";
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { api } from "../api";
import { getStatusMeta, isActiveStatus, unwrap, joinText } from "../utils";

const extensionIcons = {
  ".pdf": <FilePdfOutlined />,
  ".docx": <FileWordOutlined />,
  ".xlsx": <FileExcelOutlined />,
};

function Report() {
  const { taskId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    let timer;
    const load = async () => {
      try {
        const detail = await api.project(taskId);
        setProject(detail);
        setPolling(isActiveStatus(detail.status));
        setError("");
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
    if (polling) {
      timer = setInterval(load, 2000);
    }
    return () => clearInterval(timer);
  }, [taskId, polling]);

  if (loading) {
    return <Spin size="large" style={{ display: "block", margin: "80px auto" }} />;
  }

  if (error || !project) {
    return (
      <Result
        status="error"
        title="报告加载失败"
        subTitle={error || "项目不存在"}
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
  const isCompleted =
    project.status === "COMPLETED" || project.status === "success";
  const downloadFiles = (project.output_files || [])
    .map((file) => file.split("/").pop())
    .filter((file) => file);

  const renderSection = (title, children) => (
    <Card title={title} size="small" style={{ marginBottom: 20 }}>
      {children}
    </Card>
  );

  return (
    <div>
      <div className="page-title-row">
        <Space align="center">
          <Button icon={<ArrowLeftOutlined />} href={`/projects/${taskId}`}>
            返回详情
          </Button>
          <div>
            <Typography.Title level={3} style={{ margin: 0 }}>
              GEO 客户交付报告
            </Typography.Title>
            <Typography.Text type="secondary">
              {project.customer_name || "未命名项目"}
            </Typography.Text>
          </div>
        </Space>
        <Space wrap>
          {isCompleted &&
            downloadFiles.map((filename) => {
              const suffix = filename
                .slice(filename.lastIndexOf("."))
                .toLowerCase();
              return (
                <Button
                  key={filename}
                  icon={extensionIcons[suffix] || <DownloadOutlined />}
                  href={api.downloadUrl(taskId, filename)}
                >
                  {filename}
                </Button>
              );
            })}
        </Space>
      </div>

      {!isCompleted && (
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          message="报告尚未生成完成，请等待分析任务结束。"
        />
      )}

      {renderSection(
        "1 项目概览",
        <Descriptions bordered column={2} size="small">
          <Descriptions.Item label="客户名称">
            {project.customer_name || "-"}
          </Descriptions.Item>
          <Descriptions.Item label="官网">{project.website || "-"}</Descriptions.Item>
          <Descriptions.Item label="行业">{project.industry || "-"}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{project.created_at}</Descriptions.Item>
          <Descriptions.Item label="任务 ID">{project.task_id}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={getStatusMeta(project.status).color}>
              {getStatusMeta(project.status).label}
            </Tag>
          </Descriptions.Item>
        </Descriptions>
      )}

      {renderSection(
        "2 企业分析",
        <Descriptions bordered column={1} size="small">
          <Descriptions.Item label="企业定位">
            {company.company_positioning || "-"}
          </Descriptions.Item>
          <Descriptions.Item label="产品">
            {joinText(company.products)}
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
          <Descriptions.Item label="证据">
            {joinText(company.evidence)}
          </Descriptions.Item>
        </Descriptions>
      )}

      {renderSection(
        "3 业务机会分析",
        <List
          dataSource={business.business_lines || []}
          renderItem={(line) => (
            <List.Item>
              <Typography.Text strong>{line.business_name}</Typography.Text>
              <div>
                目标客户：{joinText(line.target_customers)} · 客户问题：
                {joinText(line.customer_problems)}
              </div>
            </List.Item>
          )}
        />
      )}

      {renderSection(
        "4 GEO关键词策略",
        <Table
          rowKey={(record) => `${record.type}-${record.keyword}`}
          size="small"
          pagination={{ pageSize: 10 }}
          dataSource={keywords}
          columns={[
            { title: "关键词", dataIndex: "keyword" },
            { title: "类型", dataIndex: "type", width: 100 },
            { title: "意图", dataIndex: "intent", width: 120 },
            { title: "优先级", dataIndex: "priority", width: 90 },
            { title: "业务线", dataIndex: "business_line", width: 200 },
          ]}
        />
      )}

      {renderSection(
        "5 用户画像分析",
        <List
          dataSource={personas}
          renderItem={(persona) => (
            <List.Item>
              <Typography.Text strong>{persona.role}</Typography.Text>
              <div>关注点：{joinText(persona.focus)}</div>
              <div>痛点：{joinText(persona.pain_points)}</div>
              <div>内容需求：{joinText(persona.content_needs)}</div>
            </List.Item>
          )}
        />
      )}

      {renderSection(
        "6 内容增长计划",
        <Table
          rowKey={(record) => record.content_topic}
          size="small"
          pagination={{ pageSize: 8 }}
          dataSource={content.content_directions || []}
          columns={[
            { title: "方向", dataIndex: "direction", width: 120 },
            { title: "主题", dataIndex: "content_topic" },
            { title: "关键词", dataIndex: "target_keyword", width: 200 },
            { title: "目标用户", dataIndex: "target_user", width: 140 },
          ]}
        />
      )}

      {renderSection(
        "7 GEO优化执行策略",
        <List
          dataSource={strategy.priority_actions || []}
          renderItem={(action) => (
            <List.Item>
              <Space align="start">
                <Tag color={action.priority === "P1" ? "red" : "blue"}>
                  {action.priority}
                </Tag>
                <div>
                  <Typography.Text strong>{action.action}</Typography.Text>
                  <div>
                    <Typography.Text type="secondary">
                      {action.reason} · {action.expected_value || "预计价值待补充"}
                    </Typography.Text>
                  </div>
                </div>
              </Space>
            </List.Item>
          )}
        />
      )}

      {renderSection(
        "8 30天执行路线图",
        <Table
          rowKey={(record) => record["日期"]}
          size="small"
          pagination={{ pageSize: 8 }}
          dataSource={content.plan || []}
          columns={[
            { title: "日期", dataIndex: "日期", width: 90 },
            { title: "内容主题", dataIndex: "内容主题" },
            { title: "目标关键词", dataIndex: "目标关键词", width: 200 },
            { title: "目标用户", dataIndex: "目标用户", width: 140 },
          ]}
        />
      )}
    </div>
  );
}

export default Report;
