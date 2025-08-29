// 认证请求类型
export interface AuthRequest {
  email: string;
  password: string;
}

// 认证响应类型
export interface AuthResponse {
  jwt: string;
  id: string;
  email: string;
  roles: string[];
}

// 表单字段类型
export interface LoginFormFields {
  email: string;
  password: string;
}

export interface RegisterFormFields extends LoginFormFields {
  confirmPassword?: string;
}

// Hook 返回类型
export interface UseAuthReturnType {
  signIn: (credentials: LoginFormFields) => Promise<void>;
  signUp: (credentials: RegisterFormFields) => Promise<void>;
  error: string | null;
  loading: boolean;
}