// Мелкие кирпичики интерфейса, чтобы не повторять одни и те же классы Tailwind.

export function Button({ variant = "primary", className = "", ...props }) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-brand-600 text-white hover:bg-brand-700",
    outline: "border border-brand-600 text-brand-600 hover:bg-brand-50",
    ghost: "text-slate-600 hover:bg-slate-100",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
}

export function Field({ label, error, children }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-slate-700">{label}</span>
      {children}
      {error && <span className="mt-1 block text-sm text-red-600">{error}</span>}
    </label>
  );
}

const inputClass =
  "w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100";

export function Input(props) {
  return <input className={inputClass} {...props} />;
}

export function Textarea(props) {
  return <textarea className={`${inputClass} min-h-32 resize-y`} {...props} />;
}

export function Select(props) {
  return <select className={`${inputClass} bg-white`} {...props} />;
}

export function Card({ className = "", ...props }) {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}
      {...props}
    />
  );
}

export function Spinner({ text }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-slate-500">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600" />
      {text}
    </div>
  );
}

export function Alert({ kind = "error", children }) {
  const kinds = {
    error: "bg-red-50 text-red-700 border-red-200",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
    info: "bg-brand-50 text-brand-700 border-brand-100",
  };
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm whitespace-pre-line ${kinds[kind]}`}>
      {children}
    </div>
  );
}

export function Badge({ children, tone = "slate" }) {
  const tones = {
    slate: "bg-slate-100 text-slate-600",
    amber: "bg-amber-100 text-amber-700",
    green: "bg-emerald-100 text-emerald-700",
  };
  return (
    <span className={`rounded-md px-2 py-0.5 text-xs font-medium ${tones[tone]}`}>{children}</span>
  );
}

// Звёзды рейтинга. Если передан onChange, звёзды становятся кликабельными.
export function Stars({ value = 0, onChange }) {
  const rounded = Math.round(value);
  return (
    <span className="inline-flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          role={onChange ? "button" : undefined}
          onClick={onChange ? () => onChange(star) : undefined}
          className={`${star <= rounded ? "text-amber-400" : "text-slate-300"} ${
            onChange ? "cursor-pointer text-2xl" : "text-base"
          }`}
        >
          ★
        </span>
      ))}
    </span>
  );
}

export function Price({ value, currency, freeLabel }) {
  const number = Number(value);
  if (!number) return <span className="font-semibold text-emerald-600">{freeLabel}</span>;
  return (
    <span className="font-semibold text-ink">
      {number.toLocaleString()} {currency}
    </span>
  );
}
