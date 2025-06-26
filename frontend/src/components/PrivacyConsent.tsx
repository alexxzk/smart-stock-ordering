import React, { useState, useEffect } from 'react';
import { doc, setDoc, getDoc, updateDoc } from 'firebase/firestore';
import { auth, db } from '../config/firebase';
import { useAuth } from '../hooks/useAuth';

interface PrivacySettings {
  marketing: boolean;
  analytics: boolean;
  personalization: boolean;
  thirdParty: boolean;
  dataRetention: '30days' | '90days' | '1year' | 'indefinite';
  dataExport: boolean;
  dataDeletion: boolean;
}

const PrivacyConsent: React.FC = () => {
  const { user } = useAuth();
  const [showConsent, setShowConsent] = useState(false);
  const [settings, setSettings] = useState<PrivacySettings>({
    marketing: false,
    analytics: false,
    personalization: false,
    thirdParty: false,
    dataRetention: '90days',
    dataExport: false,
    dataDeletion: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user) {
      checkPrivacyConsent();
    }
  }, [user]);

  const checkPrivacyConsent = async () => {
    if (!user) return;
    
    try {
      const consentDoc = await getDoc(doc(db, 'privacy_consent', user.uid));
      if (!consentDoc.exists()) {
        setShowConsent(true);
      } else {
        const data = consentDoc.data();
        setSettings(data.settings || settings);
      }
    } catch (error) {
      console.error('Error checking privacy consent:', error);
      setShowConsent(true);
    }
  };

  const saveConsent = async () => {
    if (!user) return;
    
    setIsLoading(true);
    setMessage('');
    
    try {
      await setDoc(doc(db, 'privacy_consent', user.uid), {
        userId: user.uid,
        settings,
        timestamp: new Date(),
        version: '1.0',
        ipAddress: 'captured-on-server',
        userAgent: navigator.userAgent
      });
      
      setShowConsent(false);
      setMessage('Privacy preferences saved successfully!');
      
      // Apply consent settings
      applyPrivacySettings();
      
    } catch (error) {
      console.error('Error saving privacy consent:', error);
      setMessage('Error saving privacy preferences. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const applyPrivacySettings = () => {
    // Disable analytics if not consented
    if (!settings.analytics) {
      // Disable Google Analytics
      if (window.gtag) {
        window.gtag('config', 'GA_MEASUREMENT_ID', {
          'send_page_view': false
        });
      }
    }
    
    // Disable marketing cookies if not consented
    if (!settings.marketing) {
      // Clear marketing cookies
      document.cookie.split(";").forEach((c) => {
        const eqPos = c.indexOf("=");
        const name = eqPos > -1 ? c.substr(0, eqPos) : c;
        if (name.includes('marketing') || name.includes('ad')) {
          document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
        }
      });
    }
  };

  const exportUserData = async () => {
    if (!user) return;
    
    setIsLoading(true);
    setMessage('');
    
    try {
      // Request data export from backend
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/users/export-data`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await user.getIdToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `user-data-${user.uid}-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        setMessage('Data export completed!');
      } else {
        setMessage('Error exporting data. Please try again.');
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      setMessage('Error exporting data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const requestDataDeletion = async () => {
    if (!user) return;
    
    if (!confirm('Are you sure you want to request data deletion? This action cannot be undone.')) {
      return;
    }
    
    setIsLoading(true);
    setMessage('');
    
    try {
      await setDoc(doc(db, 'data_deletion_requests', user.uid), {
        userId: user.uid,
        requestDate: new Date(),
        status: 'pending',
        reason: 'user_request',
        dataTypes: ['profile', 'sales', 'inventory', 'orders', 'analytics']
      });
      
      setMessage('Data deletion request submitted. We will process it within 30 days.');
    } catch (error) {
      console.error('Error requesting data deletion:', error);
      setMessage('Error submitting deletion request. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!showConsent) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setShowConsent(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
        >
          Privacy Settings
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-4">Privacy & Data Consent</h2>
          <p className="text-gray-600 mb-6">
            We respect your privacy and are committed to protecting your personal data. 
            Please review and customize your privacy settings below.
          </p>

          <div className="space-y-4">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">Data Collection & Usage</h3>
              
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.analytics}
                    onChange={(e) => setSettings({...settings, analytics: e.target.checked})}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-medium">Analytics & Performance</div>
                    <div className="text-sm text-gray-500">
                      Help us improve our service by collecting usage analytics
                    </div>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.personalization}
                    onChange={(e) => setSettings({...settings, personalization: e.target.checked})}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-medium">Personalization</div>
                    <div className="text-sm text-gray-500">
                      Provide personalized recommendations and features
                    </div>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.marketing}
                    onChange={(e) => setSettings({...settings, marketing: e.target.checked})}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-medium">Marketing Communications</div>
                    <div className="text-sm text-gray-500">
                      Receive updates about new features and promotions
                    </div>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.thirdParty}
                    onChange={(e) => setSettings({...settings, thirdParty: e.target.checked})}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-medium">Third-Party Services</div>
                    <div className="text-sm text-gray-500">
                      Allow data sharing with trusted third-party services
                    </div>
                  </div>
                </label>
              </div>
            </div>

            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">Data Retention</h3>
              <select
                value={settings.dataRetention}
                onChange={(e) => setSettings({...settings, dataRetention: e.target.value as any})}
                className="w-full p-2 border rounded"
              >
                <option value="30days">30 days</option>
                <option value="90days">90 days</option>
                <option value="1year">1 year</option>
                <option value="indefinite">Until account deletion</option>
              </select>
            </div>

            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">Data Rights</h3>
              <div className="space-y-3">
                <button
                  onClick={exportUserData}
                  disabled={isLoading}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
                >
                  Export My Data
                </button>
                
                <button
                  onClick={requestDataDeletion}
                  disabled={isLoading}
                  className="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 disabled:opacity-50"
                >
                  Request Data Deletion
                </button>
              </div>
            </div>
          </div>

          {message && (
            <div className={`mt-4 p-3 rounded ${message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
              {message}
            </div>
          )}

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={() => setShowConsent(false)}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={saveConsent}
              disabled={isLoading}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyConsent; 