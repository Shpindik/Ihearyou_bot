import { ComponentPropsWithoutRef, FC } from 'react';

const ExitIcon: FC<ComponentPropsWithoutRef<'svg'>> = ({ ...props }) => {
  return (
    <svg
      width="36"
      height="36"
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M22.5 12.375V9.5625C22.5 8.81658 22.2037 8.10121 21.6762 7.57376C21.1488 7.04632 20.4334 6.75 19.6875 6.75H6.1875C5.44158 6.75 4.72621 7.04632 4.19876 7.57376C3.67132 8.10121 3.375 8.81658 3.375 9.5625V26.4375C3.375 27.1834 3.67132 27.8988 4.19876 28.4262C4.72621 28.9537 5.44158 29.25 6.1875 29.25H19.6875C20.4334 29.25 21.1488 28.9537 21.6762 28.4262C22.2037 27.8988 22.5 27.1834 22.5 26.4375V23.625M27 12.375L32.625 18M32.625 18L27 23.625M32.625 18H13.4297"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default ExitIcon;
