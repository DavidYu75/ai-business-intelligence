/**
 * Authentication context and provider.
 *
 * Manages user state, login/logout, and token lifecycle.
 * Wraps the app to provide auth state to all components.
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from 'react';
import { useRouter } from 'next/router';
import { authApi, User } from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    fullName: string
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Pages that don't require authentication
const PUBLIC_PAGES = ['/login', '/register'];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await authApi.getMe();
          setUser(response.data);
        } catch {
          // Token invalid — clear it
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Redirect logic: protect private pages
  useEffect(() => {
    if (!isLoading) {
      const isPublicPage = PUBLIC_PAGES.includes(router.pathname);
      if (!user && !isPublicPage) {
        router.push('/login');
      }
    }
  }, [user, isLoading, router]);

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await authApi.login(email, password);
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);

      // Fetch user profile
      const userResponse = await authApi.getMe();
      setUser(userResponse.data);

      router.push('/');
    },
    [router]
  );

  const register = useCallback(
    async (email: string, password: string, fullName: string) => {
      await authApi.register({ email, password, full_name: fullName });

      // Auto-login after registration
      await login(email, password);
    },
    [login]
  );

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    router.push('/login');
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
