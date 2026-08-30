import { useEffect, useRef, useState } from "react";
import { Button, Card, Space, Tooltip } from "antd";
import {
  DownloadOutlined,
  FullscreenExitOutlined,
  FullscreenOutlined,
  MinusOutlined,
  PlusOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

function GeoArchitectureViewer({
  src,
  filename = "architecture.svg",
  title = "GEO 架构图",
}) {
  const [zoom, setZoom] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const viewportRef = useRef(null);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(Boolean(document.fullscreenElement));
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () =>
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  const toggleFullscreen = async () => {
    if (!viewportRef.current) return;
    if (document.fullscreenElement) {
      await document.exitFullscreen();
    } else {
      await viewportRef.current.requestFullscreen();
    }
  };

  return (
    <Card
      title={title}
      extra={
        <Space>
          <Tooltip title="缩小">
            <Button
              size="small"
              icon={<MinusOutlined />}
              disabled={zoom <= 0.4}
              onClick={() => setZoom((value) => Math.max(0.4, value - 0.2))}
            />
          </Tooltip>
          <Tooltip title="放大">
            <Button
              size="small"
              icon={<PlusOutlined />}
              disabled={zoom >= 2.6}
              onClick={() => setZoom((value) => Math.min(2.6, value + 0.2))}
            />
          </Tooltip>
          <Tooltip title="重置">
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => setZoom(1)}
            />
          </Tooltip>
          <Tooltip title={isFullscreen ? "退出全屏" : "全屏查看"}>
            <Button
              size="small"
              icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
              onClick={toggleFullscreen}
            />
          </Tooltip>
          <Tooltip title="下载 SVG">
            <Button
              size="small"
              icon={<DownloadOutlined />}
              href={src}
              target="_blank"
              rel="noreferrer"
            />
          </Tooltip>
        </Space>
      }
    >
      <div ref={viewportRef} className="geo-svg-viewport">
        <img
          className="geo-svg-image"
          src={src}
          alt={title}
          title={filename}
          style={{ width: `${Math.round(zoom * 100)}%` }}
        />
      </div>
    </Card>
  );
}

export default GeoArchitectureViewer;
