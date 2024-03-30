import React from 'react';
import axios from 'axios';
import '../HistoricalDataAnalysis/AnalysisPage.css';
//import './App.css'; // Import the global styles

const AnalysisPage = () => {
  const [analysisData, setAnalysisData] = React.useState([]);

  React.useEffect(() => {
    axios.get('/api/analysis-data').then((response) => {
      setAnalysisData(response.data);
    });
  }, []);

  return (
    <div className="analysis-page">
      <h1>Stock Analysis</h1>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Analysis Date</th>
            <th>Analysis Result</th>
          </tr>
        </thead>
        <tbody>
          {analysisData.map((data) => (
            <tr key={data.symbol}>
              <td>{data.symbol}</td>
              <td>{data.analysisDate}</td>
              <td>{data.analysisResult}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AnalysisPage;