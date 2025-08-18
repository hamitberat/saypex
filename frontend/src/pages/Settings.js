import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, User, Shield, Bell, Eye, Globe, Video, Lock, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardContent, CardTitle } from '../components/ui/card';
import { authHelpers } from '../services/api';

const Settings = () => {
  const navigate = useNavigate();
  const currentUser = authHelpers.getCurrentUser();
  const [activeTab, setActiveTab] = useState('profile');

  // Check authentication
  if (!authHelpers.isAuthenticated() || !currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-800 mb-2">Sign In Required</h2>
              <p className="text-gray-600 mb-4">You need to be signed in to access settings.</p>
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

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'privacy', name: 'Privacy', icon: Eye },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'channel', name: 'Channel', icon: Video },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      <div className="max-w-6xl mx-auto p-4">
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
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
              Account Settings
            </h1>
            <p className="text-gray-600">Manage your SAYPEX account and preferences</p>
          </div>
        </div>

        {/* Settings Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardContent className="p-4">
                <nav className="space-y-2">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                        activeTab === tab.id
                          ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                          : 'text-gray-700 hover:bg-purple-50'
                      }`}
                    >
                      <tab.icon className="w-4 h-4" />
                      <span className="font-medium">{tab.name}</span>
                    </button>
                  ))}
                </nav>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-gray-800 flex items-center">
                  {(() => {
                    const activeTabData = tabs.find(tab => tab.id === activeTab);
                    const IconComponent = activeTabData?.icon;
                    return IconComponent ? <IconComponent className="w-5 h-5 mr-2" /> : null;
                  })()}
                  {tabs.find(tab => tab.id === activeTab)?.name} Settings
                </CardTitle>
              </CardHeader>
              <CardContent>
                {activeTab === 'profile' && <ProfileSettings currentUser={currentUser} />}
                {activeTab === 'security' && <SecuritySettings currentUser={currentUser} />}
                {activeTab === 'privacy' && <PrivacySettings />}
                {activeTab === 'notifications' && <NotificationSettings />}
                {activeTab === 'channel' && <ChannelSettings currentUser={currentUser} />}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Profile Settings Component
const ProfileSettings = ({ currentUser }) => {
  const [formData, setFormData] = useState({
    username: currentUser?.username || '',
    full_name: currentUser?.full_name || '',
    email: currentUser?.email || '',
    bio: currentUser?.bio || '',
    country: currentUser?.country || '',
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = async () => {
    // TODO: Implement profile update API call
    console.log('Save profile:', formData);
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Username</label>
          <Input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            placeholder="Your username"
            className="h-12 border-purple-200 focus:border-purple-400"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Full Name</label>
          <Input
            type="text"
            name="full_name"
            value={formData.full_name}
            onChange={handleInputChange}
            placeholder="Your full name"
            className="h-12 border-purple-200 focus:border-purple-400"
          />
        </div>

        <div className="md:col-span-2 space-y-2">
          <label className="text-sm font-medium text-gray-700">Email</label>
          <Input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            placeholder="Your email address"
            className="h-12 border-purple-200 focus:border-purple-400"
          />
        </div>

        <div className="md:col-span-2 space-y-2">
          <label className="text-sm font-medium text-gray-700">Bio</label>
          <textarea
            name="bio"
            value={formData.bio}
            onChange={handleInputChange}
            placeholder="Tell viewers about yourself"
            rows={3}
            className="w-full px-3 py-2 border border-purple-200 rounded-md focus:border-purple-400 focus:ring-1 focus:ring-purple-200"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Country</label>
          <select
            name="country"
            value={formData.country}
            onChange={handleInputChange}
            className="w-full h-12 px-3 border border-purple-200 rounded-md focus:border-purple-400"
          >
            <option value="">Select Country</option>
            <option value="US">United States</option>
            <option value="GB">United Kingdom</option>
            <option value="CA">Canada</option>
            <option value="AU">Australia</option>
            <option value="DE">Germany</option>
            <option value="FR">France</option>
            <option value="IT">Italy</option>
            <option value="ES">Spain</option>
            <option value="NL">Netherlands</option>
            <option value="SE">Sweden</option>
            <option value="NO">Norway</option>
            <option value="DK">Denmark</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-6"
        >
          Save Changes
        </Button>
      </div>
    </div>
  );
};

// Security Settings Component
const SecuritySettings = ({ currentUser }) => {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-800 flex items-center">
                <Lock className="w-4 h-4 mr-2 text-blue-600" />
                Two-Factor Authentication (2FA)
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Add an extra layer of security to your account with 2FA
              </p>
            </div>
            <Link to="/settings/2fa">
              <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                Manage 2FA
              </Button>
            </Link>
          </div>
        </div>

        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-800">Change Password</h3>
              <p className="text-sm text-gray-600 mt-1">
                Update your account password regularly for better security
              </p>
            </div>
            <Button 
              variant="outline"
              className="border-yellow-300 text-yellow-700 hover:bg-yellow-100"
            >
              Change Password
            </Button>
          </div>
        </div>

        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-800 flex items-center">
                <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                OAuth Connections
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Connect with Google or Facebook for easy sign-in
              </p>
            </div>
            <Button 
              variant="outline"
              className="border-green-300 text-green-700 hover:bg-green-100"
            >
              Manage Connections
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Privacy Settings Component
const PrivacySettings = () => {
  const [settings, setSettings] = useState({
    show_subscriptions: true,
    show_playlists: true,
    show_liked_videos: false,
    allow_comments: true,
    allow_messages: true,
  });

  const handleToggle = (key) => {
    setSettings({
      ...settings,
      [key]: !settings[key]
    });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {Object.entries({
          show_subscriptions: 'Show my subscriptions publicly',
          show_playlists: 'Show my playlists publicly', 
          show_liked_videos: 'Show videos I liked publicly',
          allow_comments: 'Allow others to comment on my videos',
          allow_messages: 'Allow others to send me messages',
        }).map(([key, label]) => (
          <div key={key} className="flex items-center justify-between py-2">
            <span className="text-gray-700">{label}</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings[key]}
                onChange={() => handleToggle(key)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-purple-600 peer-checked:to-blue-600"></div>
            </label>
          </div>
        ))}
      </div>

      <div className="flex justify-end">
        <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-6">
          Save Privacy Settings
        </Button>
      </div>
    </div>
  );
};

// Notification Settings Component
const NotificationSettings = () => {
  const [settings, setSettings] = useState({
    email_notifications: true,
    push_notifications: true,
    comment_notifications: true,
    upload_notifications: true,
    like_notifications: false,
  });

  const handleToggle = (key) => {
    setSettings({
      ...settings,
      [key]: !settings[key]
    });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {Object.entries({
          email_notifications: 'Email notifications',
          push_notifications: 'Push notifications',
          comment_notifications: 'New comment notifications',
          upload_notifications: 'New upload from subscriptions',
          like_notifications: 'Like and reaction notifications',
        }).map(([key, label]) => (
          <div key={key} className="flex items-center justify-between py-2">
            <span className="text-gray-700">{label}</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings[key]}
                onChange={() => handleToggle(key)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-purple-600 peer-checked:to-blue-600"></div>
            </label>
          </div>
        ))}
      </div>

      <div className="flex justify-end">
        <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-6">
          Save Notification Settings
        </Button>
      </div>
    </div>
  );
};

// Channel Settings Component
const ChannelSettings = ({ currentUser }) => {
  const [formData, setFormData] = useState({
    channel_name: currentUser?.channel_name || '',
    channel_description: '',
    channel_keywords: '',
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Channel Name</label>
          <Input
            type="text"
            name="channel_name"
            value={formData.channel_name}
            onChange={handleInputChange}
            placeholder="Your channel name"
            className="h-12 border-purple-200 focus:border-purple-400"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Channel Description</label>
          <textarea
            name="channel_description"
            value={formData.channel_description}
            onChange={handleInputChange}
            placeholder="Describe your channel and content"
            rows={4}
            className="w-full px-3 py-2 border border-purple-200 rounded-md focus:border-purple-400 focus:ring-1 focus:ring-purple-200"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Channel Keywords</label>
          <Input
            type="text"
            name="channel_keywords"
            value={formData.channel_keywords}
            onChange={handleInputChange}
            placeholder="gaming, education, entertainment (comma-separated)"
            className="h-12 border-purple-200 focus:border-purple-400"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-6">
          Save Channel Settings
        </Button>
      </div>
    </div>
  );
};

export default Settings;