import {Job} from "../../types/job.types";
interface JobListProps {
  jobs: Job[];
  onFavorite?: (jobId: number) => void;
  showFavoriteButton?: boolean;
}

export const JobList = ({ jobs, onFavorite, showFavoriteButton = false }: JobListProps) => {
  if (jobs.length === 0) {
    return <div className="text-center text-gray-500">暂无职位</div>;
  }

  return (
    <div className="space-y-4">
      {jobs.map((job) => (
        <div key={job.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-semibold">{job.title}</h3>
              <p className="text-gray-600">{job.company}</p>
              <p className="text-sm text-gray-500">{job.location}</p>
            </div>
            {showFavoriteButton && onFavorite && (
              <button
                onClick={() => onFavorite(job.id)}
                className="text-yellow-500 hover:text-yellow-600"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </button>
            )}
          </div>
          <div className="mt-2">
            <p className="text-sm text-gray-600">{job.description}</p>
          </div>
          <div className="mt-2 flex gap-2">
            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
              {job.status}
            </span>
            {job.salary && (
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                {job.salary}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};