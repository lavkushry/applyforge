import { ProfileForm } from "@/components/forms/profile-form";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";

export default function ProfilePage() {
  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Candidate Brain"
          title="Canonical profile editor"
          description="Keep a single trustworthy source of truth that ApplyForge can score against and tailor from."
        />
        <ProfileForm />
      </section>
    </ProtectedPage>
  );
}
