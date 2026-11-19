import { useQuery } from '@tanstack/react-query';
import { apiGet } from '../api/client.ts';
import type { AdminDashboard, StudentDashboard, TeacherDashboard } from '../api/types.ts';

/** Tableros por rol (`/dashboard/*`, §7.10). Una consulta agregada por tablero. */

export const dashboardKeys = {
  student: ['dashboard', 'student'] as const,
  teacher: ['dashboard', 'teacher'] as const,
  admin: ['dashboard', 'admin'] as const,
};

export function useStudentDashboard(enabled = true) {
  return useQuery({
    queryKey: dashboardKeys.student,
    queryFn: () => apiGet<StudentDashboard>('/dashboard/student'),
    enabled,
  });
}

export function useTeacherDashboard() {
  return useQuery({
    queryKey: dashboardKeys.teacher,
    queryFn: () => apiGet<TeacherDashboard>('/dashboard/teacher'),
  });
}

export function useAdminDashboard() {
  return useQuery({
    queryKey: dashboardKeys.admin,
    queryFn: () => apiGet<AdminDashboard>('/dashboard/admin'),
  });
}
