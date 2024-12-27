import React from 'react';
import { Link } from 'react-router-dom';
import './App.css'; 
const HomePage = () => {
  return (
    <div>
      <h1 className="glow">The server</h1>
      <p>欢迎来到服务器管理页面。请选择一个操作：</p>
      <nav>
        <ul>
          <li><Link to="/node">Get Node</Link></li>
          <li><Link to="/heartbeat">Heartbeat</Link></li>
          <li><Link to="/nodes-list">Nodes List</Link></li>
          <li><Link to="/logs">Logs</Link></li>
        </ul>
      </nav>
    </div>
  );
};

export default HomePage;