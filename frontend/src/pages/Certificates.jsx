import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client.js";
import { Alert, Button, Card, Spinner } from "../components/ui.jsx";
import { useLang } from "../i18n/index.jsx";

export default function Certificates() {
  const { t } = useLang();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const raw = await api.get("/api/certificates/");
        const certificates = raw.results ?? raw;

        // Названия курсов подтягиваем отдельно: в сертификате лежит только id.
        const withTitles = await Promise.all(
          certificates.map(async (cert) => {
            try {
              const course = await api.get(`/api/courses/${cert.course}/`);
              return { ...cert, courseTitle: course.title };
            } catch {
              return { ...cert, courseTitle: `#${cert.course}` };
            }
          })
        );

        setItems(withTitles);
      } catch (e) {
        setError(e.text || t("common.error"));
      } finally {
        setLoading(false);
      }
    }

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return <Spinner text={t("common.loading")} />;

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="mb-6 text-3xl font-bold text-ink">{t("student.certificates")}</h1>

      {error && <Alert>{error}</Alert>}

      {!error && items.length === 0 && (
        <Card className="space-y-4 p-8 text-center">
          <p className="text-slate-600">{t("student.noCertificates")}</p>
          <Link to="/my-courses">
            <Button variant="outline">{t("student.myCourses")}</Button>
          </Link>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {items.map((cert) => (
          <Card key={cert.id} className="space-y-3 p-5">
            <div className="text-3xl">🎓</div>
            <h2 className="font-semibold text-ink">{cert.courseTitle}</h2>
            <p className="text-sm text-slate-500">
              {t("student.issuedAt")}: {new Date(cert.issued_at).toLocaleDateString()}
            </p>
            {cert.pdf_file && (
              <a href={cert.pdf_file} target="_blank" rel="noreferrer">
                <Button variant="outline" className="w-full">
                  {t("student.download")}
                </Button>
              </a>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
