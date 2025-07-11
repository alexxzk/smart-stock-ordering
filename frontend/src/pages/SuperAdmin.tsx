import React from 'react';

const SuperAdmin = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Super Admin</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">System Overview</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Users:</span>
              <span className="font-medium">-</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Active Sessions:</span>
              <span className="font-medium">-</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">System Status:</span>
              <span className="font-medium text-green-600">Active</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">User Management</h2>
          <div className="space-y-2">
            <button className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600">
              View All Users
            </button>
            <button className="w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600">
              Add New User
            </button>
            <button className="w-full bg-yellow-500 text-white py-2 px-4 rounded hover:bg-yellow-600">
              User Permissions
            </button>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">System Settings</h2>
          <div className="space-y-2">
            <button className="w-full bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600">
              Configuration
            </button>
            <button className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600">
              System Logs
            </button>
            <button className="w-full bg-purple-500 text-white py-2 px-4 rounded hover:bg-purple-600">
              Database Admin
            </button>
          </div>
        </div>
      </div>

      <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Recent Activity</h2>
        <div className="text-gray-600">
          <p>No recent activity to display.</p>
        </div>
      </div>
    </div>
  );
};

export default SuperAdmin;