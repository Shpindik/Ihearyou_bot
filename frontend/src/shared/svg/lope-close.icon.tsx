import { ComponentPropsWithoutRef, FC } from 'react';

const LopeCloseIcon: FC<ComponentPropsWithoutRef<'svg'>> = ({ ...props }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="40"
      height="40"
      viewBox="0 0 40 40"
      fill="none"
      {...props}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M31.556 19.113V19.113C31.556 25.9863 25.9844 31.558 19.111 31.558V31.558C12.2377 31.558 6.66602 25.9863 6.66602 19.113V19.113C6.66602 12.2396 12.2377 6.66797 19.111 6.66797V6.66797C25.9844 6.66797 31.556 12.2396 31.556 19.113Z"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M33.3327 33.3346L27.916 27.918"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M23.0259 15.1992L15.1992 23.0259"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M23.0259 23.0259L15.1992 15.1992"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default LopeCloseIcon;
