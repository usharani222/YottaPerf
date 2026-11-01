'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar, TabType } from '../components/Sidebar';
import { DashboardView } from '../components/views/DashboardView';
import { EmployeesView } from '../components/views/EmployeesView';
import { OrganizationView } from '../components/views/OrganizationView';
import { GoalsView } from '../components/views/GoalsView';
import { CheckInsView } from '../components/views/CheckInsView';
import { FeedbackView } from '../components/views/FeedbackView';
import { ReviewsView } from '../components/views/ReviewsView';
import { CompetenciesView } from '../components/views/CompetenciesView';
import { DevelopmentPlansView } from '../components/views/DevelopmentPlansView';
import { AnomalyCenterView } from '../components/views/AnomalyCenterView';
import { AnalyticsView } from '../components/views/AnalyticsView';
import { AuditLogsView } from '../components/views/AuditLogsView';
import AdminView from '../components/views/AdminView';

import { api } from '../services/api';
import {
  Employee,
  ReviewCycle,
  Goal,
  CheckIn,
  Feedback,
  Review,
  Competency,
  DevelopmentPlan,
  Anomaly,
  AuditEvent,
  HierarchyNode,
  DashboardKPIs,
  UserProfile
} from '../types';

export default function Home() {
  const [currentTab, setCurrentTab] = useState<TabType>('dashboard');
  const [loading, setLoading] = useState<boolean>(true);

  // Core Data Entities
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [cycles, setCycles] = useState<ReviewCycle[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [checkIns, setCheckIns] = useState<CheckIn[]>([]);
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [competencies, setCompetencies] = useState<Competency[]>([]);
  const [developmentPlans, setDevelopmentPlans] = useState<DevelopmentPlan[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [hierarchy, setHierarchy] = useState<HierarchyNode[]>([]);

  // Analytics Data
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [goalStats, setGoalStats] = useState<any[]>([]);
  const [reviewStats, setReviewStats] = useState<any>(null);
  const [competencyStats, setCompetencyStats] = useState<any[]>([]);
  const [anomalyStats, setAnomalyStats] = useState<any>(null);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      // Auto-authenticate as default admin persona if no token exists
      if (!api.getToken()) {
        try {
          await api.login('eleanor.vance', 'Password123!');
        } catch (authErr) {
          console.warn('Initial persona auto-login note:', authErr);
        }
      }

      // 1. Current User
      try {
        const u = await api.getCurrentUser();
        setCurrentUser(u);
      } catch {
        // Fallback demo user
        setCurrentUser({
          user_id: 'USR-000001',
          employee_id: 'EMP-000001',
          username: 'eleanor.vance',
          email: 'eleanor.vance@yottaperf.internal',
          full_name: 'Eleanor Vance',
          job_title: 'Chief Executive Officer',
          department: 'Executive',
          roles: ['ADMIN', 'MANAGER']
        });
      }

      // 2. Fetch parallel entities with safe fallback handling
      const [
        kpisRes,
        empsRes,
        cyclesRes,
        goalsRes,
        checkInsRes,
        fbRes,
        revRes,
        compRes,
        devRes,
        anoRes,
        auditRes,
        hierRes,
        goalStatsRes,
        revStatsRes,
        compStatsRes,
        anoStatsRes
      ] = await Promise.allSettled([
        api.getDashboardKPIs(),
        api.getEmployees({ limit: 200 }),
        api.getReviewCycles(),
        api.getGoals({ limit: 100 }),
        api.getCheckIns({ limit: 100 }),
        api.getFeedback({ limit: 100 }),
        api.getReviews({ limit: 100 }),
        api.getCompetencies(),
        api.getDevelopmentPlans(),
        api.getAnomalies(),
        api.getAuditEvents(),
        api.getOrganizationHierarchy(),
        api.getGoalAnalytics(),
        api.getReviewAnalytics(),
        api.getCompetencyAnalytics(),
        api.getAnomalyAnalytics()
      ]);

      if (kpisRes.status === 'fulfilled') setKpis(kpisRes.value);
      if (empsRes.status === 'fulfilled') setEmployees(empsRes.value);
      if (cyclesRes.status === 'fulfilled') setCycles(cyclesRes.value);
      if (goalsRes.status === 'fulfilled') setGoals(goalsRes.value);
      if (checkInsRes.status === 'fulfilled') setCheckIns(checkInsRes.value);
      if (fbRes.status === 'fulfilled') setFeedbacks(fbRes.value);
      if (revRes.status === 'fulfilled') setReviews(revRes.value);
      if (compRes.status === 'fulfilled') setCompetencies(compRes.value);
      if (devRes.status === 'fulfilled') setDevelopmentPlans(devRes.value);
      if (anoRes.status === 'fulfilled') setAnomalies(anoRes.value);
      if (auditRes.status === 'fulfilled') setAuditEvents(auditRes.value);
      if (hierRes.status === 'fulfilled') setHierarchy(hierRes.value);

      if (goalStatsRes.status === 'fulfilled') setGoalStats(goalStatsRes.value);
      if (revStatsRes.status === 'fulfilled') setReviewStats(revStatsRes.value);
      if (compStatsRes.status === 'fulfilled') setCompetencyStats(compStatsRes.value);
      if (anoStatsRes.status === 'fulfilled') setAnomalyStats(anoStatsRes.value);

    } catch (err) {
      console.error('Failed to load initial dataset:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const openAnomaliesCount = anomalies.filter(a => a.detection_status === 'OPEN').length;
  const activeCycle = cycles.find(c => c.stage === 'OPEN' || c.stage === 'ACTIVE');
  const activeCycleName = activeCycle ? `${activeCycle.cycle_id} (${activeCycle.cycle_name})` : 'CYCLE-2026-H1';

  return (
    <div className="relative min-h-screen bg-[#030712] text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Ambient background glow orbs */}
      <div className="pointer-events-none fixed top-0 left-1/4 h-[550px] w-[550px] rounded-full bg-emerald-500/5 blur-[130px]" />
      <div className="pointer-events-none fixed bottom-0 right-1/4 h-[550px] w-[550px] rounded-full bg-cyan-500/5 blur-[130px]" />

      <Navbar
        currentUser={currentUser}
        activeCycleName={activeCycleName}
        onRefresh={fetchAllData}
        onSwitchUser={(user) => {
          setCurrentUser(user);
          fetchAllData();
        }}
      />

      <div className="flex flex-1 overflow-hidden relative z-10">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          openAnomalyCount={openAnomaliesCount}
          currentUser={currentUser}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-transparent">
          {currentTab === 'dashboard' && (
            <DashboardView
              kpis={kpis}
              goalStats={goalStats}
              reviewStats={reviewStats}
              cycles={cycles}
              onNavigate={setCurrentTab}
              onRefresh={fetchAllData}
              loading={loading}
            />
          )}

          {currentTab === 'employees' && (
            <EmployeesView
              employees={employees}
              loading={loading}
            />
          )}

          {currentTab === 'organization' && (
            <OrganizationView
              hierarchy={hierarchy}
              employees={employees}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'goals' && (
            <GoalsView
              goals={goals}
              employees={employees}
              cycles={cycles}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'checkins' && (
            <CheckInsView
              checkIns={checkIns}
              goals={goals}
              employees={employees}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'feedback' && (
            <FeedbackView
              feedbacks={feedbacks}
              employees={employees}
              competencies={competencies}
              cycles={cycles}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'reviews' && (
            <ReviewsView
              reviews={reviews}
              cycles={cycles}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'competencies' && (
            <CompetenciesView
              competencies={competencies}
            />
          )}

          {currentTab === 'development' && (
            <DevelopmentPlansView
              plans={developmentPlans}
              employees={employees}
              competencies={competencies}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'anomalies' && (
            <AnomalyCenterView
              anomalies={anomalies}
              onRefresh={fetchAllData}
            />
          )}

          {currentTab === 'analytics' && (
            <AnalyticsView
              goalStats={goalStats}
              reviewStats={reviewStats}
              competencyStats={competencyStats}
              anomalyStats={anomalyStats}
              developmentPlans={developmentPlans}
              cycles={cycles}
            />
          )}

          {currentTab === 'audit' && (
            <AuditLogsView
              auditEvents={auditEvents}
            />
          )}

          {currentTab === 'admin' && (
            <AdminView />
          )}
        </main>
      </div>
    </div>
  );
}
