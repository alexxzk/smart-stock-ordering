import React, { useState } from 'react';

interface SalesDeductionRule {
  id: string;
  name: string;
  percentage: number;
  active: boolean;
  description: string;
}

const SalesAutoDeduction = () => {
  const [rules, setRules] = useState<SalesDeductionRule[]>([
    {
      id: '1',
      name: 'Daily Sales Deduction',
      percentage: 5,
      active: true,
      description: 'Automatically deduct 5% from daily sales for operational costs'
    },
    {
      id: '2',
      name: 'Weekend Sales Deduction',
      percentage: 3,
      active: false,
      description: 'Deduct 3% from weekend sales for additional processing'
    }
  ]);

  const [newRule, setNewRule] = useState({
    name: '',
    percentage: 0,
    description: ''
  });

  const handleToggleRule = (id: string) => {
    setRules(prevRules => 
      prevRules.map(rule => 
        rule.id === id ? { ...rule, active: !rule.active } : rule
      )
    );
  };

  const handleAddRule = () => {
    if (newRule.name && newRule.percentage > 0) {
      const rule: SalesDeductionRule = {
        id: Date.now().toString(),
        name: newRule.name,
        percentage: newRule.percentage,
        active: false,
        description: newRule.description
      };
      setRules(prevRules => [...prevRules, rule]);
      setNewRule({ name: '', percentage: 0, description: '' });
    }
  };

  const handleDeleteRule = (id: string) => {
    setRules(prevRules => prevRules.filter(rule => rule.id !== id));
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Sales Auto Deduction</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Active Rules</h2>
          <div className="space-y-4">
            {rules.map((rule) => (
              <div key={rule.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-800">{rule.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{rule.description}</p>
                    <div className="mt-2">
                      <span className="text-sm font-medium text-blue-600">
                        {rule.percentage}% deduction
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToggleRule(rule.id)}
                      className={`px-3 py-1 text-xs rounded-full ${
                        rule.active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {rule.active ? 'Active' : 'Inactive'}
                    </button>
                    <button
                      onClick={() => handleDeleteRule(rule.id)}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Add New Rule</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rule Name
              </label>
              <input
                type="text"
                value={newRule.name}
                onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter rule name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Deduction Percentage
              </label>
              <input
                type="number"
                value={newRule.percentage}
                onChange={(e) => setNewRule({ ...newRule, percentage: parseFloat(e.target.value) || 0 })}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter percentage"
                min="0"
                max="100"
                step="0.1"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={newRule.description}
                onChange={(e) => setNewRule({ ...newRule, description: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter rule description"
                rows={3}
              />
            </div>

            <button
              onClick={handleAddRule}
              className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Add Rule
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Deduction Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium text-blue-800">Total Active Rules</h3>
            <p className="text-2xl font-bold text-blue-600 mt-2">
              {rules.filter(rule => rule.active).length}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-medium text-green-800">Total Deduction Rate</h3>
            <p className="text-2xl font-bold text-green-600 mt-2">
              {rules.filter(rule => rule.active).reduce((sum, rule) => sum + rule.percentage, 0)}%
            </p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h3 className="font-medium text-yellow-800">Inactive Rules</h3>
            <p className="text-2xl font-bold text-yellow-600 mt-2">
              {rules.filter(rule => !rule.active).length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SalesAutoDeduction;