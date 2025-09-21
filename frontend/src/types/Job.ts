export interface Job {
  id: number;           // Corresponds to backend id (Long)
  title: string;        
  company: string;      
  location: string;     
  source: string;       
  url?: string;         
  description?: string; 
  isFavorite?: boolean; // Whether favorited by current user
  matchScore?: number;  // Match score (only for resume recommendation results)
}
