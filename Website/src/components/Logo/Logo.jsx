export default function Logo({ size = 28 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M12 16v-2a4 4 0 0 1 8 0v2"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
      <rect x="6" y="16" width="20" height="11" rx="3" fill="currentColor" />
    </svg>
  )
}
