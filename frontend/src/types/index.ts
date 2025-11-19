export interface User {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  role: 'admin' | 'superuser' | 'teacher' | 'student';
  is_active: boolean;
  created_at: string;
}

export interface Student {
  id: number;
  user_id?: number;
  first_name: string;
  last_name: string;
  middle_name?: string;
  date_of_birth: string;
  phone_number?: string;
  parent_phone: string;
  parent_name?: string;
  address?: string;
  photo_url?: string;
  enrollment_year: number;
  group_id?: number;
  is_active: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Group {
  id: number;
  name: string;
  description?: string;
  teacher_id?: number;
  schedule?: string;
  max_students: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Contract {
  id: number;
  contract_number: string;
  student_id: number;
  monthly_fee: number;
  discount_percentage: number;
  discount_amount: number;
  final_monthly_fee: number;
  status: 'active' | 'inactive' | 'suspended' | 'completed';
  start_date: string;
  end_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: number;
  student_id: number;
  contract_id: number;
  amount: number;
  payment_method: 'cash' | 'payme' | 'click';
  payment_status: 'pending' | 'completed' | 'failed' | 'refunded';
  transaction_id?: string;
  payment_date: string;
  month: number;
  year: number;
  notes?: string;
  created_by?: number;
  created_at: string;
}

export interface ErrorPayment {
  id: number;
  contract_number: string;
  amount: number;
  payment_method: 'cash' | 'payme' | 'click';
  transaction_id?: string;
  error_reason: string;
  is_resolved: boolean;
  resolved_student_id?: number;
  resolved_by?: number;
  resolved_at?: string;
  created_at: string;
}

export interface Session {
  id: number;
  group_id: number;
  session_date: string;
  start_time: string;
  end_time: string;
  is_completed: boolean;
  notes?: string;
  created_at: string;
}

export interface Attendance {
  id: number;
  session_id: number;
  student_id: number;
  status: 'present' | 'absent' | 'late' | 'excused';
  entered_building: boolean;
  notes?: string;
  marked_by?: number;
  marked_at: string;
}

export interface TurnstileLog {
  id: number;
  student_id: number;
  turnstile_id?: string;
  entry_time: string;
  exit_time?: string;
  access_granted: boolean;
  payment_verified: boolean;
  face_match_confidence?: number;
  notes?: string;
}

export interface DashboardStats {
  students: {
    total: number;
    active: number;
    inactive: number;
  };
  revenue: {
    today: number;
    monthly: number;
    yearly: number;
  };
  debtors: number;
  groups: {
    total: number;
    active: number;
  };
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}
