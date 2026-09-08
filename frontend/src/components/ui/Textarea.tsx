import type { TextareaHTMLAttributes } from "react";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export default function Textarea({
  label,
  error,
  id,
  className = "",
  ...rest
}: TextareaProps) {
  return (
    <div className="field">
      {label && <label htmlFor={id} className="form-label">{label}</label>}
      <textarea
        id={id}
        className={`input ${error ? "input-error" : ""} ${className}`.trim()}
        {...rest}
      />
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}