import { useEffect, useState } from "react";
import {
  Button,
  Card,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import {
  ApartmentOutlined,
  DownloadOutlined,
  EyeOutlined,
  FilePdfOutlined,
  FileWordOutlined,
} from "@ant-design/icons";
import { api, getCurrentUser } from "../api";
import { getProjectId, getStatusMeta } from "../utils";

function findReport(project, suffix) {
  return (project.output_files || [])
    .map((file) => file.split("/").pop())
    .find((file) => file.toLowerCase().endsWith(suffix));
}

function Reports() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = getCurrentUser();

  const load = async () => {
    try {
      const data = await api.projects();
      setProjects(data.projects || []);
    } catch (err) {
      message.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
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
      title: "报告数量",
      dataIndex: "reports",
      width: 110,
      render: (reports) => reports?.length || 0,
    },
    {
      title: "操作",
      key: "actions",
      width: 360,
      render: (_, record) => {
        const projectId = getProjectId(record);
        const docx = findReport(record, ".docx");
        const pdf = findReport(record, ".pdf");
        return (
          <Space>
            <Button
              size="small"
              icon={<EyeOutlined />}
              href={`/projects/${projectId}/report`}
            >
              在线预览
            </Button>
            <Button
              size="small"
              icon={<FileWordOutlined />}
              disabled={!docx}
              href={docx ? api.downloadUrl(projectId, docx) : undefined}
              target="_blank"
            >
              DOCX
            </Button>
            <Button
              size="small"
              icon={<FilePdfOutlined />}
              disabled={!pdf}
              href={pdf ? api.downloadUrl(projectId, pdf) : undefined}
              target="_blank"
            >
              PDF
            </Button>
            {record.output_files?.length > 0 && (
              <Button
                size="small"
                icon={<DownloadOutlined />}
                href={`/projects/${projectId}/report`}
              >
                全部文件
              </Button>
            )}
          </Space>
        );
      },
    },
  ];

  return (
    <div>
      <div className="page-title-row">
        <Typography.Title level={3} style={{ margin: 0 }}>
          报告中心
        </Typography.Title>
        {user.role !== "CLIENT" && (
          <Button
            type="primary"
            icon={<ApartmentOutlined />}
            href="/reports/geo-analysis"
          >
            GEO 分析中心
          </Button>
        )}
      </div>
      <Card title="客户交付报告">
        <Table
          rowKey="task_id"
          loading={loading}
          columns={columns}
          dataSource={projects.filter(
            (project) => project.status === "COMPLETED"
          )}
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: "暂无已完成报告" }}
        />
      </Card>
    </div>
  );
}

export default Reports;
