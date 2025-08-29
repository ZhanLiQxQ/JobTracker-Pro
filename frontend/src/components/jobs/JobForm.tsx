import { useForm } from 'react-hook-form';
import {JobFormValues} from "../../types/job.types";

interface Props {
  onSubmit: (data: JobFormValues) => Promise<boolean>;
}

export const JobForm = ({ onSubmit }: Props) => {
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<JobFormValues>();

  const handleFormSubmit = async (data: JobFormValues) => {
    const success = await onSubmit(data);
    if (success) reset();
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-3">
      <div>
        <label className="block font-medium">职位名称*</label>
        <input
          {...register('title' as keyof JobFormValues, { required: true })}
          className="w-full p-2 border rounded"
        />
      </div>

      <div>
        <label className="block font-medium">公司名称*</label>
        <input
          {...register('company' as keyof JobFormValues, { required: true })}
          className="w-full p-2 border rounded"
        />
      </div>

      <div>
        <label className="block font-medium">职位描述</label>
        <textarea
          {...register('description' as keyof JobFormValues)}
          rows={3}
          className="w-full p-2 border rounded"
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {isSubmitting ? '提交中...' : '添加职位'}
      </button>
    </form>
  );
};