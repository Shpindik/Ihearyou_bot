import { ComponentPropsWithoutRef, FC } from 'react';

const PlusIcon: FC<ComponentPropsWithoutRef<'svg'>> = ({ ...props }) => {
  return (
    <svg
      width="25"
      height="24"
      viewBox="0 0 25 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M3.5 12H21.5M12.5 21V3"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M3.5 12H21.5M12.5 21V3"
        stroke="currentColor"
        strokeOpacity="0.2"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default PlusIcon;
