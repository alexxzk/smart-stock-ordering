import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { db } from '../config/firebase';
import { collection, doc, setDoc, getDoc, updateDoc } from 'firebase/firestore';

interface IntegrationSettings {
  gmail: {
    enabled: boolean;
    clientId: string;
    clientSecret: string;
    refreshToken: string;
    email: string;
  };
  notifications: {
    email: boolean;
    browser: boolean;
    lowStock: boolean;
    orderUpdates: boolean;
    forecastAlerts: boolean;
  };
  slack: {
    enabled: boolean;
    webhookUrl: string;
    channel: string;
  };
  sms: {
    enabled: boolean;
    provider: 'twilio' | 'aws-sns';
    apiKey: string;
    phoneNumber: string;
  };
}

const Integrations = () => {
  const { currentUser } = useAuth();
  const [settings, setSettings] = useState<IntegrationSettings>({
    gmail: {
      enabled: false,
      clientId: '',
      clientSecret: '',
      refreshToken: '',
      email: ''
    },
    notifications: {
      email: true,
      browser: true,
      lowStock: true,
      orderUpdates: true,
      forecastAlerts: false
    },
    slack: {
      enabled: false,
      webhookUrl: '',
      channel: '#general'
    },
    sms: {
      enabled: false,
      provider: 'twilio',
      apiKey: '',
      phoneNumber: ''
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [gmailAuthUrl, setGmailAuthUrl] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    if (!currentUser) return;
    
    try {
      const settingsRef = doc(db, 'users', currentUser.uid, 'settings', 'integrations');
      const settingsDoc = await getDoc(settingsRef);
      
      if (settingsDoc.exists()) {
        setSettings(settingsDoc.data() as IntegrationSettings);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const saveSettings = async () => {
    if (!currentUser) return;
    
    setIsLoading(true);
    setMessage('');
    
    try {
      const settingsRef = doc(db, 'users', currentUser.uid, 'settings', 'integrations');
      await setDoc(settingsRef, settings);
      setMessage('✅ Settings saved successfully!');
    } catch (error) {
      setMessage('❌ Error saving settings: ' + error);
    } finally {
      setIsLoading(false);
    }
  };

  const testGmailConnection = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:8000/api/integrations/test-gmail', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          clientId: settings.gmail.clientId,
          clientSecret: settings.gmail.clientSecret,
          refreshToken: settings.gmail.refreshToken
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setMessage('✅ Gmail connection successful!');
      } else {
        setMessage('❌ Gmail connection failed: ' + result.detail);
      }
    } catch (error) {
      setMessage('❌ Error testing Gmail connection: ' + error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendTestEmail = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:8000/api/integrations/send-test-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to: settings.gmail.email,
          subject: 'Test Email from Smart Stock Ordering',
          body: 'This is a test email to verify your Gmail integration is working correctly.'
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setMessage('✅ Test email sent successfully!');
      } else {
        setMessage('❌ Failed to send test email: ' + result.detail);
      }
    } catch (error) {
      setMessage('❌ Error sending test email: ' + error);
    } finally {
      setIsLoading(false);
    }
  };

  const testSlackConnection = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:8000/api/integrations/test-slack', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          webhookUrl: settings.slack.webhookUrl,
          channel: settings.slack.channel
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setMessage('✅ Slack connection successful!');
      } else {
        setMessage('❌ Slack connection failed: ' + result.detail);
      }
    } catch (error) {
      setMessage('❌ Error testing Slack connection: ' + error);
    } finally {
      setIsLoading(false);
    }
  };

  const testSMSConnection = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:8000/api/integrations/test-sms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: settings.sms.provider,
          apiKey: settings.sms.apiKey,
          phoneNumber: settings.sms.phoneNumber
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setMessage('✅ SMS connection successful!');
      } else {
        setMessage('❌ SMS connection failed: ' + result.detail);
      }
    } catch (error) {
      setMessage('❌ Error testing SMS connection: ' + error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateSetting = (section: keyof IntegrationSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Integrations</h1>
          
          {message && (
            <div className={`mb-6 p-4 rounded-lg ${
              message.includes('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {message}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Gmail Integration */}
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Gmail Integration</h2>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.gmail.enabled}
                    onChange={(e) => updateSetting('gmail', 'enabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              {settings.gmail.enabled && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Client ID
                    </label>
                    <input
                      type="text"
                      value={settings.gmail.clientId}
                      onChange={(e) => updateSetting('gmail', 'clientId', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Gmail OAuth Client ID"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Client Secret
                    </label>
                    <input
                      type="password"
                      value={settings.gmail.clientSecret}
                      onChange={(e) => updateSetting('gmail', 'clientSecret', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Gmail OAuth Client Secret"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Refresh Token
                    </label>
                    <input
                      type="password"
                      value={settings.gmail.refreshToken}
                      onChange={(e) => updateSetting('gmail', 'refreshToken', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Gmail Refresh Token"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={settings.gmail.email}
                      onChange={(e) => updateSetting('gmail', 'email', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="your-email@gmail.com"
                    />
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={testGmailConnection}
                      disabled={isLoading}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Test Connection
                    </button>
                    <button
                      onClick={sendTestEmail}
                      disabled={isLoading}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Send Test Email
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Notifications */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Notification Settings</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Email Notifications</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications.email}
                      onChange={(e) => updateSetting('notifications', 'email', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Browser Notifications</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications.browser}
                      onChange={(e) => updateSetting('notifications', 'browser', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Low Stock Alerts</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications.lowStock}
                      onChange={(e) => updateSetting('notifications', 'lowStock', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Order Updates</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications.orderUpdates}
                      onChange={(e) => updateSetting('notifications', 'orderUpdates', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Forecast Alerts</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications.forecastAlerts}
                      onChange={(e) => updateSetting('notifications', 'forecastAlerts', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            </div>

            {/* Slack Integration */}
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Slack Integration</h2>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.slack.enabled}
                    onChange={(e) => updateSetting('slack', 'enabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              {settings.slack.enabled && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Webhook URL
                    </label>
                    <input
                      type="url"
                      value={settings.slack.webhookUrl}
                      onChange={(e) => updateSetting('slack', 'webhookUrl', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://hooks.slack.com/services/..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Channel
                    </label>
                    <input
                      type="text"
                      value={settings.slack.channel}
                      onChange={(e) => updateSetting('slack', 'channel', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="#general"
                    />
                  </div>
                  
                  <button
                    onClick={testSlackConnection}
                    disabled={isLoading}
                    className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Test Connection
                  </button>
                </div>
              )}
            </div>

            {/* SMS Integration */}
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">SMS Integration</h2>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.sms.enabled}
                    onChange={(e) => updateSetting('sms', 'enabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              {settings.sms.enabled && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Provider
                    </label>
                    <select
                      value={settings.sms.provider}
                      onChange={(e) => updateSetting('sms', 'provider', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="twilio">Twilio</option>
                      <option value="aws-sns">AWS SNS</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      API Key
                    </label>
                    <input
                      type="password"
                      value={settings.sms.apiKey}
                      onChange={(e) => updateSetting('sms', 'apiKey', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="API Key"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={settings.sms.phoneNumber}
                      onChange={(e) => updateSetting('sms', 'phoneNumber', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="+1234567890"
                    />
                  </div>
                  
                  <button
                    onClick={testSMSConnection}
                    disabled={isLoading}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Test Connection
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="mt-8 flex justify-end">
            <button
              onClick={saveSettings}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-2 rounded-md font-medium"
            >
              {isLoading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Integrations; 