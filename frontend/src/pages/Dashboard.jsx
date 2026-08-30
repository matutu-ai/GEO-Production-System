import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  message,
  Popconfirm,
  Row,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
} from "antd";
import {
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  FileTextOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { api } from "../api";
import { getProjectId, getStatusMeta, isActiveStatus } from "../utils";

function getDownloadFilename(record) {
  const files = record.output_files || [];
  const matched =
    files.find((file) => file.endsWith("GEO客户分析报告.docx")) ||
    files.find((file) => file.endsWith(".docx")) ||
    files.find((file) => file.endsWith(".pdf")) ||
    files.find((file) => file.endsWith(".xlsx")) ||
    files[0];
  return matched ? matched.split("/").pop() : "";
}

function Dashboard() {
  const [data, setData] = useState({ projects: [], stats: {} });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setData(await api.projects());
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const timer = setInterval(load, 5000);
    return () => clearInterval(timer);
  }, []);

  const handleRerun = async (record) => {
    const projectId = getProjectId(record);
    try {
      await api.rerun(projectId);
      message.success("项目已重新开始分析");
      load();
    } catch (err) {
      message.error(err.message);
    }
  };

  const handleDelete = async (record) => {
    const projectId = getProjectId(record);
    try {
      await api.deleteProject(projectId);
      message.success("项目已删除");
      load();
    } catch (err) {
      message.error(err.message);
    }
  };

  const columns = [
    {
      title: "客户名称",
      dataIndex: "customer_name",
      render: (value) => value || "未命名项目",
    },
    {
      title: "行业",
      dataIndex: "industry",
      render: (value) => value || "-",
    },
    {
      title: "负责人",
      dataIndex: "owner",
      render: (value) => value || "-",
    },
    {
      title: "状态",
      dataIndex: "status",
      width: 110,
      render: (status) => (
        <Tag color={getStatusMeta(status).color}>
          {getStatusMeta(status).label}
        </Tag>
      ),
    },
    {
      title: "创建时间",
      dataIndex: "created_time",
      width: 190,
      render: (value) => value || "-",
    },
    {
      title: "操作",
      key: "actions",
      width: 430,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            href={`/projects/${getProjectId(record)}`}
          >
            查看
          </Button>
          <Button
            size="small"
            icon={<FileTextOutlined />}
            href={`/projects/${getProjectId(record)}/report`}
          >
            报告
          </Button>
          <Popconfirm
            title="重新生成 GEO 报告"
            description="将重新执行完整分析流程，并覆盖旧输出文件。"
            okText="重新生成"
            cancelText="取消"
            onConfirm={() => handleRerun(record)}
          >
            <Button
              size="small"
              icon={<ReloadOutlined />}
              disabled={isActiveStatus(record.status)}
            >
              重新生成
            </Button>
          </Popconfirm>
          <Button
            size="small"
            icon={<DownloadOutlined />}
            disabled={!getDownloadFilename(record)}
            href={
              getDownloadFilename(record)
                ? api.downloadUrl(getProjectId(record), getDownloadFilename(record))
                : undefined
            }
            target="_blank"
          >
            下载
          </Button>
          <Popconfirm
            title="确认删除该项目？"
            description="将同时删除该项目上传文件和输出报告。"
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
            onConfirm={() => handleDelete(record)}
          >
            <Button
              danger
              size="small"
              icon={<DeleteOutlined />}
              disabled={isActiveStatus(record.status)}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-title-row">
        <Typography.Title level={3} style={{ margin: 0 }}>
          Dashboard
        </Typography.Title>
        <Button type="primary" href="/create">
          创建项目
        </Button>
      </div>

      {error && (
        <Alert
          type="error"
          showIcon
          message="无法连接后端"
          description={error}
          style={{ marginBottom: 20 }}
        />
      )}

      <Row gutter={[16, 16]} className="section-block">
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic title="项目数量" value={data.stats.total || 0} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="完成数量"
              value={data.stats.completed || 0}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="处理中数量"
              value={data.stats.processing || 0}
              valueStyle={{ color: "#1f5eff" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic title="关键词数量" value={data.stats.keyword_count || 0} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic title="报告数量" value={data.stats.report_count || 0} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="平均GEO评分"
              value={data.stats.avg_geo_score || 0}
              suffix="/100"
            />
          </Card>
        </Col>
      </Row>

      <Card title="项目列表">
        <Table
          rowKey="task_id"
          loading={loading}
          columns={columns}
          dataSource={data.projects || []}
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: "暂无项目，请先创建 GEO 分析任务" }}
        />
      </Card>
    </div>
  );
}

export default Dashboard;
