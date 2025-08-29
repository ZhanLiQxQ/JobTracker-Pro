import { useForm } from 'react-hook-form';
import { useAuth } from "../../hooks/useAuth";
import { LoginFormFields } from "../../types/auth.types";

export const LoginForm = () => {
  const { signIn, error, loading } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormFields>();

  const onSubmit = (data: LoginFormFields) => {
    // 只传递email和password
    signIn(data.email, data.password);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label>Email</label>
        <input
          {...register('email' as keyof LoginFormFields, {
            required: 'Email is required',
            pattern: {
              value: /^\S+@\S+$/i,
              message: 'Invalid email format'
            }
          })}
          type="email"
        />
        {errors.email && <span>{errors.email.message}</span>}
      </div>

      <div className="form-group">
        <label>Password</label>
        <input
          type="password"
          {...register('password' as keyof LoginFormFields, {
            required: 'Password is required',
            minLength: {
              value: 6,
              message: 'Minimum 6 characters'
            }
          })}
        />
        {errors.password && <span>{errors.password.message}</span>}
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  );
};