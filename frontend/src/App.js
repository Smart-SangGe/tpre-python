import React, { useEffect, useState } from 'react';
import axios from 'axios';
import WebSocketComponent from './WebSocketComponent';
import './App.css';

function App() {
  const [node, setNode] = useState(null);
  const [heartbeat, setHeartbeat] = useState(null);
  const [nodesList, setNodesList] = useState([]);
  const [ip, setIp] = useState(''); 
  const [count, setCount] = useState('');

  const fetchNodes = async () => {
    try {
      const response = await axios.get('/server/show_nodes');
      setNodesList(response.data);
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
        <h1 className="glow">The server</h1>
        <div className="container">
          <div className="left-panel">
            <section>
              <h2 className="glow">get node</h2>
              <input
                type="text"
                value={ip}
                onChange={(e) => setIp(e.target.value)}
                placeholder="Enter node ip"
              />
              <button onClick={handleFetchNode}>send</button>
              {node ? <p>{JSON.stringify(node)}</p> : <p>here is nothing!</p>}
            </section>

            <section>
              <h2 className="glow">heartbeat</h2>
              <button onClick={handleFetchHeartbeat}>Get heartbeat</button>
              {heartbeat ? <p>{JSON.stringify(heartbeat)}</p> : <p>here is nothing!</p>}
            </section>

            <section>
              <h2 className="glow">nodes list</h2>
              <input
                type="number"
                value={count}
                onChange={(e) => setCount(e.target.value)}
                placeholder="Enter the number of nodes"
              />
              <button onClick={handleFetchNodesList}>Get node list</button>
              {nodesList.length > 0 ? (
                <ul>
                  {nodesList.map((node, index) => (
                    <li key={index}>{JSON.stringify(node)}</li>
                  ))}
                </ul>
              ) : (
                <p>here is nothing!</p>
              )}
            </section>
          </div>
          <div className="right-panel">
            <WebSocketComponent />
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;