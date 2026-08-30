import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Descriptions,
  Form,
  Input,
  Progress,
  Radio,
  Space,
  Steps,
  Tag,
  Typography,
  message,
} from "antd";
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  EyeOutlined,
  PlayCircleOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import {
  getGeoStatusMeta,
  isActiveGeoStatus,
  unwrap,
} from "../utils";
import GeoArchitectureViewer from "../components/GeoArchitectureViewer";
import GeoExportList from "../components/GeoExportList";

const { TextArea } = Input;

function GeoAnalysisNew() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [current, setCurrent] = useState(0);
  const [inputValues, setInputValues] = useState(null);
  const [project, setProject] = useState(null);
  const [projectId, setProjectId] = useState("");
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState("");
  const [exports, setExports] = useState([]);

  const active = isActiveGeoStatus(project?.status);

  useEffect(() => {
    if (!projectId || !active) return undefined;
    let cancelled = false;
    const load = async () => {
      try {
        const next = await api.geoProject(projectId);
        if (!cancelled) {
          setProject(next);
          if (next.status === "COMPLETED") {
            setCurrent(2);
          }
        }
      } catch (err) {
        if (!cancelled) {
          message.error(err.message);
        }
      }
    };
    load();
    const timer = setInterval(load, 2000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [projectId, active]);

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
    return unwrap(raw);
  }, [project]);

  const score = analysis.score || {};
  const framework = analysis.framework || {};
  const scoreItems = [
    { label: "实体覆盖", value: score.entity_coverage },
    { label: "关键词覆盖", value: score.keyword_coverage },
    { label: "搜索意图匹配", value: score.intent_match },
    { label: "内容结构", value: score.content_structure },
    { label: "权威信号", value: score.authority_score },
  ];

  const handleNext = async () => {
    try {
      const values = await form.validateFields();
      setInputValues(values);
      setCurrent(1);
    } catch {
      // Ant Design form validation already shows the errors.
    }
  };

  const handleStart = async () => {
    if (!inputValues) return;
    setStarting(true);
    setStartError("");
    let createdId = "";
    try {
      const created = await api.geoCreateProject({
        name: inputValues.project_name,
        source: inputValues.source || "",
      });
      createdId = created.id;
      const running = await api.geoAnalyze({
        project_id: createdId,
        name: inputValues.project_name,
        source: inputValues.source || "",
        source_type: inputValues.source_type,
        content: inputValues.content || "",
        product_description: inputValues.product_description || "",
        company_info: inputValues.company_info || "",
      });
      setProjectId(createdId);
      setProject(running);
    } catch (err) {
      setStartError(err.message);
      if (createdId) {
        setProjectId(createdId);
      }
    } finally {
      setStarting(false);
    }
  };

  const steps = [
    { title: "资料输入" },
    { title: "AI 分析" },
    { title: "内容框架" },
    { title: "SVG 架构" },
    { title: "导出交付" },
  ];

  return (
    <div>
      <div className="page-title-row">
        <Space align="center">
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/reports/geo-analysis")}>
            返回
          </Button>
          <div>
            <Typography.Title level={3} style={{ margin: 0 }}>
              创建 GEO 分析
            </Typography.Title>
            <Typography.Text type="secondary">
              输入文章或官网资料，自动生成 GEO 评分、内容框架和 SVG 架构图
            </Typography.Text>
          </div>
        </Space>
      </div>

      <Card className="geo-wizard-card">
        <Steps
          current={current}
          items={steps}
          size="small"
          style={{ marginBottom: 28 }}
          responsive
        />

        {current === 0 && (
          <Form
            form={form}
            layout="vertical"
            initialValues={{
              project_name: "",
              source_type: "markdown",
              source: "",
              content: "",
              product_description: "",
              company_info: "",
            }}
          >
            <Form.Item
              label="项目名称"
              name="project_name"
              rules={[{ required: true, message: "请输入项目名称" }]}
            >
              <Input placeholder="例如：邦胜官网 GEO 内容分析" />
            </Form.Item>
            <Form.Item
              label="资料来源类型"
              name="source_type"
              rules={[{ required: true }]}
            >
              <Radio.Group>
                <Radio.Button value="url">URL</Radio.Button>
                <Radio.Button value="markdown">Markdown</Radio.Button>
                <Radio.Button value="html">HTML</Radio.Button>
                <Radio.Button value="text">TXT / 纯文本</Radio.Button>
              </Radio.Group>
            </Form.Item>
            <Form.Item
              noStyle
              shouldUpdate={(prev, next) => prev.source_type !== next.source_type}
            >
              {({ getFieldValue }) =>
                getFieldValue("source_type") === "url" ? (
                  <Form.Item
                    label="文章 URL"
                    name="source"
                    rules={[{ required: true, message: "请输入文章 URL" }]}
                  >
                    <Input placeholder="https://example.com/article" />
                  </Form.Item>
                ) : (
                  <Form.Item
                    label="文章内容"
                    name="content"
                    rules={[{ required: true, message: "请输入文章内容" }]}
                  >
                    <TextArea
                      rows={10}
                      placeholder="粘贴 Markdown、HTML 或纯文本内容"
                    />
                  </Form.Item>
                )
              }
            </Form.Item>
            <Form.Item label="产品描述（可选）" name="product_description">
              <TextArea
                rows={3}
                placeholder="例如：自动开箱机、自动包装设备、自动化包装生产线"
              />
            </Form.Item>
            <Form.Item label="企业信息（可选）" name="company_info">
              <TextArea
                rows={3}
                placeholder="例如：邦胜工业设备有限公司，专注工业自动化设备"
              />
            </Form.Item>
            <Button type="primary" onClick={handleNext}>
              下一步
            </Button>
          </Form>
        )}

        {current === 1 && (
          <div>
            <Card title="分析输入" size="small" style={{ marginBottom: 16 }}>
              <Descriptions bordered column={1} size="small">
                <Descriptions.Item label="项目名称">
                  {inputValues?.project_name}
                </Descriptions.Item>
                <Descriptions.Item label="资料来源">
                  {inputValues?.source_type}
                </Descriptions.Item>
                <Descriptions.Item label="URL / 内容">
                  {inputValues?.source || (inputValues?.content || "-").slice(0, 120)}
                </Descriptions.Item>
                <Descriptions.Item label="产品描述">
                  {inputValues?.product_description || "-"}
                </Descriptions.Item>
                <Descriptions.Item label="企业信息">
                  {inputValues?.company_info || "-"}
                </Descriptions.Item>
              </Descriptions>
            </Card>

            {!project && (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                loading={starting}
                onClick={handleStart}
              >
                开始 GEO 分析
              </Button>
            )}

            {startError && (
              <Alert
                type="error"
                showIcon
                style={{ marginBottom: 16 }}
                message="启动分析失败"
                description={startError}
              />
            )}

            {project && (
              <Card size="small" style={{ marginBottom: 16 }}>
                <Space direction="vertical" style={{ width: "100%" }}>
                  <Space>
                    <Tag color={getGeoStatusMeta(project.status).color}>
                      {getGeoStatusMeta(project.status).label}
                    </Tag>
                    <Typography.Text type="secondary">
                      {project.id}
                    </Typography.Text>
                  </Space>
                  <Progress percent={Number(project.progress) || 0} />
                  {active && (
                    <Alert
                      type="info"
                      showIcon
                      message="任务正在后台运行，页面会自动刷新进度。"
                    />
                  )}
                  {project.status === "COMPLETED" && (
                    <Alert
                      type="success"
                      showIcon
                      message="GEO 分析已完成，可以继续查看内容框架。"
                    />
                  )}
                  {project.status === "FAILED" && (
                    <Alert
                      type="error"
                      showIcon
                      message="GEO 分析失败"
                      description={
                        project.analysis_result?.error || "请检查输入资料后重试"
                      }
                    />
                  )}
                </Space>
              </Card>
            )}

            {project?.status === "COMPLETED" && (
              <Space>
                <Button type="primary" onClick={() => setCurrent(2)}>
                  查看内容框架
                </Button>
                <Button
                  icon={<EyeOutlined />}
                  onClick={() => navigate(`/reports/geo-analysis/${projectId}`)}
                >
                  查看完整详情
                </Button>
              </Space>
            )}
          </div>
        )}

        {current === 2 && (
          <div>
            <Card title="GEO 评分" size="small" style={{ marginBottom: 16 }}>
              <div className="geo-score-grid">
                {scoreItems.map((item) => (
                  <div key={item.label} className="geo-score-item">
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
                <div className="geo-score-item geo-score-total">
                  <Typography.Text type="secondary">综合评分</Typography.Text>
                  <Typography.Title level={3} style={{ margin: "6px 0 0", color: "#1f5eff" }}>
                    {Number(score.total) || 0}
                  </Typography.Title>
                  <Progress
                    percent={Number(score.total) || 0}
                    size="small"
                    showInfo={false}
                    strokeColor="#1f5eff"
                  />
                </div>
              </div>
            </Card>

            <Card title="内容结构" size="small" style={{ marginBottom: 16 }}>
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

            <Space>
              <Button onClick={() => setCurrent(1)}>返回</Button>
              <Button type="primary" onClick={() => setCurrent(3)}>
                查看 SVG 架构
              </Button>
            </Space>
          </div>
        )}

        {current === 3 && projectId && (
          <div>
            <GeoArchitectureViewer
              src={api.geoDownloadUrl(projectId, "architecture.svg")}
            />
            <Space style={{ marginTop: 16 }}>
              <Button onClick={() => setCurrent(2)}>返回</Button>
              <Button type="primary" onClick={() => setCurrent(4)}>
                导出交付物
              </Button>
            </Space>
          </div>
        )}

        {current === 4 && projectId && (
          <div>
            <Card title="交付文件" size="small" style={{ marginBottom: 16 }}>
              <GeoExportList projectId={projectId} files={exports} />
            </Card>
            <Space>
              <Button onClick={() => setCurrent(3)}>返回</Button>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={() => navigate(`/reports/geo-analysis/${projectId}`)}
              >
                查看项目详情
              </Button>
            </Space>
          </div>
        )}

        {current !== 0 && !project && !starting && !startError && (
          <div style={{ marginTop: 16 }}>
            <Button onClick={() => setCurrent(0)}>返回修改资料</Button>
          </div>
        )}
      </Card>
    </div>
  );
}

export default GeoAnalysisNew;
