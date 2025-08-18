import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, File, Image, Play, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardContent, CardTitle } from '../components/ui/card';
import { authHelpers, handleApiError } from '../services/api';

const Upload = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'entertainment',
    tags: ''
  });
  const [videoFile, setVideoFile] = useState(null);
  const [thumbnailFile, setThumbnailFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Check authentication
  const currentUser = authHelpers.getCurrentUser();
  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-800 mb-2">Sign In Required</h2>
              <p className="text-gray-600 mb-4">You need to be signed in to upload videos.</p>
              <Button 
                onClick={() => navigate('/login')}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              >
                Sign In
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleVideoFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (500MB limit)
      if (file.size > 500 * 1024 * 1024) {
        setError('Video file too large. Maximum size is 500MB.');
        return;
      }
      
      // Validate file type
      const allowedTypes = ['.mp4', '.avi', '.mov', '.mkv', '.webm'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      if (!allowedTypes.includes(fileExtension)) {
        setError(`Invalid video format. Supported formats: ${allowedTypes.join(', ')}`);
        return;
      }
      
      setVideoFile(file);
      setError('');
    }
  };

  const handleThumbnailFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate thumbnail file type
      const allowedTypes = ['.jpg', '.jpeg', '.png', '.webp'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      if (!allowedTypes.includes(fileExtension)) {
        setError(`Invalid thumbnail format. Supported formats: ${allowedTypes.join(', ')}`);
        return;
      }
      
      setThumbnailFile(file);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!videoFile) {
      setError('Please select a video file to upload.');
      return;
    }
    
    if (!formData.title.trim()) {
      setError('Please enter a title for your video.');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('video_file', videoFile);
      formDataToSend.append('title', formData.title);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('category', formData.category);
      formDataToSend.append('tags', formData.tags);
      
      if (thumbnailFile) {
        formDataToSend.append('thumbnail_file', thumbnailFile);
      }

      // Get backend URL from environment
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      // Simulate upload progress (since we can't track actual progress easily)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 500);

      const response = await fetch(`${backendUrl}/api/upload/video`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        const result = await response.json();
        setSuccess(`Video "${result.title}" uploaded successfully!`);
        
        // Redirect to video page after 2 seconds
        setTimeout(() => {
          navigate(`/watch?v=${result.id}`);
        }, 2000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

    } catch (error) {
      console.error('Upload error:', error);
      setError(error.message || 'Failed to upload video. Please try again.');
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-800 mb-2">Upload Successful!</h2>
              <p className="text-gray-600 mb-4">{success}</p>
              <p className="text-sm text-gray-500">Redirecting to your video...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="mb-4 text-purple-600 hover:text-purple-700 hover:bg-purple-50"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to SAYPEX
          </Button>
          
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <UploadIcon className="w-8 h-8 text-purple-600" />
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Upload Video
              </h1>
            </div>
            <p className="text-gray-600">Share your content with the SAYPEX community</p>
          </div>
        </div>

        {/* Upload Form */}
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-gray-800">Video Details</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-center">
                  <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                  {error}
                </div>
              )}

              {/* Video File Upload */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Video File *</label>
                <div className="border-2 border-dashed border-purple-200 rounded-lg p-6 hover:border-purple-300 transition-colors">
                  <div className="text-center">
                    <Play className="w-12 h-12 text-purple-400 mx-auto mb-2" />
                    <div className="space-y-2">
                      <Button
                        type="button"
                        onClick={() => document.getElementById('video-file').click()}
                        className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                      >
                        <File className="w-4 h-4 mr-2" />
                        Choose Video File
                      </Button>
                      <p className="text-sm text-gray-500">
                        Supported formats: MP4, AVI, MOV, MKV, WEBM (Max: 500MB)
                      </p>
                      {videoFile && (
                        <p className="text-sm text-purple-600 font-medium">
                          Selected: {videoFile.name}
                        </p>
                      )}
                    </div>
                  </div>
                  <input
                    id="video-file"
                    type="file"
                    accept=".mp4,.avi,.mov,.mkv,.webm"
                    onChange={handleVideoFileChange}
                    className="hidden"
                  />
                </div>
              </div>

              {/* Thumbnail Upload */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Thumbnail (Optional)</label>
                <div className="border-2 border-dashed border-purple-200 rounded-lg p-4 hover:border-purple-300 transition-colors">
                  <div className="text-center">
                    <Image className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                    <div className="space-y-2">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => document.getElementById('thumbnail-file').click()}
                        className="border-purple-200 text-purple-700 hover:bg-purple-50"
                      >
                        Choose Thumbnail
                      </Button>
                      <p className="text-xs text-gray-500">
                        JPG, PNG, WEBP
                      </p>
                      {thumbnailFile && (
                        <p className="text-xs text-purple-600 font-medium">
                          Selected: {thumbnailFile.name}
                        </p>
                      )}
                    </div>
                  </div>
                  <input
                    id="thumbnail-file"
                    type="file"
                    accept=".jpg,.jpeg,.png,.webp"
                    onChange={handleThumbnailFileChange}
                    className="hidden"
                  />
                </div>
              </div>

              {/* Video Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2 space-y-2">
                  <label className="text-sm font-medium text-gray-700">Title *</label>
                  <Input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="Enter video title"
                    maxLength={200}
                    className="h-12 border-purple-200 focus:border-purple-400 focus:ring-purple-200"
                    required
                  />
                </div>

                <div className="md:col-span-2 space-y-2">
                  <label className="text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    placeholder="Tell viewers about your video"
                    maxLength={5000}
                    rows={4}
                    className="w-full px-3 py-2 border border-purple-200 rounded-md focus:border-purple-400 focus:ring-1 focus:ring-purple-200 resize-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Category</label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    className="w-full h-12 px-3 border border-purple-200 rounded-md focus:border-purple-400 focus:ring-1 focus:ring-purple-200"
                  >
                    <option value="entertainment">Entertainment</option>
                    <option value="education">Education</option>
                    <option value="gaming">Gaming</option>
                    <option value="music">Music</option>
                    <option value="news">News</option>
                    <option value="sports">Sports</option>
                    <option value="technology">Technology</option>
                    <option value="lifestyle">Lifestyle</option>
                    <option value="cooking">Cooking</option>
                    <option value="travel">Travel</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Tags</label>
                  <Input
                    type="text"
                    name="tags"
                    value={formData.tags}
                    onChange={handleInputChange}
                    placeholder="gaming, tutorial, fun (comma-separated)"
                    className="h-12 border-purple-200 focus:border-purple-400 focus:ring-purple-200"
                  />
                </div>
              </div>

              {/* Upload Progress */}
              {uploading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Uploading...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={uploading || !videoFile}
                className="w-full h-12 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-lg transition-all duration-200"
              >
                {uploading ? (
                  <>
                    <UploadIcon className="w-4 h-4 mr-2 animate-spin" />
                    Uploading Video...
                  </>
                ) : (
                  <>
                    <UploadIcon className="w-4 h-4 mr-2" />
                    Upload Video
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Upload;