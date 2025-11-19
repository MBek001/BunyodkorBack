import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import api from '@/services/api';

export default function ParentPayment() {
  const [contractNumber, setContractNumber] = useState('');
  const [paymentInfo, setPaymentInfo] = useState<any>(null);
  const [error, setError] = useState('');

  const checkPaymentMutation = useMutation({
    mutationFn: async (contractNum: string) => {
      const response = await api.post('/api/payments/parent/info', {
        contract_number: contractNum,
      });
      return response.data;
    },
    onSuccess: (data) => {
      setPaymentInfo(data);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Contract not found');
      setPaymentInfo(null);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (contractNumber.trim()) {
      checkPaymentMutation.mutate(contractNumber.trim());
    }
  };

  const handlePayment = (method: 'payme' | 'click') => {
    // TODO: Integrate with Payme/Click payment gateways
    alert(`Redirecting to ${method.toUpperCase()} payment gateway...`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-500 to-blue-600 px-4 py-12">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Bunyodkor CIMS</h1>
          <p className="text-white text-opacity-90">Parent Payment Portal</p>
          <Link to="/login" className="text-sm text-white hover:underline mt-2 inline-block">
            ← Back to Login
          </Link>
        </div>

        {/* Contract Number Form */}
        <div className="bg-white rounded-xl shadow-2xl p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Check Payment Information</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="contract" className="block text-sm font-medium text-gray-700 mb-2">
                Enter Contract Number
              </label>
              <input
                id="contract"
                type="text"
                value={contractNumber}
                onChange={(e) => setContractNumber(e.target.value)}
                placeholder="e.g., 2024000123"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={checkPaymentMutation.isPending}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {checkPaymentMutation.isPending ? 'Checking...' : 'Check Payment Info'}
            </button>
          </form>
        </div>

        {/* Payment Information */}
        {paymentInfo && (
          <div className="bg-white rounded-xl shadow-2xl p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Payment Information</h3>

            <div className="space-y-4 mb-6">
              <div className="flex justify-between py-3 border-b">
                <span className="text-gray-600">Student Name</span>
                <span className="font-semibold text-gray-900">{paymentInfo.student_name}</span>
              </div>

              {paymentInfo.group_name && (
                <div className="flex justify-between py-3 border-b">
                  <span className="text-gray-600">Group</span>
                  <span className="font-semibold text-gray-900">{paymentInfo.group_name}</span>
                </div>
              )}

              <div className="flex justify-between py-3 border-b">
                <span className="text-gray-600">Monthly Fee</span>
                <span className="font-semibold text-gray-900">
                  {paymentInfo.monthly_fee.toLocaleString()} UZS
                </span>
              </div>

              {paymentInfo.discount_percentage > 0 && (
                <div className="flex justify-between py-3 border-b">
                  <span className="text-gray-600">Discount</span>
                  <span className="font-semibold text-green-600">
                    -{paymentInfo.discount_percentage}%
                  </span>
                </div>
              )}

              <div className="flex justify-between py-4 bg-blue-50 rounded-lg px-4">
                <span className="text-lg font-semibold text-gray-900">Amount to Pay</span>
                <span className="text-2xl font-bold text-blue-600">
                  {paymentInfo.final_fee.toLocaleString()} UZS
                </span>
              </div>
            </div>

            {/* Payment Methods */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Choose Payment Method</h4>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => handlePayment('payme')}
                  className="bg-gradient-to-r from-blue-500 to-blue-600 text-white py-4 rounded-lg font-semibold hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg"
                >
                  <span className="text-2xl">💳</span>
                  <p className="mt-1">Payme</p>
                </button>

                <button
                  onClick={() => handlePayment('click')}
                  className="bg-gradient-to-r from-purple-500 to-purple-600 text-white py-4 rounded-lg font-semibold hover:from-purple-600 hover:to-purple-700 transition-all shadow-lg"
                >
                  <span className="text-2xl">💰</span>
                  <p className="mt-1">Click</p>
                </button>
              </div>
            </div>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-600 text-center">
                After successful payment, your student's account will be automatically updated.
                Payment will be reflected in the system within a few minutes.
              </p>
            </div>
          </div>
        )}

        {/* Information Box */}
        <div className="mt-6 bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-6 text-white">
          <h4 className="font-semibold mb-2">Need Help?</h4>
          <p className="text-sm text-white text-opacity-90">
            If you don't have your contract number, please contact the academy administration.
            For payment issues, you can also make cash payments at the academy office.
          </p>
        </div>
      </div>
    </div>
  );
}
