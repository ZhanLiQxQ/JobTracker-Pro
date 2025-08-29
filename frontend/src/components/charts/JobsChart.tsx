import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Job } from '../../types/job.types';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface JobsChartProps {
  jobs: Job[];
}

export const JobsChart = ({ jobs }: JobsChartProps) => {
  // Group jobs by type for the chart
  const jobTypes = [...new Set(jobs.map(job => job.type))];
  const data = {
    labels: jobTypes,
    datasets: [
      {
        label: 'Jobs by Type',
        data: jobTypes.map(type => jobs.filter(job => job.type === type).length),
        backgroundColor: 'rgba(79, 70, 229, 0.5)',
        borderColor: 'rgba(79, 70, 229, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Job Distribution by Type',
      },
    },
  };

  return <Bar data={data} options={options} />;
};