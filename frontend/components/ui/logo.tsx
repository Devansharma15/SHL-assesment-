export function SHLLogo({ className = "h-6 w-auto" }: { className?: string }) {
  return (
    <svg 
      viewBox="0 0 100 40" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg" 
      className={className}
    >
      <g stroke="#424242" strokeWidth="6.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M 24 13 C 24 4, 8 4, 8 14 C 8 21, 24 19, 24 26 C 24 36, 8 36, 8 27" />
        <path d="M 38 8 L 38 32" />
        <path d="M 38 20 L 52 20" />
        <path d="M 52 8 L 52 32" />
        <path d="M 66 8 L 66 32 L 80 32" />
      </g>
      <circle cx="92" cy="32" r="5" fill="#8CC63F" />
    </svg>
  );
}
