import { cn } from "@/lib/cn";

const colors: Record<string, string> = {
  gray: "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
  indigo: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300",
  green: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  yellow: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  red: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

interface Props {
  color?: keyof typeof colors;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export function Badge({ color = "gray", className, children, onClick }: Props) {
  const Tag = onClick ? "button" : "span";
  return (
    <Tag
      onClick={onClick}
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        onClick && "cursor-pointer hover:opacity-80",
        colors[color],
        className,
      )}
    >
      {children}
    </Tag>
  );
}
