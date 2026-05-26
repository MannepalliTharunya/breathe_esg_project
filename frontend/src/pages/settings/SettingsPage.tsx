import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMe, useChangePassword } from "@/hooks/useAuth";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authService } from "@/services/api/auth.service";
import { toast } from "@/store/uiStore";
import { AUTH_KEYS } from "@/hooks/useAuth";

const profileSchema = z.object({
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  job_title: z.string().optional(),
  phone: z.string().optional(),
  timezone: z.string(),
});

const passwordSchema = z
  .object({
    current_password: z.string().min(1),
    new_password: z.string().min(10),
    new_password_confirm: z.string(),
  })
  .refine((d) => d.new_password === d.new_password_confirm, {
    message: "Passwords do not match",
    path: ["new_password_confirm"],
  });

type ProfileForm = z.infer<typeof profileSchema>;
type PasswordForm = z.infer<typeof passwordSchema>;

export function SettingsPage() {
  const { data: user } = useMe();
  const qc = useQueryClient();
  const changePassword = useChangePassword();

  const profileForm = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    values: user ? {
      first_name: user.first_name,
      last_name: user.last_name,
      job_title: user.job_title,
      phone: user.phone,
      timezone: user.timezone,
    } : undefined,
  });

  const passwordForm = useForm<PasswordForm>({ resolver: zodResolver(passwordSchema) });

  const updateProfile = useMutation({
    mutationFn: (data: ProfileForm) => authService.updateMe(data),
    onSuccess: (updated) => {
      qc.setQueryData(AUTH_KEYS.me, updated);
      toast.success("Profile updated");
    },
  });

  return (
    <div className="max-w-2xl space-y-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      {/* Profile */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Profile</h2>
        <form onSubmit={profileForm.handleSubmit((d) => updateProfile.mutate(d))} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">First name</label>
              <input type="text" className="input" {...profileForm.register("first_name")} />
            </div>
            <div>
              <label className="label">Last name</label>
              <input type="text" className="input" {...profileForm.register("last_name")} />
            </div>
          </div>
          <div>
            <label className="label">Job title</label>
            <input type="text" className="input" {...profileForm.register("job_title")} />
          </div>
          <div>
            <label className="label">Phone</label>
            <input type="tel" className="input" {...profileForm.register("phone")} />
          </div>
          <button type="submit" className="btn-primary" disabled={updateProfile.isPending}>
            {updateProfile.isPending ? "Saving..." : "Save changes"}
          </button>
        </form>
      </div>

      {/* Password */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Change password</h2>
        <form
          onSubmit={passwordForm.handleSubmit((d) =>
            changePassword.mutate({
              currentPassword: d.current_password,
              newPassword: d.new_password,
              newPasswordConfirm: d.new_password_confirm,
            }, { onSuccess: () => passwordForm.reset() })
          )}
          className="space-y-4"
        >
          <div>
            <label className="label">Current password</label>
            <input type="password" className="input" {...passwordForm.register("current_password")} />
          </div>
          <div>
            <label className="label">New password</label>
            <input type="password" className="input" {...passwordForm.register("new_password")} />
            {passwordForm.formState.errors.new_password && (
              <p className="mt-1 text-xs text-red-600">{passwordForm.formState.errors.new_password.message}</p>
            )}
          </div>
          <div>
            <label className="label">Confirm new password</label>
            <input type="password" className="input" {...passwordForm.register("new_password_confirm")} />
            {passwordForm.formState.errors.new_password_confirm && (
              <p className="mt-1 text-xs text-red-600">{passwordForm.formState.errors.new_password_confirm.message}</p>
            )}
          </div>
          <button type="submit" className="btn-primary" disabled={changePassword.isPending}>
            {changePassword.isPending ? "Updating..." : "Update password"}
          </button>
        </form>
      </div>
    </div>
  );
}
