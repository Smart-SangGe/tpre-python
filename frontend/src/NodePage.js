import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './App.css';

const NodePage = () => {
  const [ip, setIp] = useState('');
  const [node, setNode] = useState(null);

  const fetchNode = async (ip) => {
    try {
      const response = await axios.get('/server/get_node', { params: { ip } });
      const nodeData = response.data;
      const date = new Date(nodeData.current_time * 1000);
      nodeData.current_time = date.toLocaleString();
      setNode(nodeData);
    } catch (error) {
      console.error('Error fetching node:', error);
    }
  };

  const handleFetchNode = () => {
    fetchNode(ip);
  };

  return (
    <section>
      <nav>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/node">Get Node</Link></li>
          <li><Link to="/heartbeat">Heartbeat</Link></li>
          <li><Link to="/nodes-list">Nodes List</Link></li>
          <li><Link to="/logs">Logs</Link></li>
        </ul>
      </nav>
      <h2 className="glow">Get Node</h2>
      <p>请输入节点 IP 地址以获取节点信息：</p>
      <input
        type="text"
        value={ip}
        onChange={(e) => setIp(e.target.value)}
        placeholder="Enter node IP"
      />
      <button onClick={handleFetchNode}>Send</button>
      {node ? (
        <div className="node-info">
          <h3>Node Information:</h3>
          <div className="info-item"><strong>ID:</strong> {node.id}</div>
          <div className="info-item"><strong>Current Time:</strong> {node.current_time}</div>
        </div>
      ) : (
        <p>这里没有任何信息！</p>
      )}
    </section>
  );
};

export default NodePage;