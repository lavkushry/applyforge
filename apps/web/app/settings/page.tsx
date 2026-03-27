import { SettingsForm } from "@/components/forms/settings-form";
import { PageHeader } from "@/components/ui/page-header";
import { ProtectedPage } from "@/components/ui/protected-page";

export default function SettingsPage() {
  return (
    <ProtectedPage>
      <section className="space-y-6">
        <PageHeader
          eyebrow="Settings"
          title="Automation and search defaults"
          description="Tune how aggressive ApplyForge should be, and keep risky answers behind explicit approval gates."
        />
        <SettingsForm />
      </section>
    </ProtectedPage>
  );
}
