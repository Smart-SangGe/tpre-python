import React, { useEffect, useState, useRef, useCallback } from 'react';

const WebSocketComponent = () => {
    const [logs, setLogs] = useState([]);
    const [nodes, setNodes] = useState([]);
    const wsRef = useRef(null);
    const heartbeatIntervalRef = useRef(null);

    const connectWebSocket = useCallback(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            return;  // 如果连接已经打开，不再重新连接
        }

        wsRef.current = new WebSocket('ws://localhost:8000/ws/logs');

        wsRef.current.onopen = () => {
            console.log('WebSocket 连接成功');
            heartbeatIntervalRef.current = setInterval(() => {
                if (wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.send(JSON.stringify({ type: 'heartbeat' }));
                }
            }, 10000); // 心跳包间隔调整为 10 秒
        };

        wsRef.current.onmessage = (event) => {
            setLogs((prevLogs) => [...prevLogs, event.data]);  // 直接加入收到的消息
        };
        

        wsRef.current.onerror = (error) => {
            console.error('WebSocket 错误: ', error);
        };

        wsRef.current.onclose = () => {
            console.log('WebSocket 连接关闭，尝试重新连接...');
            clearInterval(heartbeatIntervalRef.current);
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
            clearInterval(heartbeatIntervalRef.current);
        };
    }, [connectWebSocket]);
        // 获取节点信息
        const fetchNodes = useCallback(async () => {
            try {
                const response = await fetch('/server/show_nodes');
                const data = await response.json();
                setNodes(data);
            } catch (error) {
                console.error('Error fetching nodes:', error);
            }
        }, []);
    
        useEffect(() => {
            connectWebSocket();
            fetchNodes();  // 组件加载时获取节点信息
            return () => {
                if (wsRef.current) {
                    wsRef.current.close();
                }
                clearInterval(heartbeatIntervalRef.current);
            };
        }, [connectWebSocket, fetchNodes]);
    useEffect(() => {
        const logContainer = document.querySelector('.log-info');
        if (logContainer) {
            logContainer.scrollTop = logContainer.scrollHeight;
        }
    }, [logs]);

    return (
        <div>
            <h1>节点记录信息</h1>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>IP</th>
                        <th>Last Heartbeat</th>
                    </tr>
                </thead>
                <tbody>
                    {nodes.map((node) => (
                        <tr key={node[0]}>
                            <td>{node[0]}</td>
                            <td>{node[1]}</td>
                            <td>{new Date(node[2] * 1000).toLocaleString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <h2>日志信息</h2>
            <div
                className="log-info"
                style={{ height: '300px', overflowY: 'scroll', background: '#fff', padding: '10px' }}
            >
                {logs.map((log, index) => (
                    <p key={index} style={{ margin: '5px 0' }}>{log}</p>
                ))}
            </div>
        </div>
    );
};

export default WebSocketComponent;
