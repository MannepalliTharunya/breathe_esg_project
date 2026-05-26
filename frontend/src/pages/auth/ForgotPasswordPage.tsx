import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { authService } from "@/services/api/auth.service";

const schema = z.object({ email: z.string().email("Enter a valid email address") });
type FormData = z.infer<typeof schema>;

export function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const mutation = useMutation({
    mutationFn: (data: FormData) => authService.requestPasswordReset(data.email),
    onSuccess: () => setSubmitted(true),
  });

  if (submitted) {
    return (
      <div className="text-center">
        <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
          <span className="text-green-600 text-xl">✓</span>
        </div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Check your email</h2>
        <p className="text-sm text-gray-500 mb-6">
          If that email exists, we've sent a password reset link.
        </p>
        <Link to="/auth/login" className="btn-secondary">Back to sign in</Link>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Reset your password</h2>
      <p className="text-sm text-gray-500 mb-6">
        Enter your email and we'll send you a reset link.
      </p>

      <form onSubmit={handleSubmit((data) => mutation.mutate(data))} noValidate>
        <div>
          <label htmlFor="email" className="label">Email address</label>
          <input id="email" type="email" className="input" {...register("email")} />
          {errors.email && (
            <p className="mt-1 text-xs text-red-600" role="alert">{errors.email.message}</p>
          )}
        </div>

        <button type="submit" disabled={mutation.isPending} className="btn-primary w-full mt-6">
          {mutation.isPending ? "Sending..." : "Send reset link"}
        </button>
      </form>

      <p className="text-center text-sm text-gray-500 mt-6">
        <Link to="/auth/login" className="text-brand-600 hover:underline">Back to sign in</Link>
      </p>
    </div>
  );
}
