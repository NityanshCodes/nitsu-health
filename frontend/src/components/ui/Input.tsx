import type { InputHTMLAttributes } from "react";
import { forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, hint, id, className = "", ...rest },
  ref,
) {
  return (
    <div className="field">
      {label && <label htmlFor={id} className="form-label">{label}</label>}
      <input
        ref={ref}
        id={id}
        className={`input ${error ? "input-error" : ""} ${className}`.trim()}
        {...rest}
      />
      {hint && !error && <p className="form-hint">{hint}</p>}
      {error && <p className="form-error">{error}</p>}
    </div>
  );
});

export default Input;