import React, { useState, useRef } from 'react';
import { Job } from '../types/Job';
import { jobService } from '../services/jobService';
import { authService } from '../services/authService';
import JobCard from './JobCard';

interface ResumeUploadProps {
  onFavoriteChange?: () => void;
}

const ResumeUpload: React.FC<ResumeUploadProps> = ({ onFavoriteChange }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [recommendedJobs, setRecommendedJobs] = useState<Job[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    // Check file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload resume in PDF or Word document format');
      return;
    }

    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size cannot exceed 10MB');
      return;
    }

    setSelectedFile(file);
    setError(null);
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }
// Note: If it's pure testing, you can temporarily comment out authService check
    // if (!authService.isAuthenticated()) ...

    setUploading(true);
    setError(null);
    setRecommendedJobs([]);

    try {
      // 1. Phase 1: Quickly get list (call Python /recommend_file)
      // aiReason in returned jobs are all null
      const { jobs, resumeText } = await jobService.uploadResumeToAI(selectedFile);

      // Immediately render list, user sees job cards and "Loading..." animation
      setRecommendedJobs(jobs);
      setUploading(false); // Stop overall Loading

      // 2. Phase 2: Lazy load AI explanations
      // Iterate through all jobs and initiate requests
      jobs.forEach(async (job) => {
        try {
          // Call Python /rag/explain_job
          const reason = await jobService.getAIExplanation(
            job.description || "",
            resumeText
          );

          // 3. Phase 3: Update individual Job state
          // Use functional update to ensure getting latest state in closure
          setRecommendedJobs(prevJobs =>
            prevJobs.map(j =>
              j.id === job.id ? { ...j, aiReason: reason } : j
            )
          );
        } catch (e) {
          console.error(`Failed to fetch AI reason for job ${job.id}`, e);
        }
      });

    } catch (err) {
      setUploading(false);
      setError('Upload failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setRecommendedJobs([]);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Resume Matching Recommendations</h2>
        <p className="text-gray-600 mb-6">
          Upload your resume (PDF or Word format), and we will recommend the most matching job opportunities for you
        </p>

        {/* File upload area */}
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : selectedFile
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <svg className="w-12 h-12 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
              </div>
              <div className="flex justify-center space-x-4">
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {uploading ? 'Analyzing...' : 'Start Matching'}
                </button>
                <button
                  onClick={handleRemoveFile}
                  disabled={uploading}
                  className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Reselect
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">Drag files here or click to select</p>
                <p className="text-sm text-gray-500">Supports PDF, Word format, max 10MB</p>
              </div>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Select File
              </button>
            </div>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileInputChange}
          className="hidden"
        />

        {/* Error message */}
        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Upload progress */}
        {uploading && (
          <div className="mt-4 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-600">Analyzing your resume, please wait...</p>
          </div>
        )}
      </div>

      {/* Recommendation results */}
      {recommendedJobs.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Recommended Jobs for You ({recommendedJobs.length} jobs)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendedJobs.map((job, index) => (
              <JobCard
                key={`${job.id}-${index}`}
                job={job}
                onFavoriteChange={onFavoriteChange}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!uploading && recommendedJobs.length === 0 && !error && selectedFile && (
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <p className="text-gray-600">No matching jobs found. Please try uploading a different resume or adjusting search criteria</p>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
