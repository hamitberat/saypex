import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, Smartphone, Key, Download, AlertCircle, CheckCircle, Copy } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardContent, CardTitle } from '../components/ui/card';
import { authHelpers, handleApiError } from '../services/api';

const TFASettings = () => {
  const navigate = useNavigate();
  const currentUser = authHelpers.getCurrentUser();
  const [tfaStatus, setTfaStatus] = useState(null);
  const [setupData, setSetupData] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [step, setStep] = useState('status'); // status, setup, verify, backup-codes

  // Check authentication
  if (!authHelpers.isAuthenticated() || !currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-800 mb-2">Sign In Required</h2>
              <p className="text-gray-600 mb-4">You need to be signed in to access security settings.</p>
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

  useEffect(() => {
    loadTfaStatus();
  }, []);

  const loadTfaStatus = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/2fa/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTfaStatus(data);
      } else {
        throw new Error('Failed to load 2FA status');
      }
    } catch (error) {
      console.error('Error loading 2FA status:', error);
      setError('Failed to load 2FA status');
    } finally {
      setLoading(false);
    }
  };

  const handleSetup2FA = async () => {
    try {
      setLoading(true);
      setError('');
      
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/2fa/setup`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSetupData(data);
        setStep('setup');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to setup 2FA');
      }
    } catch (error) {
      console.error('Error setting up 2FA:', error);
      setError(error.message || 'Failed to setup 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySetup = async () => {
    try {
      setLoading(true);
      setError('');
      
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/2fa/verify-setup`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: verificationCode })
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess('2FA has been enabled successfully!');
        setBackupCodes(setupData.backup_codes);
        setStep('backup-codes');
        await loadTfaStatus(); // Refresh status
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Invalid verification code');
      }
    } catch (error) {
      console.error('Error verifying 2FA:', error);
      setError(error.message || 'Failed to verify 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    const password = prompt('Enter your password to disable 2FA:');
    if (!password) return;

    try {
      setLoading(true);
      setError('');
      
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${backendUrl}/api/2fa/disable`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
      });

      if (response.ok) {
        setSuccess('2FA has been disabled successfully!');
        await loadTfaStatus(); // Refresh status
        setStep('status');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to disable 2FA');
      }
    } catch (error) {
      console.error('Error disabling 2FA:', error);
      setError(error.message || 'Failed to disable 2FA');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
    setTimeout(() => setSuccess(''), 2000);
  };

  const downloadBackupCodes = () => {
    const codesText = backupCodes.join('\n');
    const blob = new Blob([codesText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'saypex-backup-codes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading 2FA settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto p-4">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/settings')}
            className="mb-4 text-purple-600 hover:text-purple-700 hover:bg-purple-50"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Settings
          </Button>
          
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Shield className="w-8 h-8 text-purple-600" />
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Two-Factor Authentication
              </h1>
            </div>
            <p className="text-gray-600">Secure your account with an additional layer of protection</p>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="pt-4">
              <div className="flex items-center text-red-600">
                <AlertCircle className="w-4 h-4 mr-2" />
                {error}
              </div>
            </CardContent>
          </Card>
        )}

        {success && (
          <Card className="mb-6 border-green-200 bg-green-50">
            <CardContent className="pt-4">
              <div className="flex items-center text-green-600">
                <CheckCircle className="w-4 h-4 mr-2" />
                {success}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Content */}
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-gray-800">
              {step === 'status' && '2FA Status'}
              {step === 'setup' && 'Setup 2FA'}
              {step === 'verify' && 'Verify 2FA'}
              {step === 'backup-codes' && 'Backup Codes'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {step === 'status' && (
              <div className="space-y-6">
                <div className="text-center py-8">
                  <Shield className={`w-16 h-16 mx-auto mb-4 ${tfaStatus?.enabled ? 'text-green-500' : 'text-gray-400'}`} />
                  <h2 className="text-2xl font-bold text-gray-800 mb-2">
                    2FA is {tfaStatus?.enabled ? 'Enabled' : 'Disabled'}
                  </h2>
                  <p className="text-gray-600 mb-6">
                    {tfaStatus?.enabled 
                      ? 'Your account is protected with two-factor authentication'
                      : 'Enable 2FA to add an extra layer of security to your account'
                    }
                  </p>

                  {tfaStatus?.enabled ? (
                    <div className="space-y-4">
                      {tfaStatus.verified_date && (
                        <p className="text-sm text-gray-500">
                          Enabled on: {new Date(tfaStatus.verified_date).toLocaleDateString()}
                        </p>
                      )}
                      <p className="text-sm text-gray-600">
                        Backup codes remaining: {tfaStatus.backup_codes_remaining}
                      </p>
                      <div className="flex justify-center space-x-4">
                        <Button
                          variant="outline"
                          className="border-purple-200 text-purple-700 hover:bg-purple-50"
                        >
                          Generate New Backup Codes
                        </Button>
                        <Button
                          variant="outline"
                          onClick={handleDisable2FA}
                          className="border-red-200 text-red-700 hover:bg-red-50"
                        >
                          Disable 2FA
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <Button
                      onClick={handleSetup2FA}
                      className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-8"
                    >
                      Enable 2FA
                    </Button>
                  )}
                </div>

                {/* 2FA Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card className="border-blue-200 bg-blue-50">
                    <CardContent className="pt-4">
                      <Smartphone className="w-8 h-8 text-blue-600 mb-2" />
                      <h3 className="font-semibold text-gray-800 mb-2">Authenticator App</h3>
                      <p className="text-sm text-gray-600">
                        Use apps like Google Authenticator, Authy, or Microsoft Authenticator to generate time-based codes.
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="border-purple-200 bg-purple-50">
                    <CardContent className="pt-4">
                      <Key className="w-8 h-8 text-purple-600 mb-2" />
                      <h3 className="font-semibold text-gray-800 mb-2">Backup Codes</h3>
                      <p className="text-sm text-gray-600">
                        Single-use backup codes for account recovery when you can't access your authenticator app.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            {step === 'setup' && setupData && (
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-xl font-bold text-gray-800 mb-2">Scan QR Code</h2>
                  <p className="text-gray-600 mb-4">
                    Use your authenticator app to scan this QR code
                  </p>
                </div>

                <div className="flex flex-col md:flex-row gap-6">
                  <div className="flex-1 text-center">
                    <div className="inline-block p-4 bg-white rounded-lg border-2 border-gray-200">
                      <img 
                        src={setupData.qr_code_image} 
                        alt="2FA QR Code"
                        className="max-w-full h-auto"
                      />
                    </div>
                    
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-700 mb-2">Manual Entry Key:</p>
                      <div className="flex items-center justify-center space-x-2">
                        <code className="px-3 py-1 bg-white border rounded text-sm font-mono">
                          {setupData.secret}
                        </code>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(setupData.secret)}
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="flex-1">
                    <div className="space-y-4">
                      <h3 className="font-semibold text-gray-800">Instructions:</h3>
                      <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600">
                        <li>Install an authenticator app on your phone</li>
                        <li>Scan the QR code with your authenticator app</li>
                        <li>Enter the 6-digit code from your app below</li>
                        <li>Save your backup codes in a safe place</li>
                      </ol>

                      <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">Verification Code</label>
                        <Input
                          type="text"
                          value={verificationCode}
                          onChange={(e) => setVerificationCode(e.target.value)}
                          placeholder="Enter 6-digit code"
                          maxLength={6}
                          className="text-center text-lg font-mono"
                        />
                      </div>

                      <div className="flex space-x-2">
                        <Button
                          onClick={() => setStep('status')}
                          variant="outline"
                          className="flex-1"
                        >
                          Cancel
                        </Button>
                        <Button
                          onClick={handleVerifySetup}
                          disabled={verificationCode.length !== 6}
                          className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                        >
                          Verify & Enable
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 'backup-codes' && backupCodes.length > 0 && (
              <div className="space-y-6">
                <div className="text-center">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                  <h2 className="text-xl font-bold text-gray-800 mb-2">2FA Enabled Successfully!</h2>
                  <p className="text-gray-600 mb-4">
                    Save these backup codes in a safe place. You can use them to access your account if you lose your authenticator device.
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center text-yellow-800 mb-2">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    <strong>Important: Save these codes now!</strong>
                  </div>
                  <p className="text-sm text-yellow-700">
                    Each backup code can only be used once. Store them securely and don't share them with anyone.
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 p-4 bg-gray-50 rounded-lg">
                  {backupCodes.map((code, index) => (
                    <div key={index} className="font-mono text-center p-2 bg-white rounded border">
                      {code}
                    </div>
                  ))}
                </div>

                <div className="flex justify-center space-x-4">
                  <Button
                    onClick={downloadBackupCodes}
                    variant="outline"
                    className="border-purple-200 text-purple-700 hover:bg-purple-50"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Codes
                  </Button>
                  <Button
                    onClick={() => setStep('status')}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  >
                    Continue to Settings
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TFASettings;