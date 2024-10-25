import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './App.css';

const HeartbeatPage = () => {
  const [ip, setIp] = useState('');
  const [heartbeat, setHeartbeat] = useState(null);

  const fetchHeartbeat = async (ip) => {
    try {
      const response = await axios.get('/server/heartbeat', { params: { ip } });
      setHeartbeat(response.data);
    } catch (error) {
      console.error('Error fetching heartbeat:', error);
    }
  };

  const handleFetchHeartbeat = () => {
    fetchHeartbeat(ip);
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
      <h2 className="glow">Heartbeat</h2>
      <p>请输入节点 IP 地址以获取心跳状态信息：</p>
      <input
        type="text"
        value={ip}
        onChange={(e) => setIp(e.target.value)}
        placeholder="Enter node IP"
      />
      <button onClick={handleFetchHeartbeat}>Get Heartbeat</button>
      {heartbeat ? (
        <div className="heartbeat-info">
          <h3>Heartbeat Information:</h3>
          <div className="info-item"><strong>Status:</strong> {heartbeat.status}</div>
        </div>
      ) : (
        <p>这里没有任何信息！</p>
      )}
    </section>
  );
};

export default HeartbeatPage;