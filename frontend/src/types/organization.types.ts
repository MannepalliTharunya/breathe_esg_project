export interface Organization {
  id: string;
  name: string;
  legal_name: string;
  industry: string;
  country: string;
  website: string;
  logo: string | null;
  description: string;
  employee_count: number | null;
  annual_revenue: number | null;
  fiscal_year_end: string;
  reporting_currency: string;
  is_active: boolean;
  subscription_tier: "starter" | "professional" | "enterprise";
  member_count: number;
  created_at: string;
}

export interface Facility {
  id: string;
  organization: string;
  name: string;
  facility_type: string;
  address_line1: string;
  city: string;
  country: string;
  is_active: boolean;
}

export interface Membership {
  id: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string;
    avatar: string | null;
    job_title: string;
    is_active: boolean;
    created_at: string;
  };
  role: string;
  is_active: boolean;
  joined_at: string;
}

export interface PaginatedResponse<T> {
  pagination: {
    count: number;
    total_pages: number;
    current_page: number;
    next: string | null;
    previous: string | null;
  };
  results: T[];
}
