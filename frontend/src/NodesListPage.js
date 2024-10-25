import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './App.css';

const NodesListPage = () => {
  const [count, setCount] = useState('');
  const [nodesList, setNodesList] = useState([]);

  const fetchNodesList = async (count) => {
    try {
      const response = await axios.get('/server/send_nodes_list', { params: { count } });
      setNodesList(response.data);
    } catch (error) {
      console.error('Error fetching nodes list:', error);
    }
  };

  const handleFetchNodesList = () => {
    fetchNodesList(count);
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
      <h2 className="glow">Nodes List</h2>
      <p>请输入要获取的节点数量：</p>
      <input
        type="number"
        value={count}
        onChange={(e) => setCount(e.target.value)}
        placeholder="Enter the number of nodes"
      />
      <button onClick={handleFetchNodesList}>Get Node List</button>
      {nodesList.length > 0 ? (
        <div className="nodes-list">
          <h3>Nodes Information:</h3>
          <ul>
            {nodesList.map((node, index) => (
              <li key={index} className="info-item">
                {node}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p>这里没有任何信息！</p>
      )}
    </section>
  );
};

export default NodesListPage;