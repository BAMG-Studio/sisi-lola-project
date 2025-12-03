import { create } from 'zustand';

interface User {
  id: number;
  email: string;
  roles: string[];
}

interface AuthStore {
  user: User | null;
  setUser: (user: User | null) => void;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  setUser: (user) => set({ user }),
  hasPermission: (permission) => {
    const user = get().user;
    if (!user) return false;
    if (user.roles.includes('SUPER_ADMIN')) return true;
    return false; // Simplified - expand based on role permissions
  },
  hasRole: (role) => {
    const user = get().user;
    return user?.roles.includes(role) || user?.roles.includes('SUPER_ADMIN') || false;
  }
}));
