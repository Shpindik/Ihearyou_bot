import { ComponentPropsWithoutRef, FC } from 'react';


type InfoLabelProps = {
  state?: "pressed" | "inactive";
  children: React.ReactNode;
} & ComponentPropsWithoutRef<"span">;


const InfoLabel: FC<InfoLabelProps> = ({
  state = "inactive",
  children,
  className,
  ...props
}) => {
  return (
    <span
      className={cn(
        "inline-block h-14 px-8 py-6 rounded-full text-white text-lg font-medium select-none items-center justify-center",
        state === "pressed" && "bg-purple-primary",
        state === "inactive" && "bg-purple-secondary",
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
export default InfoLabel;