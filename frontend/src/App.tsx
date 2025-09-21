import React, { useState, useEffect } from 'react';
import { Job } from './types/Job';
import { jobService } from './services/jobService';
import { authService } from './services/authService';
import { User, AuthState, LoginRequest, RegisterRequest } from './types/Auth';
import SearchForm from './components/SearchForm';
import JobCard from './components/JobCard';
import LoginModal from './components/LoginModal';
import FavoritesPage from './components/FavoritesPage';
import ResumeUpload from './components/ResumeUpload';
import './index.css';

function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState<'home' | 'favorites' | 'resume'>('home');

  useEffect(() => {
    // Check if user is already logged in
    const userInfo = authService.getUser();
    if (userInfo) {
      setUser(userInfo);
    }
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const jobsData = await jobService.getAllJobs();
      setJobs(jobsData);
      setError(null);
    } catch (err) {
      setError('Failed to load jobs: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (title: string, company: string, location: string) => {
    try {
      setLoading(true);
      const jobsData = await jobService.getAllJobs(title, company, location);
      setJobs(jobsData);
      setError(null);
    } catch (err) {
      setError('Search failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (credentials: LoginRequest) => {
    try {
      await authService.login(credentials);
      setUser(authService.getUser());
      setShowLoginModal(false);
      // Reload job list to get favorite status
      loadJobs();
    } catch (err) {
      alert('Login failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleRegister = async (credentials: RegisterRequest) => {
    try {
      await authService.register(credentials);
      // Auto login after successful registration
      await handleLogin(credentials);
    } catch (err) {
      alert('Registration failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    // Reload job list to clear favorite status
    loadJobs();
  };

  const handleFavoriteChange = () => {
    // Reload job list when favorite status changes
    loadJobs();
  };

  const navigateToHome = () => {
    setCurrentPage('home');
  };

  const navigateToFavorites = () => {
    setCurrentPage('favorites');
  };

  const navigateToResume = () => {
    setCurrentPage('resume');
  };

  // Render resume upload page
  if (currentPage === 'resume') {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Navigation bar */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">JobTracker Pro</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={navigateToHome}
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Home
                </button>
                {user ? (
                  <>
                    <button
                      onClick={navigateToFavorites}
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      My Favorites
                    </button>
                    <button
                      onClick={navigateToResume}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                    >
                      Resume Match
                    </button>
                    <span className="text-gray-700 text-sm">{user.email}</span>
                    <button
                      onClick={handleLogout}
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setShowLoginModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    Login/Register
                  </button>
                )}
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <ResumeUpload onFavoriteChange={handleFavoriteChange} />
        </div>
      </div>
    );
  }

  // Render favorites page
  if (currentPage === 'favorites') {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Navigation bar */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">JobTracker Pro</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={navigateToHome}
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Home
                </button>
                {user ? (
                  <>
                    <button
                      onClick={navigateToFavorites}
                      className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                    >
                      My Favorites
                    </button>
                    <button
                      onClick={navigateToResume}
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Resume Match
                    </button>
                    <span className="text-gray-700 text-sm">{user.email}</span>
                    <button
                      onClick={handleLogout}
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setShowLoginModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    Login/Register
                  </button>
                )}
              </div>
            </div>
          </div>
        </nav>

        <FavoritesPage />
      </div>
    );
  }

  // Render main page
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation bar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">JobTracker Pro</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={navigateToHome}
                className="bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Home
              </button>
              {user ? (
                <>
                  <button
                    onClick={navigateToFavorites}
                    className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    My Favorites
                  </button>
                  <button
                    onClick={navigateToResume}
                    className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Resume Match
                  </button>
                  <span className="text-gray-700 text-sm">{user.email}</span>
                  <button
                    onClick={handleLogout}
                    className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setShowLoginModal(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  Login/Register
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

        {/* Main content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search form */}
        <SearchForm onSearch={handleSearch} />

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading...</p>
          </div>
        )}

        {/* Job list */}
        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onFavoriteChange={handleFavoriteChange}
              />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && jobs.length === 0 && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600">Try adjusting search criteria</p>
          </div>
        )}
      </div>

      {/* Login modal */}
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onLogin={handleLogin}
        onRegister={handleRegister}
      />
    </div>
  );
}

export default App;

