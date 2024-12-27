import React, { useEffect, useState, useRef, useCallback } from 'react';
import './App.css'; // 确保引入了样式文件

const WebSocketComponent = () => {
    const [logs, setLogs] = useState([]);
    const wsRef = useRef(null);

    const connectWebSocket = useCallback(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            return;  // 如果连接已经打开，不再重新连接
        }

        wsRef.current = new WebSocket('ws://localhost:8000/ws/logs');

        wsRef.current.onopen = () => {
            console.log('WebSocket 连接成功');
        };

        wsRef.current.onmessage = (event) => {
            setLogs((prevLogs) => [...prevLogs, JSON.parse(event.data)]);  // 解析 JSON 数据
        };

        wsRef.current.onerror = (error) => {
            console.error('WebSocket 错误: ', error);
        };

        wsRef.current.onclose = () => {
            console.log('WebSocket 连接关闭，尝试重新连接...');
            // 确保 WebSocket 连接在关闭后再进行重连
            setTimeout(() => {
                connectWebSocket();
            }, 5000);  // 延迟 5 秒再重连
        };
    }, []);

    useEffect(() => {
        connectWebSocket();
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connectWebSocket]);

    useEffect(() => {
        const logContainer = document.querySelector('.log-info');
        if (logContainer) {
            logContainer.scrollTop = logContainer.scrollHeight;
        }
    }, [logs]);

    return (
        <div>
            <h2 className="glow">The logs</h2>
            <p>这里显示服务器的日志信息：</p>
            <div className="log-info">
                {logs.map((log, index) => {
                    const [timestamp, message] = log.message.split(' - ', 2);
                    return (
                        <div key={index} className="log-entry">
                            <span className="log-timestamp">{timestamp}</span>
                            <span className="log-message"> - {message}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default WebSocketComponent;