import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Row,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
} from "antd";
import { EyeOutlined, FileTextOutlined } from "@ant-design/icons";
import { api } from "../api";

const statusColors = {
  queued: "processing",
  running: "processing",
  success: "success",
  error: "error",
};

const statusLabels = {
  queued: "排队中",
  running: "处理中",
  success: "已完成",
  error: "失败",
};

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
      title: "状态",
      dataIndex: "status",
      width: 110,
      render: (status) => (
        <Tag color={statusColors[status] || "default"}>
          {statusLabels[status] || status}
        </Tag>
      ),
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      width: 190,
      render: (value) => value || "-",
    },
    {
      title: "操作",
      key: "actions",
      width: 220,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            href={`/projects/${record.task_id}`}
          >
            详情
          </Button>
          <Button
            size="small"
            icon={<FileTextOutlined />}
            href={`/projects/${record.task_id}/report`}
          >
            报告
          </Button>
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
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="项目数量" value={data.stats.total || 0} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="完成数量"
              value={data.stats.completed || 0}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="处理中数量"
              value={data.stats.processing || 0}
              valueStyle={{ color: "#1f5eff" }}
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
