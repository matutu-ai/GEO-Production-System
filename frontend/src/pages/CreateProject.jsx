import { useState } from "react";
import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  message,
  Typography,
  Upload,
} from "antd";
import { InboxOutlined, PlayCircleOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const acceptedFormats = ".xlsx,.docx,.pdf";

function CreateProject() {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    const file = fileList[0]?.originFileObj;
    if (!file) {
      message.warning("请先上传客户资料文件");
      return;
    }

    const formData = new FormData();
    formData.append("customer_name", values.customer_name || "");
    formData.append("website", values.website || "");
    formData.append("industry", values.industry || "");
    formData.append("file", file);

    setSubmitting(true);
    try {
      const job = await api.createProject(formData);
      message.success("项目已创建，正在后台运行分析");
      navigate(`/projects/${job.project_id || job.task_id}`);
    } catch (err) {
      message.error(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="page-title-row">
        <Typography.Title level={3} style={{ margin: 0 }}>
          创建 GEO 项目
        </Typography.Title>
      </div>

      <Card>
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
          message="分析任务会在后台执行，提交后可在项目详情页查看进度和结果。"
        />
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            customer_name: "邦胜工业设备有限公司",
            website: "sdhdktsb.com",
            industry: "工业自动化设备",
          }}
        >
          <Form.Item
            label="客户名称"
            name="customer_name"
            rules={[{ required: true, message: "请输入客户名称" }]}
          >
            <Input placeholder="例如：邦胜工业设备有限公司" />
          </Form.Item>
          <Form.Item label="官网" name="website">
            <Input placeholder="例如：sdhdktsb.com" />
          </Form.Item>
          <Form.Item
            label="行业"
            name="industry"
            rules={[{ required: true, message: "请输入行业" }]}
          >
            <Input placeholder="例如：工业自动化设备" />
          </Form.Item>
          <Form.Item label="客户资料文件" required>
            <Upload.Dragger
              accept={acceptedFormats}
              maxCount={1}
              fileList={fileList}
              beforeUpload={() => false}
              onChange={({ fileList: next }) => setFileList(next.slice(-1))}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">拖拽或点击上传客户资料</p>
              <p className="ant-upload-hint">支持 xlsx、docx、pdf</p>
            </Upload.Dragger>
          </Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            icon={<PlayCircleOutlined />}
            loading={submitting}
          >
            开始分析
          </Button>
        </Form>
      </Card>
    </div>
  );
}

export default CreateProject;
