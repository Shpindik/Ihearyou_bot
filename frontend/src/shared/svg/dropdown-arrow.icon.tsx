import { ComponentPropsWithoutRef, FC } from 'react';

const DropdownArrowIcon: FC<ComponentPropsWithoutRef<'svg'>> = ({
  ...props
}) => {
  return (
    <svg
      width="19"
      height="11"
      viewBox="0 0 19 11"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M18 1L11.0025 9.2677C10.1761 10.2441 8.82386 10.2441 7.99748 9.2677L1 1"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeMiterlimit="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default DropdownArrowIcon;
