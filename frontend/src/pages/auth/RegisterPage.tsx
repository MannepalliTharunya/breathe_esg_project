import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { useRegister } from "@/hooks/useAuth";
import { getApiErrorMessage } from "@/utils/apiError";

const schema = z
  .object({
    email: z.string().email("Enter a valid email address"),
    first_name: z.string().min(1, "First name is required"),
    last_name: z.string().min(1, "Last name is required"),
    password: z.string().min(10, "Password must be at least 10 characters"),
    password_confirm: z.string(),
    job_title: z.string().optional(),
  })
  .refine((d) => d.password === d.password_confirm, {
    message: "Passwords do not match",
    path: ["password_confirm"],
  });

type FormData = z.infer<typeof schema>;

export function RegisterPage() {
  const register_ = useRegister();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Create your account</h2>

      <form onSubmit={handleSubmit((data) => register_.mutate(data))} noValidate>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="first_name" className="label">First name</label>
              <input id="first_name" type="text" className="input" {...register("first_name")} />
              {errors.first_name && (
                <p className="mt-1 text-xs text-red-600" role="alert">{errors.first_name.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="last_name" className="label">Last name</label>
              <input id="last_name" type="text" className="input" {...register("last_name")} />
              {errors.last_name && (
                <p className="mt-1 text-xs text-red-600" role="alert">{errors.last_name.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="email" className="label">Email address</label>
            <input id="email" type="email" autoComplete="email" className="input" {...register("email")} />
            {errors.email && (
              <p className="mt-1 text-xs text-red-600" role="alert">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="job_title" className="label">Job title <span className="text-gray-400">(optional)</span></label>
            <input id="job_title" type="text" className="input" {...register("job_title")} />
          </div>

          <div>
            <label htmlFor="password" className="label">Password</label>
            <input id="password" type="password" autoComplete="new-password" className="input" {...register("password")} />
            {errors.password && (
              <p className="mt-1 text-xs text-red-600" role="alert">{errors.password.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="password_confirm" className="label">Confirm password</label>
            <input id="password_confirm" type="password" autoComplete="new-password" className="input" {...register("password_confirm")} />
            {errors.password_confirm && (
              <p className="mt-1 text-xs text-red-600" role="alert">{errors.password_confirm.message}</p>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={register_.isPending}
          className="btn-primary w-full mt-6"
        >
          {register_.isPending ? "Creating account..." : "Create account"}
        </button>

        {register_.error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg" role="alert">
            <p className="text-sm text-red-700">
              {getApiErrorMessage(register_.error, "Registration failed. Please try again.")}
            </p>
          </div>
        )}
      </form>

      <p className="text-center text-sm text-gray-500 mt-6">
        Already have an account?{" "}
        <Link to="/auth/login" className="text-brand-600 font-medium hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
