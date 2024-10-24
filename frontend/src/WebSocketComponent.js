import React, { useEffect, useState, useRef, useCallback } from 'react';

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
            setLogs((prevLogs) => [...prevLogs, event.data]);  // 直接加入收到的消息
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
            <h2>The logs</h2>
            <div
                className="log-info"
                style={{ height: '550px', overflowY: 'scroll', backgroundColor: 'rgb(32, 28, 28)', padding: '10px' }}
            >
                {logs.map((log, index) => (
                    <p key={index} style={{ margin: '5px 0' }}>{log}</p>
                ))}
            </div>
        </div>
    );
};

export default WebSocketComponent;