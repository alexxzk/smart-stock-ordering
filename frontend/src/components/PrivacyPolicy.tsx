import React from 'react';

const PrivacyPolicy: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
      
      <div className="space-y-6 text-gray-700">
        <section>
          <h2 className="text-xl font-semibold mb-3">1. Information We Collect</h2>
          <div className="space-y-2">
            <h3 className="font-medium">Personal Information:</h3>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Name, email address, and phone number</li>
              <li>Business information and preferences</li>
              <li>Payment and billing information</li>
              <li>Usage data and analytics</li>
            </ul>
            
            <h3 className="font-medium mt-3">Business Data:</h3>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Sales history and transaction data</li>
              <li>Inventory levels and stock movements</li>
              <li>Supplier information and order history</li>
              <li>Forecasting models and predictions</li>
            </ul>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">2. How We Use Your Information</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>Provide and maintain our smart stock ordering service</li>
            <li>Generate sales forecasts and inventory predictions</li>
            <li>Create AI-powered ordering recommendations</li>
            <li>Process supplier orders and manage relationships</li>
            <li>Improve our services and develop new features</li>
            <li>Send important updates and notifications</li>
            <li>Ensure security and prevent fraud</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">3. Data Sharing and Third Parties</h2>
          <p className="mb-2">We do not sell, trade, or rent your personal information to third parties. We may share data with:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Service providers who assist in operating our platform</li>
            <li>Suppliers when processing orders (only necessary information)</li>
            <li>Legal authorities when required by law</li>
            <li>Business partners with your explicit consent</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">4. Data Security</h2>
          <p className="mb-2">We implement industry-standard security measures to protect your data:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>End-to-end encryption for data transmission</li>
            <li>Secure cloud storage with Firebase</li>
            <li>Regular security audits and updates</li>
            <li>Access controls and authentication</li>
            <li>Data backup and disaster recovery</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">5. Your Rights (GDPR/CCPA)</h2>
          <p className="mb-2">You have the following rights regarding your personal data:</p>
          <ul className="list-disc list-inside space-y-1">
            <li><strong>Access:</strong> Request a copy of your personal data</li>
            <li><strong>Rectification:</strong> Correct inaccurate or incomplete data</li>
            <li><strong>Erasure:</strong> Request deletion of your personal data</li>
            <li><strong>Portability:</strong> Receive your data in a structured format</li>
            <li><strong>Restriction:</strong> Limit how we process your data</li>
            <li><strong>Objection:</strong> Object to certain types of processing</li>
            <li><strong>Withdrawal:</strong> Withdraw consent at any time</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">6. Data Retention</h2>
          <p className="mb-2">We retain your data for as long as necessary to:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Provide our services to you</li>
            <li>Comply with legal obligations</li>
            <li>Resolve disputes and enforce agreements</li>
            <li>Improve our services</li>
          </ul>
          <p className="mt-2">You can choose your data retention period in your privacy settings.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">7. Cookies and Tracking</h2>
          <p className="mb-2">We use cookies and similar technologies to:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Remember your preferences and settings</li>
            <li>Analyze website usage and performance</li>
            <li>Provide personalized content and features</li>
            <li>Ensure security and prevent fraud</li>
          </ul>
          <p className="mt-2">You can control cookie settings in your browser or privacy preferences.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">8. International Data Transfers</h2>
          <p>Your data may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place to protect your data in accordance with applicable laws.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">9. Children's Privacy</h2>
          <p>Our service is not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">10. Changes to This Policy</h2>
          <p>We may update this privacy policy from time to time. We will notify you of any material changes by email or through our service.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">11. Contact Us</h2>
          <p className="mb-2">If you have questions about this privacy policy or want to exercise your rights, contact us:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Email: privacy@smartstockordering.com</li>
            <li>Phone: +1 (555) 123-4567</li>
            <li>Address: 123 Business St, City, State 12345</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">12. Data Protection Officer</h2>
          <p>For EU residents, you can contact our Data Protection Officer at dpo@smartstockordering.com</p>
        </section>
      </div>

      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <strong>Last updated:</strong> {new Date().toLocaleDateString()}
        </p>
      </div>
    </div>
  );
};

export default PrivacyPolicy; 