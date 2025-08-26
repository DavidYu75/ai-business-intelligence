import React from 'react';
import Head from 'next/head';

export default function Home() {
  return (
    <>
      <Head>
        <title>Real-Time Business Intelligence Platform</title>
        <meta name="description" content="Real-Time BI Platform for natural language query processing" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Real-Time Business Intelligence Platform
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Transform your data with natural language queries and real-time visualizations
            </p>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 max-w-2xl mx-auto">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                🚀 Development Environment Ready!
              </h2>
              <p className="text-gray-600 mb-4">
                Your Real-Time BI Platform development environment is now running successfully.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-green-800">✅ Backend API</h3>
                  <p className="text-green-600 text-sm">Running on port 8000</p>
                  <a 
                    href="http://localhost:8000/docs" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-green-700 hover:text-green-800 underline text-sm"
                  >
                    View API Docs
                  </a>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-blue-800">✅ Frontend</h3>
                  <p className="text-blue-600 text-sm">Running on port 3000</p>
                  <a 
                    href="http://localhost:3000" 
                    className="text-blue-700 hover:text-blue-800 underline text-sm"
                  >
                    View Application
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
