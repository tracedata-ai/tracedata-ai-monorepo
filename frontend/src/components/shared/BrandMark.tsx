import Image from "next/image";

type BrandMarkProps = {
  size?: number;
  className?: string;
  priority?: boolean;
};

export function BrandMark({
  size = 28,
  className,
  priority = false,
}: BrandMarkProps) {
  return (
    <Image
      src="/logo.png"
      alt="TraceData"
      width={size}
      height={size}
      priority={priority}
      className={className}
    />
  );
}
