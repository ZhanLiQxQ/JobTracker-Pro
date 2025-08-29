import {Job} from "../../types/job.types";
interface JobDetailProps {
  job: Job;
  onFavorite?: (jobId: number) => void;
  showFavoriteButton?: boolean;
}

export const JobDetail = ({ job, onFavorite, showFavoriteButton = false }: JobDetailProps) => {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">{job.title}</h1>
          <p className="text-xl text-gray-600 mb-1">{job.company}</p>
          <p className="text-gray-500">{job.location}</p>
        </div>
        {showFavoriteButton && onFavorite && (
          <button
            onClick={() => onFavorite(job.id)}
            className="text-yellow-500 hover:text-yellow-600"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </button>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">职位描述</h2>
          <p className="text-gray-700 whitespace-pre-line">{job.description}</p>
        </div>

        {job.requirements && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">职位要求</h2>
            <p className="text-gray-700 whitespace-pre-line">{job.requirements}</p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-lg font-semibold mb-2">职位信息</h3>
            <ul className="space-y-2">
              <li className="flex items-center">
                <span className="text-gray-500 w-24">状态：</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  {job.status}
                </span>
              </li>
              {job.salary && (
                <li className="flex items-center">
                  <span className="text-gray-500 w-24">薪资：</span>
                  <span>{job.salary}</span>
                </li>
              )}
              <li className="flex items-center">
                <span className="text-gray-500 w-24">来源：</span>
                <span>{job.source}</span>
              </li>
              <li className="flex items-center">
                <span className="text-gray-500 w-24">发布时间：</span>
                <span>{new Date(job.postedAt).toLocaleDateString()}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};