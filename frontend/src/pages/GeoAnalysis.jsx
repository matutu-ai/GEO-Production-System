import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Button,
  Card,
  Col,
  Progress,
  Row,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import {
  ApartmentOutlined,
  EyeOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { getGeoStatusMeta, isActiveGeoStatus } from "../utils";

function GeoAnalysis() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await api.geoProjects();
      setProjects(data.projects || []);
    } catch (err) {
      message.error(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const stats = useMemo(() => {
    const completed = projects.filter(
      (project) => project.status === "COMPLETED"
    ).length;
    const processing = projects.filter((project) =>
      isActiveGeoStatus(project.status)
    ).length;
    const failed = projects.filter(
      (project) => project.status === "FAILED"
    ).length;
    return { total: projects.length, completed, processing, failed };
  }, [projects]);

  const columns = [
    {
      title: "项目名称",
      dataIndex: "name",
      render: (value, record) => (
        <Space direction="vertical" size={2}>
          <Typography.Text strong>{value || "未命名项目"}</Typography.Text>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {record.id}
          </Typography.Text>
        </Space>
      ),
    },
    {
      title: "资料来源",
      dataIndex: "source",
      ellipsis: true,
      render: (value) => value || "直接输入",
    },
    {
      title: "状态",
      dataIndex: "status",
      width: 130,
      render: (status) => {
        const meta = getGeoStatusMeta(status);
        return <Tag color={meta.color}>{meta.label}</Tag>;
      },
    },
    {
      title: "进度",
      dataIndex: "progress",
      width: 170,
      render: (progress, record) =>
        isActiveGeoStatus(record.status) ? (
          <Progress percent={Number(progress) || 0} size="small" />
        ) : (
          <Typography.Text type="secondary">
            {record.status === "COMPLETED" ? "100%" : "-"}
          </Typography.Text>
        ),
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      width: 210,
      render: (value) => value || "-",
    },
    {
      title: "操作",
      key: "actions",
      width: 170,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            type="primary"
            ghost
            icon={<EyeOutlined />}
            onClick={() => navigate(`/reports/geo-analysis/${record.id}`)}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-title-row">
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            GEO Analysis
          </Typography.Title>
          <Typography.Text type="secondary">
            对文章、官网内容与资料做 GEO 结构化分析并生成 SVG 架构图
          </Typography.Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate("/reports/geo-analysis/new")}
        >
          创建 GEO 分析
        </Button>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 18 }}>
        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic title="项目总数" value={stats.total} prefix={<ApartmentOutlined />} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title="已完成"
              value={stats.completed}
              valueStyle={{ color: "#2f9e44" }}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title="处理中"
              value={stats.processing}
              valueStyle={{ color: "#1f5eff" }}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title="失败"
              value={stats.failed}
              valueStyle={{ color: "#d9363e" }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="GEO 分析项目">
        <Table
          rowKey="id"
          loading={loading}
          columns={columns}
          dataSource={projects}
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: "暂无 GEO 分析项目" }}
        />
      </Card>
    </div>
  );
}

export default GeoAnalysis;
