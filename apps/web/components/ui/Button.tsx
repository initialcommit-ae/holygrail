"use client";

import { type ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils/cn";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "rounded-full font-mono transition-all inline-flex items-center justify-center disabled:opacity-50 disabled:pointer-events-none",
          variant === "primary" &&
            "bg-black text-white hover:bg-slate-800 text-[15px]",
          variant === "secondary" &&
            "bg-[#f2f4f7] text-slate-900 hover:bg-slate-200 text-[15px]",
          variant === "ghost" && "bg-transparent text-slate-600 hover:bg-slate-100",
          size === "sm" && "px-4 py-2 text-[13px]",
          size === "md" && "px-6 py-2.5 text-[15px]",
          size === "lg" && "px-10 py-4 text-[15px]",
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";

export { Button };
