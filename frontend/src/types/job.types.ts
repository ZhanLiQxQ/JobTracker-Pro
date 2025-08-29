export type JobStatus = 'APPLIED' | 'INTERVIEW' | 'REJECTED';

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  status: JobStatus;
  description: string;
  requirements?: string;
  salary?: string;
  source: string;
  postedAt: string;
  isFavorite: boolean;
}

export interface JobFormValues {
  title: string;
  company: string;
  location: string;
  description: string;
  requirements?: string;
  salary?: string;
  source: string;
  status: JobStatus;
}