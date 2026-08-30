import { Layout, Menu, Typography } from "antd";
import {
  DashboardOutlined,
  FileTextOutlined,
  PlusCircleOutlined,
} from "@ant-design/icons";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CreateProject from "./pages/CreateProject";
import ProjectDetail from "./pages/ProjectDetail";
import Report from "./pages/Report";

const { Header, Content, Sider } = Layout;

const menuItems = [
  { key: "/", icon: <DashboardOutlined />, label: "项目总览" },
  { key: "/create", icon: <PlusCircleOutlined />, label: "创建项目" },
];

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const selectedKey =
    menuItems.find((item) => item.key === location.pathname)?.key || "/";

  return (
    <Layout className="app-shell">
      <Sider width={220} theme="light" className="app-sider">
        <div className="app-brand">
          <FileTextOutlined />
          <Typography.Text strong>GEO Production</Typography.Text>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Typography.Title level={4} style={{ margin: 0 }}>
            GEO Production System
          </Typography.Title>
          <Typography.Text type="secondary">V2.0 Internal Console</Typography.Text>
        </Header>
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<CreateProject />} />
            <Route path="/projects/:taskId" element={<ProjectDetail />} />
            <Route path="/projects/:taskId/report" element={<Report />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
