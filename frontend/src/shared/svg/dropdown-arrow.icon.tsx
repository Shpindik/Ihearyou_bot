import {ComponentPropsWithoutRef, FC} from 'react';

const DropdownArrowIcon: FC<ComponentPropsWithoutRef<'svg'>> = ({
  ...props
}) => {
  return (
    <svg
      width="21"
      height="12"
      viewBox="0 0 21 12"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M19.5 1L12.0909 10.1863C11.2159 11.2712 9.78409 11.2712 8.90909 10.1863L1.5 1"
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
