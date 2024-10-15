import React, { useEffect, useState } from 'react';
import axios from 'axios';
import WebSocketComponent from './WebSocketComponent';

function App() {
  const [nodes, setNodes] = useState([]);
  const [node, setNode] = useState(null);
  const [heartbeat, setHeartbeat] = useState(null);
  const [nodesList, setNodesList] = useState([]);
  const [ip, setIp] = useState(''); 
  const [count, setCount] = useState('');

  const fetchNodes = async () => {
    try {
      const response = await axios.get('/server/show_nodes');
      setNodes(response.data);
    } catch (error) {
      console.error('Error fetching nodes:', error);
    }
  };

  const fetchNode = async (ip) => {
    try {
      const response = await axios.get('/server/get_node', { params: { ip } });
      setNode(response.data);
    } catch (error) {
      console.error('Error fetching node:', error);
    }
  };

  const fetchHeartbeat = async (ip) => {
    try {
      const response = await axios.get('/server/heartbeat', { params: { ip } });
      setHeartbeat(response.data);
    } catch (error) {
      console.error('Error fetching heartbeat:', error);
    }
  };

  const fetchNodesList = async (count) => {
    try {
      const response = await axios.get('/server/send_nodes_list', { params: { count } });
      setNodesList(response.data);
    } catch (error) {
      console.error('Error fetching nodes list:', error);
    }
  };

  useEffect(() => {
    fetchNodes(); // 获取所有节点
  }, []);

  const handleFetchNode = () => {
    fetchNode(ip); // 根据输入的 IP 获取单个节点
  };

  const handleFetchHeartbeat = () => {
    fetchHeartbeat(ip); // 根据输入的 IP 获取心跳信息
  };

  const handleFetchNodesList = () => {
    fetchNodesList(count); // 根据输入的数量获取节点列表
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>中央服务器路由</h1>

        <h2>所有节点</h2>
        {nodes.length > 0 ? (
          <ul>
            {nodes.map((node, index) => (
              <li key={index}>{JSON.stringify(node)}</li>
            ))}
          </ul>
        ) : (
          <p>没有节点数据</p>
        )}

        <h2>单个节点</h2>
        <input
          type="text"
          value={ip}
          onChange={(e) => setIp(e.target.value)}
          placeholder="输入节点 IP"
        />
        <button onClick={handleFetchNode}>获取节点</button>
        {node ? <p>{JSON.stringify(node)}</p> : <p>没有单个节点数据</p>}

        <h2>心跳信息</h2>
        <button onClick={handleFetchHeartbeat}>获取心跳信息</button>
        {heartbeat ? <p>{JSON.stringify(heartbeat)}</p> : <p>没有心跳数据</p>}

        <h2>节点列表</h2>
        <input
          type="number"
          value={count}
          onChange={(e) => setCount(e.target.value)}
          placeholder="输入节点数量"
        />
        <button onClick={handleFetchNodesList}>获取节点列表</button>
        {nodesList.length > 0 ? (
          <ul>
            {nodesList.map((node, index) => (
              <li key={index}>{JSON.stringify(node)}</li>
            ))}
          </ul>
        ) : (
          <p>没有节点列表数据</p>
        )}
      </header>
      <WebSocketComponent/>
    </div>
  );
}

export default App;