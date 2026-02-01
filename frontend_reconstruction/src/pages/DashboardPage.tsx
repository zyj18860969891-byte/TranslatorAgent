import React from 'react';
import { Dashboard } from '../components/Dashboard';

interface DashboardPageProps {
  results?: any[];
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ results }) => {
  return <Dashboard results={results} />;
};