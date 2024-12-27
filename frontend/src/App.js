import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './HomePage';
import NodePage from './NodePage';
import HeartbeatPage from './HeartbeatPage';
import NodesListPage from './NodesListPage';
import WebSocketComponent from './WebSocketComponent';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Header 部分仅放置导航或标题 */}
        <header className="App-header">
        </header>

        {/* Main 部分用来渲染路由的内容 */}
        <main className="App-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/node" element={<NodePage />} />
            <Route path="/heartbeat" element={<HeartbeatPage />} />
            <Route path="/nodes-list" element={<NodesListPage />} />
            <Route path="/logs" element={<WebSocketComponent />} />
          </Routes>
        </main>

        {/* Footer 部分 */}
        <footer className="App-footer">
          <p>&copy; 2024 Server Application</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
