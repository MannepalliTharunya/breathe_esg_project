import apiClient from "./client";
import type { Organization, Facility, Membership, PaginatedResponse } from "@/types/organization.types";

export const organizationsService = {
  getOrganizations: () =>
    apiClient.get<PaginatedResponse<Organization>>("/organizations/").then((r) => r.data),

  getOrganization: (id: string) =>
    apiClient.get<Organization>(`/organizations/${id}/`).then((r) => r.data),

  createOrganization: (data: Partial<Organization>) =>
    apiClient.post<Organization>("/organizations/", data).then((r) => r.data),

  updateOrganization: (id: string, data: Partial<Organization>) =>
    apiClient.patch<Organization>(`/organizations/${id}/`, data).then((r) => r.data),

  // Facilities
  getFacilities: (orgId: string) =>
    apiClient.get<PaginatedResponse<Facility>>(`/organizations/${orgId}/facilities/`).then((r) => r.data),

  createFacility: (orgId: string, data: Partial<Facility>) =>
    apiClient.post<Facility>(`/organizations/${orgId}/facilities/`, data).then((r) => r.data),

  updateFacility: (orgId: string, facilityId: string, data: Partial<Facility>) =>
    apiClient.patch<Facility>(`/organizations/${orgId}/facilities/${facilityId}/`, data).then((r) => r.data),

  // Departments
  getDepartments: (orgId: string) =>
    apiClient.get<PaginatedResponse<any>>(`/organizations/${orgId}/departments/`).then((r) => r.data),

  createDepartment: (orgId: string, data: any) =>
    apiClient.post<any>(`/organizations/${orgId}/departments/`, data).then((r) => r.data),

  // Members
  getMembers: (orgId: string) =>
    apiClient.get<PaginatedResponse<Membership>>(`/organizations/${orgId}/members/`).then((r) => r.data),

  inviteMember: (orgId: string, userId: string, role: string) =>
    apiClient.post<Membership>(`/organizations/${orgId}/members/`, { user_id: userId, role }).then((r) => r.data),

  updateMemberRole: (orgId: string, memberId: string, role: string) =>
    apiClient.patch<Membership>(`/organizations/${orgId}/members/${memberId}/`, { role }).then((r) => r.data),

  removeMember: (orgId: string, memberId: string) =>
    apiClient.delete(`/organizations/${orgId}/members/${memberId}/`),
};
