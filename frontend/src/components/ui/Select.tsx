import type { SelectHTMLAttributes } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
  error?: string;
}

export default function Select({
  label,
  options,
  error,
  id,
  className = "",
  ...rest
}: SelectProps) {
  return (
    <div className="field">
      {label && <label htmlFor={id} className="form-label">{label}</label>}
      <select
        id={id}
        className={`input ${error ? "input-error" : ""} ${className}`.trim()}
        {...rest}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}