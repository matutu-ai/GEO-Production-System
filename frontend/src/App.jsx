import { useEffect, useState } from "react";
import { Button, Layout, Menu, Space, Spin, Typography } from "antd";
import {
  DashboardOutlined,
  FileTextOutlined,
  PlusCircleOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  AUTH_EXPIRED_EVENT,
  api,
  clearAuth,
  getCurrentUser,
  getToken,
} from "./api";
import Dashboard from "./pages/Dashboard";
import CreateProject from "./pages/CreateProject";
import ProjectDetail from "./pages/ProjectDetail";
import Report from "./pages/Report";
import Login from "./pages/Login";
import Reports from "./pages/Reports";

const { Header, Content, Sider } = Layout;

const menuItems = [
  { key: "/", icon: <DashboardOutlined />, label: "项目总览" },
  { key: "/create", icon: <PlusCircleOutlined />, label: "创建项目" },
  { key: "/reports", icon: <FileTextOutlined />, label: "报告中心" },
];

const CLIENT_REPORT_PATHS = [
  "/reports",
  "/projects/",
];

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [, setAuthVersion] = useState(0);
  const [tokenReady, setTokenReady] = useState(!getToken());
  const token = getToken();
  const user = getCurrentUser();
  const isLoginPage = location.pathname === "/login";
  const isClient = user.role === "CLIENT";
  const isClientReportPath = CLIENT_REPORT_PATHS.some((path) =>
    location.pathname.startsWith(path)
  );
  const visibleMenuItems = isClient
    ? menuItems.filter((item) => item.key === "/reports")
    : menuItems;
  const selectedKey =
    visibleMenuItems.find((item) => item.key === location.pathname)?.key || "/";

  useEffect(() => {
    const handleAuthExpired = () => {
      clearAuth();
      setAuthVersion((version) => version + 1);
      navigate("/login", { replace: true });
    };
    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired);
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired);
  }, [navigate]);

  useEffect(() => {
    if (!token || isLoginPage) {
      setTokenReady(true);
      return undefined;
    }

    let cancelled = false;
    setTokenReady(false);
    api
      .me()
      .then(() => {
        if (!cancelled) {
          setTokenReady(true);
        }
      })
      .catch(() => {
        if (cancelled) {
          return;
        }
        clearAuth();
        setAuthVersion((version) => version + 1);
        setTokenReady(true);
        navigate("/login", { replace: true });
      });
    return () => {
      cancelled = true;
    };
  }, [token, isLoginPage, navigate]);

  if (!token && !isLoginPage) {
    return <Navigate to="/login" replace />;
  }
  if (token && isLoginPage) {
    return <Navigate to="/" replace />;
  }
  if (!token) {
    return <Login />;
  }
  if (!tokenReady) {
    return (
      <div className="auth-checking">
        <Spin size="large" tip="正在校验登录状态" />
      </div>
    );
  }
  if (isClient && !isClientReportPath) {
    return <Navigate to="/reports" replace />;
  }

  const handleLogout = () => {
    clearAuth();
    navigate("/login");
  };

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
          items={visibleMenuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Space>
            <Typography.Title level={4} style={{ margin: 0 }}>
              GEO Production System
            </Typography.Title>
            <Typography.Text type="secondary">Beta Internal Platform</Typography.Text>
          </Space>
          <Space>
            <Typography.Text>
              {user.display_name || user.username} · {user.role}
            </Typography.Text>
            <Button size="small" icon={<LogoutOutlined />} onClick={handleLogout}>
              退出
            </Button>
          </Space>
        </Header>
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<CreateProject />} />
            <Route path="/projects/:taskId" element={<ProjectDetail />} />
            <Route path="/projects/:taskId/report" element={<Report />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
