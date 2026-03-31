"use client";
import { cn } from "@/lib/cn";
import { type InputHTMLAttributes, forwardRef } from "react";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, Props>(({ label, error, className, id, ...props }, ref) => {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        className={cn(
          "block w-full rounded-lg border px-3 py-2 text-sm shadow-sm transition-colors",
          "border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500",
          "dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:focus:border-indigo-400",
          error && "border-red-500 focus:border-red-500 focus:ring-red-500",
          className,
        )}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
});
Input.displayName = "Input";
