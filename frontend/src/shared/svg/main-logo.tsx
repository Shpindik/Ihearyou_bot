import { ComponentPropsWithoutRef, FC } from 'react';

const MainIcon: FC<ComponentPropsWithoutRef<'svg'>> = ({ ...props }) => {
  return (
    <svg
      width="60"
      height="60"
      viewBox="0 0 60 60"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <rect
        x="10"
        y="10"
        width="40"
        height="40"
        fill="url(#pattern0_122_151)"
      />
      <defs>
        <pattern
          id="pattern0_122_151"
          patternContentUnits="objectBoundingBox"
          width="1"
          height="1"
        >
          <use transform="translate(-1.825 -0.000923802) scale(0.00235729)" />
        </pattern>
        <image
          id="image0_122_151"
          width="1962"
          height="425"
          preserveAspectRatio="none"
        />
      </defs>
    </svg>
  );
};

export default MainIcon;
