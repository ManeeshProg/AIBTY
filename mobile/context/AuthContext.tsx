import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authApi, getToken, setToken, removeToken } from '@/lib/api';

interface User {
  id: string;
  email: string;
  full_name: string | null;
  preferences: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await getToken();
      if (token) {
        const userData = await authApi.getMe();
        setUser(userData);
      }
    } catch (error) {
      // Token invalid or expired
      await removeToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    await setToken(response.access_token);
    const userData = await authApi.getMe();
    setUser(userData);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    await authApi.register(email, password, fullName);
    // Auto-login after registration
    await login(email, password);
  };

  const logout = async () => {
    await removeToken();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (error) {
      await logout();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
