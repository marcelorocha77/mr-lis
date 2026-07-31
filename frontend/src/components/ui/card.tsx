import * as React from "react";
import { cn } from "@/lib/utils";

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => (
  <div className={cn("rounded-lg border border-slate-200 bg-white shadow-sm", className)} {...props} />
);

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => (
  <div className={cn("border-b border-slate-100 px-5 py-4", className)} {...props} />
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className, ...props }) => (
  <h3 className={cn("text-lg font-semibold text-slate-800", className)} {...props} />
);

export const CardBody: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => (
  <div className={cn("px-5 py-4", className)} {...props} />
);
