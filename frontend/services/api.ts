import {
  UserProfile, Employee, HierarchyNode, ReviewCycle, Goal, KeyResult,
  GoalHistory, CheckIn, Feedback, Review, Competency, DevelopmentPlan,
  Anomaly, AuditEvent, DashboardKPIs
} from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api';

class ApiService {
  private token: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('yotta_token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('yotta_token', token);
      } else {
        localStorage.removeItem('yotta_token');
      }
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('yotta_token');
    }
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    const token = this.getToken();
    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch (e) {
        // Fallback
      }
      throw new Error(errorMsg);
    }

    return response.json();
  }

  // Auth
  async login(username: string, password: string): Promise<any> {
    const res = await this.request<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    if (res.access_token) {
      this.setToken(res.access_token);
    }
    return res;
  }

  async getMe(): Promise<UserProfile> {
    return this.request<UserProfile>('/auth/me');
  }

  async getCurrentUser(): Promise<UserProfile> {
    return this.getMe();
  }

  // Employees & Organization
  async getEmployees(params?: { department?: string; search?: string; limit?: number }): Promise<Employee[]> {
    const query = new URLSearchParams();
    if (params?.department) query.set('department', params.department);
    if (params?.search) query.set('search', params.search);
    if (params?.limit) query.set('limit', params.limit.toString());
    return this.request<Employee[]>(`/employees?${query.toString()}`);
  }

  async getOrganizationHierarchy(rootId?: string): Promise<HierarchyNode[]> {
    const query = rootId ? `?root_id=${encodeURIComponent(rootId)}` : '';
    return this.request<HierarchyNode[]>(`/organization/hierarchy${query}`);
  }

  async transferManager(employeeId: string, newManagerId: string | null, reason?: string): Promise<Employee> {
    return this.request<Employee>(`/organization/transfer/${employeeId}`, {
      method: 'POST',
      body: JSON.stringify({ new_manager_id: newManagerId, reason })
    });
  }

  // Review Cycles
  async getReviewCycles(): Promise<ReviewCycle[]> {
    return this.request<ReviewCycle[]>('/review-cycles');
  }

  async updateCycleStage(cycleId: string, stage: string, reason?: string): Promise<ReviewCycle> {
    return this.request<ReviewCycle>(`/review-cycles/${cycleId}/stage`, {
      method: 'PUT',
      body: JSON.stringify({ stage, reason })
    });
  }

  // Goals & Key Results
  async getGoals(params?: { employee_id?: string; review_cycle_id?: string; status?: string; limit?: number }): Promise<Goal[]> {
    const query = new URLSearchParams();
    if (params?.employee_id) query.set('employee_id', params.employee_id);
    if (params?.review_cycle_id) query.set('review_cycle_id', params.review_cycle_id);
    if (params?.status) query.set('status', params.status);
    if (params?.limit) query.set('limit', params.limit.toString());
    return this.request<Goal[]>(`/goals?${query.toString()}`);
  }

  async createGoal(payload: Partial<Goal> & { is_admin_correction?: boolean; correction_reason?: string }): Promise<Goal> {
    return this.request<Goal>('/goals', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async getGoalHistory(goalId: string): Promise<GoalHistory[]> {
    return this.request<GoalHistory[]>(`/goals/${goalId}/history`);
  }

  async addKeyResult(goalId: string, payload: Partial<KeyResult>): Promise<KeyResult> {
    return this.request<KeyResult>(`/goals/${goalId}/key-results`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async updateKeyResultValue(keyResultId: string, currentValue: number): Promise<KeyResult> {
    return this.request<KeyResult>(`/key-results/${keyResultId}`, {
      method: 'PUT',
      body: JSON.stringify({ current_value: currentValue })
    });
  }

  // Check-ins
  async getCheckIns(params?: { employee_id?: string; goal_id?: string; review_cycle_id?: string; limit?: number }): Promise<CheckIn[]> {
    const query = new URLSearchParams();
    if (params?.employee_id) query.set('employee_id', params.employee_id);
    if (params?.goal_id) query.set('goal_id', params.goal_id);
    if (params?.review_cycle_id) query.set('review_cycle_id', params.review_cycle_id);
    if (params?.limit) query.set('limit', params.limit.toString());
    return this.request<CheckIn[]>(`/check-ins?${query.toString()}`);
  }

  async submitCheckIn(payload: Partial<CheckIn> & { evidence_reference_url?: string; evidence_type?: string; evidence_description?: string }): Promise<CheckIn> {
    return this.request<CheckIn>('/check-ins', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Competencies & Feedback
  async getCompetencies(): Promise<Competency[]> {
    return this.request<Competency[]>('/competencies');
  }

  async getFeedback(params?: { subject_employee_id?: string; review_cycle_id?: string; limit?: number }): Promise<Feedback[]> {
    const query = new URLSearchParams();
    if (params?.subject_employee_id) query.set('subject_employee_id', params.subject_employee_id);
    if (params?.review_cycle_id) query.set('review_cycle_id', params.review_cycle_id);
    if (params?.limit) query.set('limit', params.limit.toString());
    return this.request<Feedback[]>(`/feedback?${query.toString()}`);
  }

  async submitFeedback(payload: Partial<Feedback>): Promise<Feedback> {
    return this.request<Feedback>('/feedback', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Reviews
  async getReviews(params?: { review_cycle_id?: string; stage?: string; limit?: number }): Promise<Review[]> {
    const query = new URLSearchParams();
    if (params?.review_cycle_id) query.set('review_cycle_id', params.review_cycle_id);
    if (params?.stage) query.set('stage', params.stage);
    if (params?.limit) query.set('limit', params.limit.toString());
    return this.request<Review[]>(`/reviews?${query.toString()}`);
  }

  async transitionReview(reviewId: string, targetStage: string, comments?: string): Promise<Review> {
    return this.request<Review>(`/reviews/${reviewId}/transition`, {
      method: 'POST',
      body: JSON.stringify({ target_stage: targetStage, comments })
    });
  }

  // Development Plans
  async getDevelopmentPlans(params?: { employee_id?: string; status?: string; limit?: number }): Promise<DevelopmentPlan[]> {
    const query = new URLSearchParams();
    if (params?.employee_id) query.set('employee_id', params.employee_id);
    if (params?.status) query.set('status', params.status);
    if (params?.limit) query.set('limit', params.limit.toString());
    return this.request<DevelopmentPlan[]>(`/development-plans?${query.toString()}`);
  }

  async createDevelopmentPlan(payload: Partial<DevelopmentPlan>): Promise<DevelopmentPlan> {
    return this.request<DevelopmentPlan>('/development-plans', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async approveDevelopmentPlan(planId: string, decision: string, comments?: string): Promise<DevelopmentPlan> {
    return this.request<DevelopmentPlan>(`/development-plans/${planId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ decision, comments })
    });
  }

  // Anomalies
  async getAnomalies(params?: { detection_status?: string; issue_type?: string }): Promise<Anomaly[]> {
    const query = new URLSearchParams();
    if (params?.detection_status) query.set('detection_status', params.detection_status);
    if (params?.issue_type) query.set('issue_type', params.issue_type);
    return this.request<Anomaly[]>(`/anomalies?${query.toString()}`);
  }

  async resolveAnomaly(anomalyId: string, resolutionNotes: string): Promise<Anomaly> {
    return this.request<Anomaly>(`/anomalies/${anomalyId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution_status: 'RESOLVED', resolution_notes: resolutionNotes })
    });
  }

  // Analytics
  async getDashboardKPIs(params?: { department?: string; review_cycle_id?: string }): Promise<DashboardKPIs> {
    const query = new URLSearchParams();
    if (params?.department) query.set('department', params.department);
    if (params?.review_cycle_id) query.set('review_cycle_id', params.review_cycle_id);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<DashboardKPIs>(`/analytics/dashboard${qs}`);
  }

  async getGoalAnalytics(params?: { department?: string; review_cycle_id?: string }): Promise<any[]> {
    const query = new URLSearchParams();
    if (params?.department) query.set('department', params.department);
    if (params?.review_cycle_id) query.set('review_cycle_id', params.review_cycle_id);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<any[]>(`/analytics/goals${qs}`);
  }

  async getReviewAnalytics(params?: { department?: string; review_cycle_id?: string }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.department) query.set('department', params.department);
    if (params?.review_cycle_id) query.set('review_cycle_id', params.review_cycle_id);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<any>(`/analytics/reviews${qs}`);
  }

  async getCompetencyAnalytics(params?: { department?: string; review_cycle_id?: string }): Promise<any[]> {
    const query = new URLSearchParams();
    if (params?.department) query.set('department', params.department);
    if (params?.review_cycle_id) query.set('review_cycle_id', params.review_cycle_id);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<any[]>(`/analytics/competencies${qs}`);
  }

  async getAnomalyAnalytics(): Promise<any> {
    return this.request<any>('/analytics/anomalies');
  }

  async getEmployeePerformanceProfile(employeeId: string): Promise<any> {
    return this.request<any>(`/employees/${employeeId}/performance-profile`);
  }

  // Audit
  async getAuditEvents(): Promise<AuditEvent[]> {
    return this.request<AuditEvent[]>('/audit-events?limit=50');
  }

  // Admin
  async generateData(mode: 'starter' | 'full', seed: number = 20261022): Promise<any> {
    return this.request<any>('/admin/generate-data', {
      method: 'POST',
      body: JSON.stringify({ mode, seed, load_into_db: true })
    });
  }

  async validateData(datasetDir?: string): Promise<any> {
    const query = datasetDir ? `?dataset_dir=${encodeURIComponent(datasetDir)}` : '';
    return this.request<any>(`/admin/validate-data${query}`, {
      method: 'POST'
    });
  }
}

export const api = new ApiService();
