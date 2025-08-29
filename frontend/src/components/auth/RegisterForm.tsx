import { useForm } from 'react-hook-form';
import { useAuth } from "../../hooks/useAuth";
import { RegisterFormFields } from "../../types/auth.types";

export const RegisterForm = () => {
  const { signUp, error, loading } = useAuth();
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm<RegisterFormFields>();

  const password = watch('password');

  const onSubmit = (data: RegisterFormFields) => {
    // 只传递email和password
    signUp(data.email, data.password);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label>Email</label>
        <input
          {...register('email', {
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
          {...register('password', {
            required: 'Password is required',
            minLength: {
              value: 6,
              message: 'Minimum 6 characters'
            }
          })}
        />
        {errors.password && <span>{errors.password.message}</span>}
      </div>

      <div className="form-group">
        <label>Confirm Password</label>
        <input
          type="password"
          {...register('confirmPassword', {
            validate: value =>
              value === password || 'Passwords do not match'
          })}
        />
        {errors.confirmPassword && <span>{errors.confirmPassword.message}</span>}
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
};