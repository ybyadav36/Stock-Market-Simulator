import React from 'react';
import { Line } from 'react-chartjs-2';
import '../TrendGraphs/TrendGraphs.css';
//import './App.css'; // Import the global styles

const TrendGraph = () => {
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Stock Price',
        data: [120, 150, 130, 140, 160, 155, 145, 150, 160, 170, 165, 180],
        borderColor: '#4caf50',
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    scales: {
      yAxes: [
        {
          ticks: {
            beginAtZero: true,
          },
        },
      ],
    },
  };

  return <Line data={data} options={options} />;
};

export default TrendGraph;