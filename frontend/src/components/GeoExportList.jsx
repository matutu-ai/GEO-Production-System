import { Button, Space, Table, Tag, Typography } from "antd";
import {
  DownloadOutlined,
  FileImageOutlined,
  FileMarkdownOutlined,
  FilePdfOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import { api } from "../api";
import { formatFileSize } from "../utils";

function exportMeta(filename) {
  const meta = {
    ".md": { label: "Markdown", color: "blue", icon: <FileMarkdownOutlined /> },
    ".html": { label: "HTML", color: "cyan", icon: <FileTextOutlined /> },
    ".json": { label: "JSON", color: "default", icon: <FileTextOutlined /> },
    ".pdf": { label: "PDF", color: "red", icon: <FilePdfOutlined /> },
    ".svg": { label: "SVG", color: "purple", icon: <FileImageOutlined /> },
    ".png": { label: "PNG", color: "green", icon: <FileImageOutlined /> },
  };
  const key = Object.keys(meta).find((suffix) =>
    filename.toLowerCase().endsWith(suffix)
  );
  return meta[key] || { label: filename, color: "default", icon: <FileTextOutlined /> };
}

function GeoExportList({ projectId, files = [] }) {
  const columns = [
    {
      title: "文件",
      dataIndex: "filename",
      render: (filename) => {
        const meta = exportMeta(filename);
        return (
          <Space>
            {meta.icon}
            <Typography.Text strong>{filename}</Typography.Text>
          </Space>
        );
      },
    },
    {
      title: "格式",
      dataIndex: "filename",
      width: 140,
      render: (filename) => {
        const meta = exportMeta(filename);
        return <Tag color={meta.color}>{meta.label}</Tag>;
      },
    },
    {
      title: "大小",
      dataIndex: "size",
      width: 120,
      render: (size) => formatFileSize(size),
    },
    {
      title: "操作",
      key: "actions",
      width: 120,
      render: (_, record) => (
        <Button
          size="small"
          type="primary"
          ghost
          icon={<DownloadOutlined />}
          href={api.geoDownloadUrl(projectId, record.filename)}
          target="_blank"
          rel="noreferrer"
        >
          下载
        </Button>
      ),
    },
  ];

  if (!files.length) {
    return (
      <Typography.Paragraph type="secondary">
        暂无可下载文件
      </Typography.Paragraph>
    );
  }

  return (
    <Table
      rowKey="filename"
      size="small"
      pagination={false}
      columns={columns}
      dataSource={files}
    />
  );
}

export default GeoExportList;
